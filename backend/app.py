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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"LLM configured: {Config.is_llm_configured()}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
