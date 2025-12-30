#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
database.py - SQLite database module for Weekly Report and OKR Assistant
"""

import sqlite3
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'reports.db')


def get_db_connection() -> sqlite3.Connection:
    """
    Get a database connection with row factory for dict-like access.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """
    Initialize the database with required tables.
    Creates tables if they don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create daily_reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_reports (
                entry_date TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create weekly_reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_reports (
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (start_date, end_date)
            )
        ''')
        
        # Create okr_reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS okr_reports (
                creation_date TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create todo_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todo_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ========================================
        # Career Asset Management Tables (新增)
        # ========================================
        
        # Create projects table (项目维度表)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                start_date TEXT,
                end_date TEXT,
                star_summary TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create work_items table (工作项原子表)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_log_date TEXT NOT NULL,
                project_id INTEGER,
                action TEXT,
                problem TEXT,
                result_metric TEXT,
                skills_tags TEXT,
                extraction_status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        
        # Create skills table (技能统计表)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                count INTEGER DEFAULT 0,
                first_used_date TEXT,
                last_used_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()


# ========================
# Daily Reports CRUD
# ========================

def save_daily_report(entry_date: str, content: str) -> bool:
    """
    Save or update a daily report.
    
    Args:
        entry_date: Date in YYYY-MM-DD format
        content: Daily report content
        
    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO daily_reports (entry_date, content, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(entry_date) DO UPDATE SET
                content = excluded.content,
                updated_at = CURRENT_TIMESTAMP
        ''', (entry_date, content))
        
        conn.commit()
        logger.info(f"Daily report saved for {entry_date}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving daily report: {e}")
        return False
    finally:
        conn.close()


def get_daily_report(entry_date: str) -> Optional[Dict[str, Any]]:
    """
    Get a daily report by date.
    
    Args:
        entry_date: Date in YYYY-MM-DD format
        
    Returns:
        Dict with entry_date, content, created_at, updated_at or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'SELECT * FROM daily_reports WHERE entry_date = ?',
            (entry_date,)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        logger.error(f"Error getting daily report: {e}")
        return None
    finally:
        conn.close()


def get_daily_reports_by_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Get daily reports within a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        List of daily reports
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM daily_reports 
            WHERE entry_date >= ? AND entry_date <= ?
            ORDER BY entry_date
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"Error getting daily reports: {e}")
        return []
    finally:
        conn.close()


def get_all_daily_report_dates() -> List[str]:
    """
    Get all dates that have daily reports.
    
    Returns:
        List of dates in YYYY-MM-DD format
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT entry_date FROM daily_reports ORDER BY entry_date DESC')
        rows = cursor.fetchall()
        return [row['entry_date'] for row in rows]
        
    except Exception as e:
        logger.error(f"Error getting daily report dates: {e}")
        return []
    finally:
        conn.close()


def delete_daily_report(entry_date: str) -> bool:
    """
    Delete a daily report.
    
    Args:
        entry_date: Date in YYYY-MM-DD format
        
    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM daily_reports WHERE entry_date = ?', (entry_date,))
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        logger.error(f"Error deleting daily report: {e}")
        return False
    finally:
        conn.close()


# ========================
# Weekly Reports CRUD
# ========================

def save_weekly_report(start_date: str, end_date: str, content: str) -> bool:
    """
    Save or update a weekly report.
    
    Args:
        start_date: Week start date (Monday) in YYYY-MM-DD format
        end_date: Week end date (Friday) in YYYY-MM-DD format
        content: Weekly report content
        
    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO weekly_reports (start_date, end_date, content, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(start_date, end_date) DO UPDATE SET
                content = excluded.content,
                updated_at = CURRENT_TIMESTAMP
        ''', (start_date, end_date, content))
        
        conn.commit()
        logger.info(f"Weekly report saved for {start_date} ~ {end_date}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving weekly report: {e}")
        return False
    finally:
        conn.close()


