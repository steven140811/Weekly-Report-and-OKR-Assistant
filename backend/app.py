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
    use_mock = data.get('use_mock', False)
    
    # If LLM not configured, force mock mode
    if not Config.is_llm_configured():
        use_mock = True
        logger.info("LLM not configured, using mock mode")
    
    result = generate_weekly_report(content, use_mock=use_mock)
    
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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"LLM configured: {Config.is_llm_configured()}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
