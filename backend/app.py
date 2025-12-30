#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py - Flask application for Weekly Report and OKR Assistant
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from generator import generate_weekly_report, generate_okr, validate_weekly_report, validate_okr
from parser import parse_and_categorize, get_current_week_range, format_date
from config import Config
import database as db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'llm_configured': Config.is_llm_configured(),
        'max_input_chars': Config.MAX_INPUT_CHARS
    })


@app.route('/api/week-range', methods=['GET'])
def get_week_range():
    """Get current week's Monday-Friday date range"""
    monday, friday = get_current_week_range()
    return jsonify({
        'monday': format_date(monday),
        'friday': format_date(friday)
    })


@app.route('/api/parse', methods=['POST'])
def parse_daily_report():
    """
    Parse daily report content without generating weekly report.
    Useful for preview/debugging.
    """
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({
            'success': False,
            'error': '缺少 content 字段'
        }), 400
    
    content = data['content']
    
    if len(content) > Config.MAX_INPUT_CHARS:
        return jsonify({
            'success': False,
            'error': f'输入超过最大长度限制 ({Config.MAX_INPUT_CHARS} 字符)'
        }), 400
    
    try:
        parsed = parse_and_categorize(content)
        return jsonify({
            'success': True,
            'data': parsed
        })
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate/weekly-report', methods=['POST'])
def api_generate_weekly_report():
    """
    Generate weekly report from daily report content.
    
    Request body:
    {
        "content": "daily report text...",
        "use_mock": false,  // optional, default false
        "start_date": "2025-12-08",  // optional, date range start
        "end_date": "2025-12-12"  // optional, date range end
    }
    """
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({
            'success': False,
            'error': '缺少 content 字段'
        }), 400
    
    content = data['content']
    use_mock = data.get('use_mock', False)
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    # If LLM not configured, force mock mode
    if not Config.is_llm_configured():
        use_mock = True
        logger.info("LLM not configured, using mock mode")
    
    result = generate_weekly_report(
        content, 
        use_mock=use_mock,
        start_date=start_date,
        end_date=end_date
    )
    
    if result['success']:
        # Validate the generated report
        validation = validate_weekly_report(result['report'])
        result['validation'] = validation
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/api/generate/okr', methods=['POST'])
def api_generate_okr():
    """
    Generate OKR from historical materials.
    
    Request body:
    {
        "content": "historical materials...",
        "next_quarter": "2026第一季度",  // optional
        "use_mock": false  // optional, default false
    }
    """
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({
            'success': False,
            'error': '缺少 content 字段'
        }), 400
    
    content = data['content']
    next_quarter = data.get('next_quarter', '2026第一季度')
    use_mock = data.get('use_mock', False)
    
    # If LLM not configured, force mock mode
    if not Config.is_llm_configured():
        use_mock = True
        logger.info("LLM not configured, using mock mode")
    
    result = generate_okr(content, next_quarter=next_quarter, use_mock=use_mock)
    
    if result['success']:
        # Validate the generated OKR
        validation = validate_okr(result['okr'])
        result['validation'] = validation
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/api/validate/weekly-report', methods=['POST'])
def api_validate_weekly_report():
    """
    Validate a weekly report against structure requirements.
    
    Request body:
    {
        "report": "weekly report text..."
    }
    """
    data = request.get_json()
    if not data or 'report' not in data:
        return jsonify({
            'success': False,
            'error': '缺少 report 字段'
        }), 400
    
    validation = validate_weekly_report(data['report'])
    return jsonify({
        'success': True,
        'validation': validation
    })