def get_weekly_report(start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
    """
    Get a weekly report by start and end date.
    
    Args:
        start_date: Week start date in YYYY-MM-DD format
        end_date: Week end date in YYYY-MM-DD format
        
    Returns:
        Dict with start_date, end_date, content, created_at, updated_at or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM weekly_reports 
            WHERE start_date = ? AND end_date = ?
        ''', (start_date, end_date))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        logger.error(f"Error getting weekly report: {e}")
        return None
    finally:
        conn.close()


def get_latest_weekly_report() -> Optional[Dict[str, Any]]:
    """
    Get the most recent weekly report (by end_date closest to today).
    
    Returns:
        Dict with weekly report data or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        today = date.today().isoformat()
        cursor.execute('''
            SELECT * FROM weekly_reports 
            ORDER BY ABS(julianday(end_date) - julianday(?))
            LIMIT 1
        ''', (today,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        logger.error(f"Error getting latest weekly report: {e}")
        return None
    finally:
        conn.close()


def get_all_weekly_reports() -> List[Dict[str, Any]]:
    """
    Get all weekly reports ordered by end_date descending.
    
    Returns:
        List of weekly reports
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM weekly_reports 
            ORDER BY end_date DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"Error getting all weekly reports: {e}")
        return []
    finally:
        conn.close()


def search_weekly_reports(start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
    """
    Search weekly reports by start_date and/or end_date.
    
    Args:
        start_date: Optional filter by start_date
        end_date: Optional filter by end_date
        
    Returns:
        List of matching weekly reports
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = 'SELECT * FROM weekly_reports WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND start_date = ?'
            params.append(start_date)
            
        if end_date:
            query += ' AND end_date = ?'
            params.append(end_date)
            
        query += ' ORDER BY end_date DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"Error searching weekly reports: {e}")
        return []
    finally:
        conn.close()


def delete_weekly_report(start_date: str, end_date: str) -> bool:
    """
    Delete a weekly report.
    
    Args:
        start_date: Week start date in YYYY-MM-DD format
        end_date: Week end date in YYYY-MM-DD format
        
    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            DELETE FROM weekly_reports 
            WHERE start_date = ? AND end_date = ?
        ''', (start_date, end_date))
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        logger.error(f"Error deleting weekly report: {e}")
        return False
    finally:
        conn.close()


# ========================
# OKR Reports CRUD
# ========================

def save_okr_report(creation_date: str, content: str) -> bool:
    """
    Save or update an OKR report.
    
    Args:
        creation_date: Creation date in YYYY-MM-DD format
        content: OKR content
        
    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO okr_reports (creation_date, content, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(creation_date) DO UPDATE SET
                content = excluded.content,
                updated_at = CURRENT_TIMESTAMP
        ''', (creation_date, content))
        
        conn.commit()
        logger.info(f"OKR report saved for {creation_date}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving OKR report: {e}")
        return False
    finally:
        conn.close()


def get_okr_report(creation_date: str) -> Optional[Dict[str, Any]]:
    """
    Get an OKR report by creation date.
    
    Args:
        creation_date: Creation date in YYYY-MM-DD format
        
    Returns:
        Dict with creation_date, content, created_at, updated_at or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'SELECT * FROM okr_reports WHERE creation_date = ?',
            (creation_date,)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        logger.error(f"Error getting OKR report: {e}")
        return None
    finally:
        conn.close()


def get_latest_okr_report() -> Optional[Dict[str, Any]]:
    """
    Get the most recent OKR report.
    
    Returns:
        Dict with OKR report data or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM okr_reports 
            ORDER BY creation_date DESC
            LIMIT 1
        ''')
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        logger.error(f"Error getting latest OKR report: {e}")
        return None
    finally:
        conn.close()


def get_all_okr_reports() -> List[Dict[str, Any]]:
    """
    Get all OKR reports ordered by creation_date descending.
    
    Returns:
        List of OKR reports
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM okr_reports 
            ORDER BY creation_date DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"Error getting all OKR reports: {e}")
        return []
    finally:
        conn.close()


def delete_okr_report(creation_date: str) -> bool:
    """
    Delete an OKR report.
    
    Args:
        creation_date: Creation date in YYYY-MM-DD format
        
    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM okr_reports WHERE creation_date = ?', (creation_date,))
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        logger.error(f"Error deleting OKR report: {e}")
        return False
    finally:
        conn.close()


# ===================
# TODO Items Functions
# ===================

def get_all_todo_items() -> List[Dict[str, Any]]:
    """
    Get all TODO items.
    
    Returns:
        List of TODO items
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM todo_items 
            ORDER BY sort_order ASC, created_at DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"Error getting TODO items: {e}")
        return []
    finally:
        conn.close()


def create_todo_item(content: str) -> Optional[Dict[str, Any]]:
    """
    Create a new TODO item.
    
    Args:
        content: TODO item content
        
    Returns:
        Created TODO item or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get max sort_order
        cursor.execute('SELECT COALESCE(MAX(sort_order), 0) + 1 FROM todo_items')
        next_order = cursor.fetchone()[0]
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO todo_items (content, completed, sort_order, created_at, updated_at)
            VALUES (?, 0, ?, ?, ?)
        ''', (content, next_order, now, now))
        
        conn.commit()
        
        # Get the created item
        cursor.execute('SELECT * FROM todo_items WHERE id = ?', (cursor.lastrowid,))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    except Exception as e:
        logger.error(f"Error creating TODO item: {e}")
        return None
    finally:
        conn.close()


def update_todo_item(item_id: int, content: str = None, completed: bool = None) -> Optional[Dict[str, Any]]:
    """
    Update a TODO item.
    
    Args:
        item_id: TODO item ID
        content: New content (optional)
        completed: New completed status (optional)
        
    Returns:
        Updated TODO item or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if content is not None:
            updates.append('content = ?')
            params.append(content)
        
        if completed is not None:
            updates.append('completed = ?')
            params.append(1 if completed else 0)
        
        if not updates:
            return None
            
        updates.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        params.append(item_id)
        
        cursor.execute(f'''
            UPDATE todo_items 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        
        conn.commit()
        
        if cursor.rowcount > 0:
            cursor.execute('SELECT * FROM todo_items WHERE id = ?', (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        return None
        
    except Exception as e:
        logger.error(f"Error updating TODO item: {e}")
        return None
    finally:
        conn.close()


def delete_todo_item(item_id: int) -> bool:
    """
    Delete a TODO item.
    
    Args:
        item_id: TODO item ID
        
    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM todo_items WHERE id = ?', (item_id,))
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        logger.error(f"Error deleting TODO item: {e}")
        return False
    finally:
        conn.close()


# ========================================
# Career Asset Management: Projects CRUD
# ========================================

def create_project(name: str, description: str = None, status: str = 'active') -> Optional[Dict[str, Any]]:
    """
    Create a new project.
    
    Args:
        name: Project name (unique)
        description: Project description
        status: Project status (active, archived)
        
    Returns:
        Created project dict or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO projects (name, description, status, start_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, status, now[:10], now, now))
        
        conn.commit()
        project_id = cursor.lastrowid
        
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    except sqlite3.IntegrityError:
        logger.warning(f"Project '{name}' already exists")
        cursor.execute('SELECT * FROM projects WHERE name = ?', (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return None
    finally:
        conn.close()


def get_project_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a project by name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM projects WHERE name = ?', (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        return None
    finally:
        conn.close()


def get_project_by_id(project_id: int) -> Optional[Dict[str, Any]]:
    """Get a project by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        return None
    finally:
        conn.close()


def get_all_projects(status: str = None) -> List[Dict[str, Any]]:
    """
    Get all projects, optionally filtered by status.
    
    Args:
        status: Filter by status (active, archived)
        
    Returns:
        List of project dicts
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if status:
            cursor.execute('SELECT * FROM projects WHERE status = ? ORDER BY updated_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM projects ORDER BY updated_at DESC')
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        return []
    finally:
        conn.close()


def update_project(project_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Update a project.
    
    Args:
        project_id: Project ID
        **kwargs: Fields to update (name, description, status, star_summary, end_date)
        
    Returns:
        Updated project dict or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['name', 'description', 'status', 'star_summary', 'end_date']
    updates = []
    params = []
    
    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            updates.append(f'{field} = ?')
            params.append(value)
    
    if not updates:
        return get_project_by_id(project_id)
    
    updates.append('updated_at = ?')
    params.append(datetime.now().isoformat())
    params.append(project_id)
    
    try:
        cursor.execute(f'''
            UPDATE projects SET {', '.join(updates)} WHERE id = ?
        ''', params)
        conn.commit()
        
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        return None
    finally:
        conn.close()


def delete_project(project_id: int) -> bool:
    """Delete a project and its work items."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM work_items WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        return False
    finally:
        conn.close()


def delete_all_projects() -> Dict[str, Any]:
    """Delete all projects and their work items."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) as count FROM projects')
        project_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM work_items')
        work_item_count = cursor.fetchone()['count']
        
        cursor.execute('DELETE FROM work_items')
        cursor.execute('DELETE FROM projects')
        cursor.execute('DELETE FROM skills')
        conn.commit()
        
        return {
            'success': True,
            'message': f'已删除 {project_count} 个项目和 {work_item_count} 条工作记录',
            'deleted_projects': project_count,
            'deleted_work_items': work_item_count
        }
    except Exception as e:
        logger.error(f"Error deleting all projects: {e}")
        conn.rollback()
        return {
            'success': False,
            'message': str(e)
        }
    finally:
        conn.close()


# ========================================
# Career Asset Management: Work Items CRUD
# ========================================

def create_work_item(
    raw_log_date: str,
    project_id: int = None,
    action: str = None,
    problem: str = None,
    result_metric: str = None,
    skills_tags: str = None,
    extraction_status: str = 'pending'
) -> Optional[Dict[str, Any]]:
    """
    Create a new work item.
    
    Args:
        raw_log_date: Date from daily log (YYYY-MM-DD)
        project_id: Associated project ID
        action: What was done
        problem: Problem encountered
        result_metric: Quantified result
        skills_tags: JSON array of skill tags
        extraction_status: pending, extracted, needs_review
        
    Returns:
        Created work item dict or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO work_items 
            (raw_log_date, project_id, action, problem, result_metric, skills_tags, extraction_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (raw_log_date, project_id, action, problem, result_metric, skills_tags, extraction_status, now, now))
        
        conn.commit()
        item_id = cursor.lastrowid
        
        cursor.execute('SELECT * FROM work_items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error creating work item: {e}")
        return None
    finally:
        conn.close()


def get_work_items_by_project(project_id: int) -> List[Dict[str, Any]]:
    """Get all work items for a project."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM work_items WHERE project_id = ? ORDER BY raw_log_date DESC
        ''', (project_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting work items: {e}")
        return []
    finally:
        conn.close()


def get_work_items_by_date_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Get work items within a date range."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT w.*, p.name as project_name 
            FROM work_items w
            LEFT JOIN projects p ON w.project_id = p.id
            WHERE w.raw_log_date BETWEEN ? AND ?
            ORDER BY w.raw_log_date DESC
        ''', (start_date, end_date))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting work items: {e}")
        return []
    finally:
        conn.close()


def get_all_work_items() -> List[Dict[str, Any]]:
    """Get all work items with project info."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT w.*, p.name as project_name 
            FROM work_items w
            LEFT JOIN projects p ON w.project_id = p.id
            ORDER BY w.raw_log_date DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting work items: {e}")
        return []
    finally:
        conn.close()


def update_work_item(item_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """Update a work item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['project_id', 'action', 'problem', 'result_metric', 'skills_tags', 'extraction_status']
    updates = []
    params = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            updates.append(f'{field} = ?')
            params.append(value)
    
    if not updates:
        return None
    
    updates.append('updated_at = ?')
    params.append(datetime.now().isoformat())
    params.append(item_id)
    
    try:
        cursor.execute(f'''
            UPDATE work_items SET {', '.join(updates)} WHERE id = ?
        ''', params)
        conn.commit()
        
        cursor.execute('SELECT * FROM work_items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error updating work item: {e}")
        return None
    finally:
        conn.close()


def delete_work_item(item_id: int) -> bool:
    """Delete a work item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM work_items WHERE id = ?', (item_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting work item: {e}")
        return False
    finally:
        conn.close()


# ========================================
# Career Asset Management: Skills CRUD
# ========================================

def infer_skill_category(skill_name: str) -> str:
    """
    Infer skill category based on skill name.
    
    Args:
        skill_name: Name of the skill
        
    Returns:
        Category string: 'tech', 'soft', 'domain', or None
    """
    if not skill_name:
        return None
    
    skill_lower = skill_name.lower()
    
    # 技术技能关键词
    tech_keywords = [
        'python', 'java', 'javascript', 'typescript', 'react', 'vue', 'angular',
        'node', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker',
        'kubernetes', 'k8s', 'aws', 'azure', 'gcp', 'git', 'linux', 'shell',
        'api', 'rest', 'graphql', 'json', 'xml', 'html', 'css', 'sass',
        'webpack', 'nginx', 'apache', 'flask', 'django', 'spring', 'golang',
        'rust', 'c++', 'c#', '.net', 'swift', 'kotlin', 'flutter', 'dart',
        'tensorflow', 'pytorch', 'ai', 'ml', '机器学习', '深度学习', '算法',
        '前端', '后端', '全栈', '架构', '数据库', '缓存', '微服务', '容器',
        '代码', '开发', '编程', '测试', '自动化', 'ci', 'cd', 'devops',
        '性能优化', '重构', '调试', 'debug', '接口', '系统', '服务', '部署',
        'excel', 'vba', 'power bi', 'tableau', '数据分析', '可视化'
    ]
    
    # 软技能关键词
    soft_keywords = [
        '沟通', '协调', '汇报', '表达', '演讲', '培训', '指导', '带教',
        '团队', '协作', '配合', '管理', '领导', '规划', '计划', '组织',
        '分析', '思考', '解决问题', '决策', '判断', '创新', '学习',
        '时间管理', '项目管理', '文档', '写作', '总结', '复盘', '反思',
        '跨部门', '对接', '推进', '跟进', '落地', '执行', '谈判', '需求分析'
    ]
    
    # 业务领域关键词
    domain_keywords = [
        '财务', '会计', '预算', '成本', '审计', '税务', '报表',
        '人力', 'hr', '招聘', '绩效', '薪酬', '培训',
        '销售', '营销', '市场', '客户', '运营', '产品',
        '供应链', '采购', '物流', '仓储', '生产', '制造', '质量',
        '法务', '合规', '知识产权', '行政', '后勤',
        '业务', '流程', '制度', '标准', '规范',
        '汽车', '零部件', '检验', '控制计划', '工艺', '设备'
    ]
    
    for keyword in tech_keywords:
        if keyword in skill_lower:
            return 'tech'
    
    for keyword in soft_keywords:
        if keyword in skill_lower:
            return 'soft'
    
    for keyword in domain_keywords:
        if keyword in skill_lower:
            return 'domain'
    
    return None


def upsert_skill(name: str, category: str = None) -> Optional[Dict[str, Any]]:
    """
    Create or update a skill, incrementing count.
    
    Args:
        name: Skill name
        category: Skill category (tech, soft, domain)
        
    Returns:
        Skill dict or None
    """
    # 过滤无效的技能名
    if not name or name.lower() in ['null', 'none', '待补充', '']:
        return None
    
    # 如果没有指定 category，尝试自动推断
    if not category:
        category = infer_skill_category(name)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        today = now[:10]
        
        # Check if skill exists
        cursor.execute('SELECT * FROM skills WHERE name = ?', (name,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE skills SET 
                    count = count + 1, 
                    last_used_date = ?,
                    updated_at = ?
                WHERE name = ?
            ''', (today, now, name))
        else:
            cursor.execute('''
                INSERT INTO skills (name, category, count, first_used_date, last_used_date, created_at, updated_at)
                VALUES (?, ?, 1, ?, ?, ?, ?)
            ''', (name, category, today, today, now, now))
        
        conn.commit()
        
        cursor.execute('SELECT * FROM skills WHERE name = ?', (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error upserting skill: {e}")
        return None
    finally:
        conn.close()


def recategorize_all_skills() -> Dict[str, Any]:
    """
    重新推断所有技能的分类（使用关键词匹配）。
    
    Returns:
        包含操作结果的字典
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, name, category FROM skills')
        skills = cursor.fetchall()
        
        updated_count = 0
        now = datetime.now().isoformat()
        
        for skill in skills:
            new_category = infer_skill_category(skill['name'])
            if new_category and new_category != skill['category']:
                cursor.execute('''
                    UPDATE skills SET category = ?, updated_at = ? WHERE id = ?
                ''', (new_category, now, skill['id']))
                updated_count += 1
        
        conn.commit()
        
        return {
            'success': True,
            'message': f'已更新 {updated_count} 个技能的分类',
            'updated_count': updated_count,
            'total_skills': len(skills)
        }
    except Exception as e:
        logger.error(f"Error recategorizing skills: {e}")
        conn.rollback()
        return {
            'success': False,
            'message': str(e)
        }
    finally:
        conn.close()


def get_all_skills_for_categorization() -> List[Dict[str, Any]]:
    """获取所有技能用于分类。"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, name, category FROM skills 
            WHERE name IS NOT NULL 
              AND name != '' 
              AND LOWER(name) NOT IN ('null', 'none', '待补充')
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting skills for categorization: {e}")
        return []
    finally:
        conn.close()


def update_skill_categories(categorized_skills: List[Dict]) -> Dict[str, Any]:
    """
    批量更新技能分类。
    
    Args:
        categorized_skills: 包含 id, new_category 的技能列表
        
    Returns:
        操作结果
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        updated_count = 0
        
        for skill in categorized_skills:
            cursor.execute('''
                UPDATE skills SET category = ?, updated_at = ? WHERE id = ?
            ''', (skill['new_category'], now, skill['id']))
            if cursor.rowcount > 0:
                updated_count += 1
        
        conn.commit()
        
        return {
            'success': True,
            'message': f'已更新 {updated_count} 个技能的分类',
            'updated_count': updated_count
        }
    except Exception as e:
        logger.error(f"Error updating skill categories: {e}")
        conn.rollback()
        return {
            'success': False,
            'message': str(e)
        }
    finally:
        conn.close()


def get_work_items_by_skill(skill_name: str) -> List[Dict[str, Any]]:
    """
    获取包含指定技能的所有工作条目。
    
    Args:
        skill_name: 技能名称
        
    Returns:
        工作条目列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 搜索 skills_tags JSON 字段中包含该技能的工作条目
        # SQLite 使用 LIKE 进行简单的 JSON 搜索
        search_pattern = f'%"{skill_name}"%'
        
        cursor.execute('''
            SELECT w.*, p.name as project_name
            FROM work_items w
            LEFT JOIN projects p ON w.project_id = p.id
            WHERE w.skills_tags LIKE ?
            ORDER BY w.raw_log_date DESC
        ''', (search_pattern,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting work items by skill: {e}")
        return []
    finally:
        conn.close()


def get_all_skills() -> List[Dict[str, Any]]:
    """Get all skills sorted by count, filtering out invalid entries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 过滤掉无效的技能名
        cursor.execute('''
            SELECT * FROM skills 
            WHERE name IS NOT NULL 
              AND name != '' 
              AND LOWER(name) NOT IN ('null', 'none', '待补充')
            ORDER BY count DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting skills: {e}")
        return []
    finally:
        conn.close()


def get_skills_stats() -> Dict[str, Any]:
    """Get skills statistics for radar chart."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 过滤无效技能名的条件
        valid_skills_condition = '''
            name IS NOT NULL 
            AND name != '' 
            AND LOWER(name) NOT IN ('null', 'none', '待补充')
        '''
        
        # Get top skills (排除无效数据)
        cursor.execute(f'''
            SELECT name, count FROM skills 
            WHERE {valid_skills_condition}
            ORDER BY count DESC LIMIT 10
        ''')
        top_skills = [{'name': row['name'], 'count': row['count']} for row in cursor.fetchall()]
        
        # Get skills by category (排除无效数据)
        cursor.execute(f'''
            SELECT category, SUM(count) as total_count 
            FROM skills 
            WHERE category IS NOT NULL AND {valid_skills_condition}
            GROUP BY category
        ''')
        by_category = {row['category']: row['total_count'] for row in cursor.fetchall()}
        
        # Get total skills count (排除无效数据)
        cursor.execute(f'SELECT COUNT(*) as total FROM skills WHERE {valid_skills_condition}')
        total = cursor.fetchone()['total']
        
        return {
            'top_skills': top_skills,
            'by_category': by_category,
            'total_unique': total
        }
    except Exception as e:
        logger.error(f"Error getting skills stats: {e}")
        return {'top_skills': [], 'by_category': {}, 'total_unique': 0}
    finally:
        conn.close()


def get_project_with_work_items(project_id: int) -> Optional[Dict[str, Any]]:
    """Get a project with all its work items."""
    project = get_project_by_id(project_id)
    if project:
        project['work_items'] = get_work_items_by_project(project_id)
    return project


def get_projects_summary() -> List[Dict[str, Any]]:
    """Get projects summary with work item counts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT 
                p.*,
                COUNT(w.id) as work_item_count,
                MIN(w.raw_log_date) as first_work_date,
                MAX(w.raw_log_date) as last_work_date
            FROM projects p
            LEFT JOIN work_items w ON p.id = w.project_id
            GROUP BY p.id
            ORDER BY p.updated_at DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting projects summary: {e}")
        return []
    finally:
        conn.close()


def merge_null_projects_to_temporary() -> Dict[str, Any]:
    """
    将所有名为 null、空字符串或无效名称的项目的工作条目
    合并到一个叫做"临时工作"的项目中，然后删除这些无效项目。
    
    Returns:
        包含操作结果的字典
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. 查找或创建"临时工作"项目
        cursor.execute("SELECT id FROM projects WHERE name = '临时工作'")
        row = cursor.fetchone()
        
        if row:
            temp_project_id = row['id']
        else:
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO projects (name, description, status, created_at, updated_at)
                VALUES ('临时工作', '未归类到具体项目的临时性工作', 'active', ?, ?)
            ''', (now, now))
            temp_project_id = cursor.lastrowid
        
        # 2. 查找所有无效项目（null、空、undefined等）
        cursor.execute('''
            SELECT id, name FROM projects 
            WHERE name IS NULL 
               OR name = 'null' 
               OR name = 'undefined'
               OR TRIM(name) = ''
        ''')
        invalid_projects = cursor.fetchall()
        
        if not invalid_projects:
            return {
                'success': True,
                'message': '没有需要处理的无效项目',
                'merged_count': 0,
                'deleted_projects': 0
            }
        
        invalid_project_ids = [p['id'] for p in invalid_projects]
        
        # 3. 将这些项目的工作条目迁移到"临时工作"
        placeholders = ','.join('?' * len(invalid_project_ids))
        cursor.execute(f'''
            UPDATE work_items 
            SET project_id = ? 
            WHERE project_id IN ({placeholders})
        ''', [temp_project_id] + invalid_project_ids)
        merged_count = cursor.rowcount
        
        # 4. 删除这些无效项目
        cursor.execute(f'''
            DELETE FROM projects WHERE id IN ({placeholders})
        ''', invalid_project_ids)
        deleted_count = cursor.rowcount
        
        conn.commit()
        
        return {
            'success': True,
            'message': f'成功将 {merged_count} 条工作记录合并到"临时工作"项目',
            'merged_count': merged_count,
            'deleted_projects': deleted_count,
            'temp_project_id': temp_project_id
        }
        
    except Exception as e:
        logger.error(f"Error merging null projects: {e}")
        conn.rollback()
        return {
            'success': False,
            'message': str(e),
            'merged_count': 0,
            'deleted_projects': 0
        }
    finally:
        conn.close()


def merge_similar_projects(target_project_id: int, source_project_ids: List[int]) -> Dict[str, Any]:
    """
    将多个相似项目合并到目标项目。
    
    Args:
        target_project_id: 目标项目ID（保留的项目）
        source_project_ids: 要合并的源项目ID列表
        
    Returns:
        包含操作结果的字典
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 确保目标项目存在
        cursor.execute('SELECT id, name FROM projects WHERE id = ?', (target_project_id,))
        target = cursor.fetchone()
        if not target:
            return {
                'success': False,
                'message': f'目标项目 {target_project_id} 不存在'
            }
        
        # 过滤掉目标项目ID
        source_ids = [sid for sid in source_project_ids if sid != target_project_id]
        
        if not source_ids:
            return {
                'success': True,
                'message': '没有需要合并的项目',
                'merged_count': 0
            }
        
        # 迁移工作条目
        placeholders = ','.join('?' * len(source_ids))
        cursor.execute(f'''
            UPDATE work_items 
            SET project_id = ? 
            WHERE project_id IN ({placeholders})
        ''', [target_project_id] + source_ids)
        merged_count = cursor.rowcount
        
        # 删除源项目
        cursor.execute(f'''
            DELETE FROM projects WHERE id IN ({placeholders})
        ''', source_ids)
        deleted_count = cursor.rowcount
        
        # 更新目标项目的更新时间
        now = datetime.now().isoformat()
        cursor.execute('UPDATE projects SET updated_at = ? WHERE id = ?', (now, target_project_id))
        
        conn.commit()
        
        return {
            'success': True,
            'message': f'成功将 {merged_count} 条工作记录合并到项目 "{target["name"]}"',
            'merged_count': merged_count,
            'deleted_projects': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error merging projects: {e}")
        conn.rollback()
        return {
            'success': False,
            'message': str(e)
        }
    finally:
        conn.close()


def find_similar_project_groups(threshold: float = 0.6) -> List[Dict[str, Any]]:
    """
    查找相似的项目并分组。
    
    Args:
        threshold: 相似度阈值 (0-1)
        
    Returns:
        相似项目组列表
    """
    from difflib import SequenceMatcher
    
    projects = get_all_projects()
    if not projects:
        return []
    
    # 过滤掉无效项目名
    valid_projects = [p for p in projects if p['name'] and p['name'] != 'null' and p['name'].strip()]
    
    # 用于标记已分组的项目
    grouped = set()
    groups = []
    
    for i, p1 in enumerate(valid_projects):
        if p1['id'] in grouped:
            continue
            
        similar_group = [p1]
        
        for j, p2 in enumerate(valid_projects):
            if i >= j or p2['id'] in grouped:
                continue
            
            # 计算相似度
            ratio = SequenceMatcher(None, p1['name'], p2['name']).ratio()
            
            if ratio >= threshold:
                similar_group.append(p2)
                grouped.add(p2['id'])
        
        if len(similar_group) > 1:
            grouped.add(p1['id'])
            # 选择最短的名称作为推荐的目标项目
            similar_group.sort(key=lambda x: len(x['name']))
            groups.append({
                'recommended_target': similar_group[0],
                'projects': similar_group,
                'project_ids': [p['id'] for p in similar_group]
            })
    
    return groups


# Initialize database on module import
init_database()
