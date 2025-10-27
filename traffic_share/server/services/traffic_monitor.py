"""Real-time traffic monitoring service."""

import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from traffic_share.server.database import SessionLocal
from traffic_share.server.models import TrafficSession, TrafficLog
from traffic_share.core.constants import SessionStatus

class TrafficMonitor:
    """Real-time traffic monitoring service."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.monitoring = False
        self.update_interval = 10  # seconds
    
    async def start_monitoring(self):
        """Start traffic monitoring."""
        self.monitoring = True
        print("Traffic monitoring started")
        
        while self.monitoring:
            try:
                await self._update_all_sessions()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in traffic monitoring: {e}")
                await asyncio.sleep(5)
    
    async def stop_monitoring(self):
        """Stop traffic monitoring."""
        self.monitoring = False
        print("Traffic monitoring stopped")
    
    async def add_session(self, session_id: str, user_id: int, device_id: int):
        """Add session to monitoring."""
        self.active_sessions[session_id] = {
            'user_id': user_id,
            'device_id': device_id,
            'start_time': datetime.utcnow(),
            'last_update': datetime.utcnow(),
            'bytes_tx': 0,
            'bytes_rx': 0,
            'bytes_total': 0,
        }
        print(f"Added session {session_id} to monitoring")
    
    async def remove_session(self, session_id: str):
        """Remove session from monitoring."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            print(f"Removed session {session_id} from monitoring")
    
    async def update_session_traffic(self, session_id: str, bytes_tx: int, bytes_rx: int):
        """Update session traffic data."""
        if session_id in self.active_sessions:
            session_data = self.active_sessions[session_id]
            session_data['bytes_tx'] += bytes_tx
            session_data['bytes_rx'] += bytes_rx
            session_data['bytes_total'] = session_data['bytes_tx'] + session_data['bytes_rx']
            session_data['last_update'] = datetime.utcnow()
    
    async def _update_all_sessions(self):
        """Update all active sessions in database."""
        if not self.active_sessions:
            return
        
        db = SessionLocal()
        try:
            for session_id, session_data in self.active_sessions.items():
                await self._update_session_in_db(db, session_id, session_data)
        finally:
            db.close()
    
    async def _update_session_in_db(self, db: Session, session_id: str, session_data: Dict):
        """Update session in database."""
        try:
            # Find session in database
            session = db.query(TrafficSession).filter(
                TrafficSession.session_id == session_id
            ).first()
            
            if not session:
                # Session not found, remove from monitoring
                await self.remove_session(session_id)
                return
            
            # Update session data
            session.bytes_tx = session_data['bytes_tx']
            session.bytes_rx = session_data['bytes_rx']
            session.bytes_total = session_data['bytes_total']
            session.updated_at = datetime.utcnow()
            
            # Create traffic log entry
            log = TrafficLog(
                session_id=session.id,
                bytes_tx=session_data['bytes_tx'],
                bytes_rx=session_data['bytes_rx']
            )
            db.add(log)
            
            db.commit()
            
        except Exception as e:
            print(f"Error updating session {session_id}: {e}")
            db.rollback()
    
    async def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """Get session statistics."""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id].copy()
        return None
    
    async def get_all_stats(self) -> Dict:
        """Get all active sessions statistics."""
        return {
            'active_sessions': len(self.active_sessions),
            'total_bytes': sum(s['bytes_total'] for s in self.active_sessions.values()),
            'sessions': list(self.active_sessions.keys())
        }
    
    async def cleanup_stale_sessions(self):
        """Clean up stale sessions (older than 1 hour without update)."""
        current_time = datetime.utcnow()
        stale_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            if current_time - session_data['last_update'] > timedelta(hours=1):
                stale_sessions.append(session_id)
        
        for session_id in stale_sessions:
            await self.remove_session(session_id)
            print(f"Removed stale session: {session_id}")

# Global traffic monitor instance
traffic_monitor = TrafficMonitor()