@app.route('/api/validate/okr', methods=['POST'])
def api_validate_okr():
    """
    Validate OKR against structure requirements.
    
    Request body:
    {
        "okr": "OKR text..."
    }
    """
    data = request.get_json()
    if not data or 'okr' not in data:
        return jsonify({
            'success': False,
            'error': '缺少 okr 字段'
        }), 400
    
    validation = validate_okr(data['okr'])
    return jsonify({
        'success': True,
        'validation': validation
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


# ========================
# Daily Reports API
# ========================

@app.route('/api/daily-reports', methods=['POST'])
def save_daily_report():
    """
    Save or update a daily report.
    
    Request body:
    {
        "entry_date": "2025-01-20",
        "content": "Daily report content..."
    }
    """
    data = request.get_json()
    if not data or 'entry_date' not in data or 'content' not in data:
        return jsonify({
            'success': False,
            'error': '缺少 entry_date 或 content 字段'
        }), 400
    
    success = db.save_daily_report(data['entry_date'], data['content'])
    
    if success:
        return jsonify({'success': True, 'message': '日报保存成功'})
    else:
        return jsonify({'success': False, 'error': '日报保存失败'}), 500


@app.route('/api/daily-reports/<entry_date>', methods=['GET'])
def get_daily_report(entry_date):
    """
    Get a daily report by date.
    
    URL parameter: entry_date (YYYY-MM-DD format)
    """
    report = db.get_daily_report(entry_date)
    
    if report:
        return jsonify({'success': True, 'data': report})
    else:
        return jsonify({'success': True, 'data': None})


@app.route('/api/daily-reports/range', methods=['GET'])
def get_daily_reports_by_range():
    """
    Get daily reports within a date range.
    
    Query parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({
            'success': False,
            'error': '缺少 start_date 或 end_date 参数'
        }), 400
    
    reports = db.get_daily_reports_by_range(start_date, end_date)
    return jsonify({'success': True, 'data': reports})


@app.route('/api/daily-reports/dates', methods=['GET'])
def get_daily_report_dates():
    """
    Get all dates that have daily reports.
    """
    dates = db.get_all_daily_report_dates()
    return jsonify({'success': True, 'data': dates})


@app.route('/api/daily-reports/<entry_date>', methods=['DELETE'])
def delete_daily_report(entry_date):
    """
    Delete a daily report by date.
    
    URL parameter: entry_date (YYYY-MM-DD format)
    """
    success = db.delete_daily_report(entry_date)
    
    if success:
        return jsonify({'success': True, 'message': '日报删除成功'})
    else:
        return jsonify({'success': False, 'error': '日报不存在或删除失败'}), 404


# ========================
# Weekly Reports API
# ========================

@app.route('/api/weekly-reports', methods=['POST'])
def save_weekly_report():
    """
    Save or update a weekly report.
    
    Request body:
    {
        "start_date": "2025-01-20",
        "end_date": "2025-01-24",
        "content": "Weekly report content..."
    }
    """
    data = request.get_json()
    if not data or 'start_date' not in data or 'end_date' not in data or 'content' not in data:
        return jsonify({
            'success': False,
            'error': '缺少 start_date、end_date 或 content 字段'
        }), 400
    
    success = db.save_weekly_report(data['start_date'], data['end_date'], data['content'])
    
    if success:
        return jsonify({'success': True, 'message': '周报保存成功'})
    else:
        return jsonify({'success': False, 'error': '周报保存失败'}), 500


@app.route('/api/weekly-reports/query', methods=['GET'])
def query_weekly_report():
    """
    Get a weekly report by start and end date.
    
    Query parameters:
    - start_date: Week start date (YYYY-MM-DD)
    - end_date: Week end date (YYYY-MM-DD)
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({
            'success': False,
            'error': '缺少 start_date 或 end_date 参数'
        }), 400
    
    report = db.get_weekly_report(start_date, end_date)
    
    if report:
        return jsonify({'success': True, 'data': report})
    else:
        return jsonify({'success': True, 'data': None})


@app.route('/api/weekly-reports/latest', methods=['GET'])
def get_latest_weekly_report():
    """
    Get the most recent weekly report.
    """
    report = db.get_latest_weekly_report()
    
    if report:
        return jsonify({'success': True, 'data': report})
    else:
        return jsonify({'success': True, 'data': None})


@app.route('/api/weekly-reports', methods=['GET'])
def get_all_weekly_reports():
    """
    Get all weekly reports ordered by end_date descending.
    """
    reports = db.get_all_weekly_reports()
    return jsonify({'success': True, 'data': reports})


@app.route('/api/weekly-reports', methods=['DELETE'])
def delete_weekly_report():
    """
    Delete a weekly report by start and end date.
    
    Query parameters:
    - start_date: Week start date (YYYY-MM-DD)
    - end_date: Week end date (YYYY-MM-DD)
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({
            'success': False,
            'error': '缺少 start_date 或 end_date 参数'
        }), 400
    
    success = db.delete_weekly_report(start_date, end_date)
    
    if success:
        return jsonify({'success': True, 'message': '周报删除成功'})
    else:
        return jsonify({'success': False, 'error': '周报不存在或删除失败'}), 404


# ========================
# OKR Reports API
# ========================

@app.route('/api/okr-reports', methods=['POST'])
def save_okr_report():
    """
    Save or update an OKR report.
    
    Request body:
    {
        "creation_date": "2025-01-20",
        "content": "OKR content..."
    }
    """
    data = request.get_json()
    if not data or 'creation_date' not in data or 'content' not in data:
        return jsonify({
            'success': False,
            'error': '缺少 creation_date 或 content 字段'
        }), 400
    
    success = db.save_okr_report(data['creation_date'], data['content'])
    
    if success:
        return jsonify({'success': True, 'message': 'OKR保存成功'})
    else:
        return jsonify({'success': False, 'error': 'OKR保存失败'}), 500


@app.route('/api/okr-reports/<creation_date>', methods=['GET'])
def get_okr_report(creation_date):
    """
    Get an OKR report by creation date.
    
    URL parameter: creation_date (YYYY-MM-DD format)
    """
    report = db.get_okr_report(creation_date)
    
    if report:
        return jsonify({'success': True, 'data': report})
    else:
        return jsonify({'success': True, 'data': None})


@app.route('/api/okr-reports/latest', methods=['GET'])
def get_latest_okr_report():
    """
    Get the most recent OKR report.
    """
    report = db.get_latest_okr_report()
    
    if report:
        return jsonify({'success': True, 'data': report})
    else:
        return jsonify({'success': True, 'data': None})


@app.route('/api/okr-reports', methods=['GET'])
def get_all_okr_reports():
    """
    Get all OKR reports ordered by creation_date descending.
    """
    reports = db.get_all_okr_reports()
    return jsonify({'success': True, 'data': reports})


@app.route('/api/okr-reports/<creation_date>', methods=['DELETE'])
def delete_okr_report(creation_date):
    """
    Delete an OKR report by creation date.
    
    URL parameter: creation_date (YYYY-MM-DD format)
    """
    success = db.delete_okr_report(creation_date)
    
    if success:
        return jsonify({'success': True, 'message': 'OKR删除成功'})
    else:
        return jsonify({'success': False, 'error': 'OKR不存在或删除失败'}), 404


# ===================
# TODO Items API
# ===================

@app.route('/api/todo-items', methods=['GET'])
def get_todo_items():
    """
    Get all TODO items.
    """
    items = db.get_all_todo_items()
    return jsonify({'success': True, 'data': items})


@app.route('/api/todo-items', methods=['POST'])
def create_todo_item():
    """
    Create a new TODO item.
    
    Request body:
    {
        "content": "TODO item content"
    }
    """
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'success': False, 'error': '缺少 content 字段'}), 400
    
    content = data['content'].strip()
    if not content:
        return jsonify({'success': False, 'error': '内容不能为空'}), 400
    
    item = db.create_todo_item(content)
    
    if item:
        return jsonify({'success': True, 'data': item})
    else:
        return jsonify({'success': False, 'error': '创建失败'}), 500


@app.route('/api/todo-items/<int:item_id>', methods=['PUT'])
def update_todo_item(item_id):
    """
    Update a TODO item.
    
    Request body:
    {
        "content": "Updated content",  // optional
        "completed": true  // optional
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '缺少请求体'}), 400
    
    content = data.get('content')
    completed = data.get('completed')
    
    item = db.update_todo_item(item_id, content=content, completed=completed)
    
    if item:
        return jsonify({'success': True, 'data': item})
    else:
        return jsonify({'success': False, 'error': '更新失败或项目不存在'}), 404


@app.route('/api/todo-items/<int:item_id>', methods=['DELETE'])
def delete_todo_item(item_id):
    """
    Delete a TODO item.
    """
    success = db.delete_todo_item(item_id)
    
    if success:
        return jsonify({'success': True, 'message': 'TODO项删除成功'})
    else:
        return jsonify({'success': False, 'error': 'TODO项不存在或删除失败'}), 404


# ========================================
# Career Asset Management API (新增)
# ========================================

# --- Projects API ---

@app.route('/api/projects', methods=['GET'])
def get_all_projects():
    """
    Get all projects, optionally filtered by status.
    
    Query parameters:
    - status: 'active' or 'archived' (optional)
    """
    status = request.args.get('status')
    projects = db.get_all_projects(status=status)
    return jsonify({'success': True, 'data': projects})


@app.route('/api/projects/summary', methods=['GET'])
def get_projects_summary():
    """
    Get projects summary with work item counts.
    """
    summary = db.get_projects_summary()
    return jsonify({'success': True, 'data': summary})


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """
    Get a project by ID with all its work items.
    """
    project = db.get_project_with_work_items(project_id)
    if project:
        return jsonify({'success': True, 'data': project})
    else:
        return jsonify({'success': False, 'error': '项目不存在'}), 404


@app.route('/api/projects', methods=['POST'])
def create_project():
    """
    Create a new project.
    
    Request body:
    {
        "name": "Project Name",
        "description": "Optional description"
    }
    """
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'success': False, 'error': '缺少 name 字段'}), 400
    
    project = db.create_project(
        name=data['name'],
        description=data.get('description'),
        status=data.get('status', 'active')
    )
    
    if project:
        return jsonify({'success': True, 'data': project})
    else:
        return jsonify({'success': False, 'error': '项目创建失败'}), 500


