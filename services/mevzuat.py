"""
Mevzuat Takip Servisi
Web scraping, keyword matching, and alert management for EPDK regulations.
"""
import re
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_SCRAPING = True
except ImportError:
    HAS_SCRAPING = False

import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = os.environ.get('DATABASE_URL') or \
    'postgresql://postgres:518518Erkan@localhost:5432/osos_db'

logger = logging.getLogger(__name__)


@dataclass
class MevzuatItem:
    """Represents a found regulation item"""
    title: str
    url: str
    content_snippet: str
    published_date: Optional[datetime]
    matched_keywords: List[str]


class MevzuatService:
    """Service for managing mevzuat (regulation) tracking"""
    
    def __init__(self):
        self.conn = None
        self.cur = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    # ==================== SOURCES ====================
    
    def get_all_sources(self) -> List[Dict]:
        """Get all mevzuat sources"""
        self.cur.execute("""
            SELECT id, name, url, source_type, check_interval_hours,
                   last_checked_at, is_active, created_at
            FROM mevzuat_sources
            ORDER BY is_active DESC, name
        """)
        return self.cur.fetchall()
    
    def get_active_sources(self) -> List[Dict]:
        """Get only active sources"""
        self.cur.execute("""
            SELECT id, name, url, source_type, check_interval_hours,
                   last_checked_at, is_active
            FROM mevzuat_sources
            WHERE is_active = true
            ORDER BY name
        """)
        return self.cur.fetchall()
    
    def add_source(self, name: str, url: str, source_type: str = 'web',
                   check_interval_hours: int = 24) -> Dict:
        """Add a new source"""
        self.cur.execute("""
            INSERT INTO mevzuat_sources (name, url, source_type, check_interval_hours)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, url, source_type, check_interval_hours, is_active
        """, (name, url, source_type, check_interval_hours))
        self.conn.commit()
        return self.cur.fetchone()
    
    def update_source(self, source_id: int, **kwargs) -> bool:
        """Update a source"""
        allowed = {'name', 'url', 'source_type', 'check_interval_hours', 'is_active'}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return False
        
        set_clause = ', '.join(f"{k} = %s" for k in updates.keys())
        values = list(updates.values()) + [source_id]
        
        self.cur.execute(f"""
            UPDATE mevzuat_sources SET {set_clause} WHERE id = %s
        """, values)
        self.conn.commit()
        return self.cur.rowcount > 0
    
    def delete_source(self, source_id: int) -> bool:
        """Delete a source (also deletes related alerts)"""
        self.cur.execute("DELETE FROM mevzuat_alerts WHERE source_id = %s", (source_id,))
        self.cur.execute("DELETE FROM mevzuat_sources WHERE id = %s", (source_id,))
        self.conn.commit()
        return self.cur.rowcount > 0
    
    def mark_source_checked(self, source_id: int):
        """Update last_checked_at for a source"""
        self.cur.execute("""
            UPDATE mevzuat_sources SET last_checked_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (source_id,))
        self.conn.commit()
    
    # ==================== KEYWORDS ====================
    
    def get_all_keywords(self) -> List[Dict]:
        """Get all keywords"""
        self.cur.execute("""
            SELECT id, keyword, priority, is_active, created_at
            FROM mevzuat_keywords
            ORDER BY priority, keyword
        """)
        return self.cur.fetchall()
    
    def get_active_keywords(self) -> List[str]:
        """Get list of active keywords"""
        self.cur.execute("""
            SELECT keyword FROM mevzuat_keywords
            WHERE is_active = true
            ORDER BY priority
        """)
        return [row['keyword'] for row in self.cur.fetchall()]
    
    def add_keyword(self, keyword: str, priority: int = 1) -> Dict:
        """Add a new keyword"""
        self.cur.execute("""
            INSERT INTO mevzuat_keywords (keyword, priority)
            VALUES (%s, %s)
            RETURNING id, keyword, priority, is_active
        """, (keyword, priority))
        self.conn.commit()
        return self.cur.fetchone()
    
    def update_keyword(self, keyword_id: int, **kwargs) -> bool:
        """Update a keyword"""
        allowed = {'keyword', 'priority', 'is_active'}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return False
        
        set_clause = ', '.join(f"{k} = %s" for k in updates.keys())
        values = list(updates.values()) + [keyword_id]
        
        self.cur.execute(f"""
            UPDATE mevzuat_keywords SET {set_clause} WHERE id = %s
        """, values)
        self.conn.commit()
        return self.cur.rowcount > 0
    
    def delete_keyword(self, keyword_id: int) -> bool:
        """Delete a keyword"""
        self.cur.execute("DELETE FROM mevzuat_keywords WHERE id = %s", (keyword_id,))
        self.conn.commit()
        return self.cur.rowcount > 0
    
    # ==================== ALERTS ====================
    
    def get_alerts(self, limit: int = 50, unread_only: bool = False,
                   important_only: bool = False) -> List[Dict]:
        """Get alerts with filters"""
        conditions = []
        if unread_only:
            conditions.append("a.is_read = false")
        if important_only:
            conditions.append("a.is_important = true")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        self.cur.execute(f"""
            SELECT a.id, a.source_id, s.name as source_name, a.title, a.url,
                   a.content_snippet, a.matched_keywords, a.published_date,
                   a.found_at, a.is_read, a.is_important, a.notes
            FROM mevzuat_alerts a
            JOIN mevzuat_sources s ON a.source_id = s.id
            {where_clause}
            ORDER BY a.found_at DESC
            LIMIT %s
        """, (limit,))
        return self.cur.fetchall()
    
    def get_unread_count(self) -> int:
        """Get count of unread alerts"""
        self.cur.execute("SELECT COUNT(*) as count FROM mevzuat_alerts WHERE is_read = false")
        return self.cur.fetchone()['count']
    
    def add_alert(self, source_id: int, title: str, url: str,
                  content_snippet: str, matched_keywords: List[str],
                  published_date: Optional[datetime] = None) -> Dict:
        """Add a new alert"""
        # Check for duplicate (same URL)
        self.cur.execute("SELECT id FROM mevzuat_alerts WHERE url = %s", (url,))
        if self.cur.fetchone():
            return None  # Already exists
        
        self.cur.execute("""
            INSERT INTO mevzuat_alerts 
            (source_id, title, url, content_snippet, matched_keywords, published_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, title, url, matched_keywords, found_at
        """, (source_id, title, url, content_snippet, matched_keywords, published_date))
        self.conn.commit()
        return self.cur.fetchone()
    
    def mark_alert_read(self, alert_id: int) -> bool:
        """Mark an alert as read"""
        self.cur.execute("""
            UPDATE mevzuat_alerts SET is_read = true WHERE id = %s
        """, (alert_id,))
        self.conn.commit()
        return self.cur.rowcount > 0
    
    def mark_all_read(self) -> int:
        """Mark all alerts as read"""
        self.cur.execute("UPDATE mevzuat_alerts SET is_read = true WHERE is_read = false")
        self.conn.commit()
        return self.cur.rowcount
    
    def toggle_important(self, alert_id: int) -> bool:
        """Toggle important status of an alert"""
        self.cur.execute("""
            UPDATE mevzuat_alerts SET is_important = NOT is_important
            WHERE id = %s
        """, (alert_id,))
        self.conn.commit()
        return self.cur.rowcount > 0
    
    def update_alert_notes(self, alert_id: int, notes: str) -> bool:
        """Update notes for an alert"""
        self.cur.execute("""
            UPDATE mevzuat_alerts SET notes = %s WHERE id = %s
        """, (notes, alert_id))
        self.conn.commit()
        return self.cur.rowcount > 0
    
    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert"""
        self.cur.execute("DELETE FROM mevzuat_alerts WHERE id = %s", (alert_id,))
        self.conn.commit()
        return self.cur.rowcount > 0
    
    # ==================== SCRAPING ====================
    
    def check_text_for_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Check if text contains any of the keywords (case-insensitive)"""
        text_lower = text.lower()
        matched = []
        for kw in keywords:
            if kw.lower() in text_lower:
                matched.append(kw)
        return matched
    
    def scrape_source(self, source: Dict) -> List[MevzuatItem]:
        """Scrape a source for new content (basic implementation)"""
        if not HAS_SCRAPING:
            logger.warning("requests/beautifulsoup not installed, skipping scrape")
            return []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(source['url'], headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            keywords = self.get_active_keywords()
            items = []
            
            # Generic scraping - look for links with text
            for link in soup.find_all('a', href=True):
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                matched = self.check_text_for_keywords(title, keywords)
                if matched:
                    url = link['href']
                    if not url.startswith('http'):
                        # Make absolute URL
                        from urllib.parse import urljoin
                        url = urljoin(source['url'], url)
                    
                    items.append(MevzuatItem(
                        title=title[:500],
                        url=url,
                        content_snippet=title[:200],
                        published_date=None,
                        matched_keywords=matched
                    ))
            
            return items[:20]  # Limit results
            
        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {e}")
            return []
    
    def scan_all_sources(self) -> Dict[str, Any]:
        """Scan all active sources and add new alerts"""
        sources = self.get_active_sources()
        results = {
            'scanned': 0,
            'new_alerts': 0,
            'errors': []
        }
        
        for source in sources:
            try:
                items = self.scrape_source(source)
                for item in items:
                    alert = self.add_alert(
                        source_id=source['id'],
                        title=item.title,
                        url=item.url,
                        content_snippet=item.content_snippet,
                        matched_keywords=item.matched_keywords,
                        published_date=item.published_date
                    )
                    if alert:
                        results['new_alerts'] += 1
                
                self.mark_source_checked(source['id'])
                results['scanned'] += 1
                
            except Exception as e:
                results['errors'].append(f"{source['name']}: {str(e)}")
        
        return results
    
    # ==================== DASHBOARD ====================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get statistics for dashboard widget"""
        self.cur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM mevzuat_alerts WHERE is_read = false) as unread_count,
                (SELECT COUNT(*) FROM mevzuat_alerts WHERE is_important = true) as important_count,
                (SELECT COUNT(*) FROM mevzuat_alerts 
                 WHERE found_at > CURRENT_TIMESTAMP - INTERVAL '7 days') as week_count,
                (SELECT COUNT(*) FROM mevzuat_sources WHERE is_active = true) as active_sources
        """)
        return self.cur.fetchone()
    
    def get_recent_alerts(self, limit: int = 5) -> List[Dict]:
        """Get recent alerts for dashboard"""
        self.cur.execute("""
            SELECT a.id, a.title, s.name as source_name, a.matched_keywords,
                   a.found_at, a.is_read, a.is_important
            FROM mevzuat_alerts a
            JOIN mevzuat_sources s ON a.source_id = s.id
            ORDER BY a.found_at DESC
            LIMIT %s
        """, (limit,))
        return self.cur.fetchall()
