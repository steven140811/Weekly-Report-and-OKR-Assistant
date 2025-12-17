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


# Initialize database on module import
init_database()