@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """
    Update a project.
    
    Request body:
    {
        "name": "New name",  // optional
        "description": "New description",  // optional
        "status": "archived",  // optional
        "star_summary": "STAR summary text"  // optional
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '缺少请求体'}), 400
    
    project = db.update_project(project_id, **data)
    
    if project:
        return jsonify({'success': True, 'data': project})
    else:
        return jsonify({'success': False, 'error': '更新失败或项目不存在'}), 404


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """
    Delete a project and its work items.
    """
    success = db.delete_project(project_id)
    
    if success:
        return jsonify({'success': True, 'message': '项目删除成功'})
    else:
        return jsonify({'success': False, 'error': '项目不存在或删除失败'}), 404


@app.route('/api/projects/<int:project_id>/star', methods=['POST'])
def generate_project_star(project_id):
    """
    Generate STAR summary for a project.
    """
    from generator import generate_star_summary
    
    project = db.get_project_with_work_items(project_id)
    if not project:
        return jsonify({'success': False, 'error': '项目不存在'}), 404
    
    work_items = project.get('work_items', [])
    if not work_items:
        return jsonify({'success': False, 'error': '项目没有工作记录，无法生成 STAR 总结'}), 400
    
    use_mock = not Config.is_llm_configured()
    result = generate_star_summary(project['name'], work_items, use_mock=use_mock)
    
    if result['success']:
        # Save the STAR summary to project
        db.update_project(project_id, star_summary=result['summary'])
        return jsonify({
            'success': True,
            'summary': result['summary']
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', '生成失败')
        }), 500


@app.route('/api/projects/cleanup/null', methods=['POST'])
def cleanup_null_projects():
    """
    将所有名为 null 或空的项目的工作条目合并到"临时工作"项目。
    """
    result = db.merge_null_projects_to_temporary()
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/api/projects/similar', methods=['GET'])
def get_similar_projects():
    """
    获取相似项目分组，用于手动合并。
    """
    threshold = request.args.get('threshold', 0.6, type=float)
    groups = db.find_similar_project_groups(threshold)
    return jsonify({
        'success': True,
        'groups': groups
    })


@app.route('/api/projects/merge', methods=['POST'])
def merge_projects():
    """
    合并多个相似项目到目标项目。
    
    请求体:
    {
        "target_project_id": 1,
        "source_project_ids": [2, 3, 4]
    }
    """
    data = request.get_json()
    
    target_id = data.get('target_project_id')
    source_ids = data.get('source_project_ids', [])
    
    if not target_id:
        return jsonify({'success': False, 'error': '缺少目标项目ID'}), 400
    
    if not source_ids:
        return jsonify({'success': False, 'error': '缺少要合并的项目ID'}), 400
    
    result = db.merge_similar_projects(target_id, source_ids)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/api/projects/all', methods=['DELETE'])
def delete_all_projects():
    """
    删除所有项目、工作条目和技能数据。
    """
    result = db.delete_all_projects()
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500


# --- Work Items API ---

@app.route('/api/work-items', methods=['GET'])
def get_all_work_items():
    """
    Get all work items with project info.
    """
    work_items = db.get_all_work_items()
    return jsonify({'success': True, 'data': work_items})


@app.route('/api/work-items/range', methods=['GET'])
def get_work_items_by_range():
    """
    Get work items within a date range.
    
    Query parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'success': False, 'error': '缺少日期参数'}), 400
    
    items = db.get_work_items_by_date_range(start_date, end_date)
    return jsonify({'success': True, 'data': items})


@app.route('/api/work-items', methods=['POST'])
def create_work_item():
    """
    Create a work item manually.
    
    Request body:
    {
        "raw_log_date": "2025-12-30",
        "project_id": 1,  // optional
        "action": "What was done",
        "problem": "Problem encountered",  // optional
        "result_metric": "Quantified result",  // optional
        "skills_tags": "[\"Python\", \"Redis\"]"  // JSON string, optional
    }
    """
    data = request.get_json()
    if not data or 'raw_log_date' not in data:
        return jsonify({'success': False, 'error': '缺少 raw_log_date 字段'}), 400
    
    item = db.create_work_item(
        raw_log_date=data['raw_log_date'],
        project_id=data.get('project_id'),
        action=data.get('action'),
        problem=data.get('problem'),
        result_metric=data.get('result_metric'),
        skills_tags=data.get('skills_tags'),
        extraction_status='manual'
    )
    
    if item:
        return jsonify({'success': True, 'data': item})
    else:
        return jsonify({'success': False, 'error': '创建失败'}), 500


@app.route('/api/work-items/<int:item_id>', methods=['PUT'])
def update_work_item(item_id):
    """
    Update a work item.
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '缺少请求体'}), 400
    
    item = db.update_work_item(item_id, **data)
    
    if item:
        return jsonify({'success': True, 'data': item})
    else:
        return jsonify({'success': False, 'error': '更新失败'}), 404


@app.route('/api/work-items/<int:item_id>', methods=['DELETE'])
def delete_work_item(item_id):
    """
    Delete a work item.
    """
    success = db.delete_work_item(item_id)
    
    if success:
        return jsonify({'success': True, 'message': '工作项删除成功'})
    else:
        return jsonify({'success': False, 'error': '工作项不存在或删除失败'}), 404


# --- Extraction API ---

@app.route('/api/extract-work-items', methods=['POST'])
def extract_work_items_api():
    """
    Extract structured work items from daily log content using LLM.
    
    Request body:
    {
        "log_content": "Daily log text...",
        "log_date": "2025-12-30",
        "auto_save": false  // optional, whether to auto-save extracted items
    }
    """
    from generator import extract_work_items, find_best_matching_project
    
    data = request.get_json()
    if not data or 'log_content' not in data or 'log_date' not in data:
        return jsonify({'success': False, 'error': '缺少 log_content 或 log_date 字段'}), 400
    
    use_mock = not Config.is_llm_configured()
    result = extract_work_items(data['log_content'], data['log_date'], use_mock=use_mock)
    
    if result['success'] and data.get('auto_save'):
        # Get existing projects for similarity matching
        existing_projects = db.get_all_projects()
        
        # Auto-save extracted items to database
        saved_items = []
        for item in result.get('work_items', []):
            # Create or find project with similarity matching
            project_id = None
            if item.get('project') and item.get('project') != '日常工作':
                # First, try to find a similar existing project
                matching_project = find_best_matching_project(
                    item['project'], 
                    existing_projects, 
                    threshold=0.6
                )
                
                if matching_project:
                    project_id = matching_project['id']
                    # Update the item's project name to match the existing one
                    item['project'] = matching_project['name']
                else:
                    # Create new project
                    project = db.create_project(name=item['project'])
                    if project:
                        project_id = project['id']
                        # Add to existing_projects for future matching in this batch
                        existing_projects.append(project)
            
            # Save work item
            skills_json = None
            if item.get('skills'):
                import json
                skills_json = json.dumps(item['skills'], ensure_ascii=False)
                # Update skills table
                for skill in item['skills']:
                    if skill and skill not in ['null', 'None', '待补充']:
                        db.upsert_skill(skill)
            
            saved = db.create_work_item(
                raw_log_date=data['log_date'],
                project_id=project_id,
                action=item.get('action'),
                problem=item.get('problem'),
                result_metric=item.get('result_metric'),
                skills_tags=skills_json,
                extraction_status='extracted'
            )
            if saved:
                saved_items.append(saved)
        
        result['saved_items'] = saved_items
    
    return jsonify(result)


# --- Skills API ---

@app.route('/api/skills', methods=['GET'])
def get_all_skills():
    """
    Get all skills sorted by count.
    """
    skills = db.get_all_skills()
    return jsonify({'success': True, 'data': skills})


@app.route('/api/skills/stats', methods=['GET'])
def get_skills_stats():
    """
    Get skills statistics for visualization (radar chart, etc.)
    """
    stats = db.get_skills_stats()
    return jsonify({'success': True, 'data': stats})


@app.route('/api/skills/recategorize', methods=['POST'])
def recategorize_skills():
    """
    重新推断所有技能的分类。
    """
    result = db.recategorize_all_skills()
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/api/skills/recategorize-llm', methods=['POST'])
def recategorize_skills_with_llm():
    """
    使用 LLM 智能识别并更新所有技能的分类。
    """
    from generator import categorize_skills_with_llm
    
    # 获取所有技能
    skills = db.get_all_skills_for_categorization()
    
    if not skills:
        return jsonify({
            'success': True,
            'message': '没有需要分类的技能',
            'updated_count': 0
        })
    
    # 使用 LLM 进行分类
    use_mock = not Config.is_llm_configured()
    result = categorize_skills_with_llm(skills, use_mock=use_mock)
    
    if not result['success']:
        return jsonify(result), 500
    
    # 更新数据库中的分类
    categorized_skills = result.get('categorized_skills', [])
    update_result = db.update_skill_categories(categorized_skills)
    
    if update_result['success']:
        return jsonify({
            'success': True,
            'message': f"已使用 AI 更新 {update_result['updated_count']} 个技能的分类",
            'updated_count': update_result['updated_count'],
            'details': categorized_skills
        })
    else:
        return jsonify(update_result), 500


@app.route('/api/skills/<skill_name>/work-items', methods=['GET'])
def get_work_items_by_skill(skill_name):
    """
    获取包含指定技能的所有工作条目。
    """
    work_items = db.get_work_items_by_skill(skill_name)
    return jsonify({
        'success': True,
        'data': work_items,
        'skill_name': skill_name
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"LLM configured: {Config.is_llm_configured()}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
