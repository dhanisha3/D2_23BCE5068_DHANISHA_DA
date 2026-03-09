#!/usr/bin/env python3
"""
Secure Locker System
A simple backend for managing delivery lockers with QR code authentication
"""

import uuid
import hashlib
import json
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
import base64
from db import get_connection, init_db


class SecureLocker:
    def __init__(self, locker_id: str, location: str):
        self.locker_id = locker_id
        self.location = location

    @staticmethod
    def log_access(locker_id, delivery_id, role, qr_token, action, cursor=None):
        # Use provided cursor if available, else open a new connection
        if cursor is not None:
            cursor.execute(
                """
                INSERT INTO access_logs (locker_id, delivery_id, role, qr_token, action)
                VALUES (?, ?, ?, ?, ?)
                """,
                (locker_id, delivery_id, role, hashlib.sha256(qr_token.encode()).hexdigest()[:8], action)
            )
        else:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO access_logs (locker_id, delivery_id, role, qr_token, action)
                VALUES (?, ?, ?, ?, ?)
                """,
                (locker_id, delivery_id, role, hashlib.sha256(qr_token.encode()).hexdigest()[:8], action)
            )
            conn.commit()
            conn.close()

class DeliverySystem:
    def __init__(self):
        init_db()

    def add_locker(self, locker_id: str, location: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO lockers (locker_id, address, status) VALUES (?, ?, 'available')", (locker_id, location))
        conn.commit()
        conn.close()
        return f"Locker {locker_id} added at {location}"

    def generate_delivery_qr(self, delivery_id: str, customer_phone: str, locker_id: str, 
                           customer_email: str = '', package_size: str = 'medium', 
                           priority: str = 'standard', delivery_notes: str = '') -> tuple:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT locker_id FROM lockers WHERE locker_id=?", (locker_id,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError(f"Locker {locker_id} not found")

        # Check if locker is already assigned to any active delivery
        cursor.execute("""
            SELECT delivery_id, status FROM deliveries 
            WHERE locker_id=? AND status IN ('pending_delivery', 'deposited', 'ready_for_pickup')
        """, (locker_id,))
        existing_delivery = cursor.fetchone()
        if existing_delivery:
            conn.close()
            raise ValueError(f"Locker {locker_id} is already assigned to delivery {existing_delivery[0]} (Status: {existing_delivery[1]})")

        agent_token = str(uuid.uuid4())
        customer_token = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(days=7)).isoformat()
        cursor.execute(
            """
            INSERT INTO deliveries (delivery_id, customer_phone, customer_email, locker_id, agent_qr, customer_qr, 
                                  status, priority, package_size, delivery_notes, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending_delivery', ?, ?, ?, ?, ?)
            """,
            (delivery_id, customer_phone, customer_email, locker_id, agent_token, customer_token, 
             priority, package_size, delivery_notes, created_at, expires_at)
        )
        conn.commit()
        conn.close()
        return agent_token, customer_token
   
    def agent_deposit_parcel(self, qr_token: str, locker_id: str) -> dict:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM deliveries WHERE agent_qr=?", (qr_token,))
            delivery = cursor.fetchone()
            if not delivery:
                return {'success': False, 'message': 'Invalid QR code'}
            
            delivery_id = delivery[0]
            delivery_locker_id = delivery[3]  # locker_id
            delivery_status = delivery[6]     # status
            expires_at = delivery[11]         # expires_at
            
            if delivery_locker_id != locker_id:
                return {'success': False, 'message': 'Wrong locker for this delivery'}
            if delivery_status != 'pending_delivery':
                return {'success': False, 'message': 'Delivery already processed'}
            # Check if delivery has expired
            if expires_at:
                try:
                    expiry_date = datetime.fromisoformat(expires_at)
                    if datetime.now() > expiry_date:
                        return {'success': False, 'message': 'Delivery expired'}
                except (ValueError, TypeError):
                    # If expires_at is not in the expected format, ignore expiry check
                    pass
                
            # Check if locker is available (no active deliveries)
            cursor.execute("""
                SELECT COUNT(*) FROM deliveries 
                WHERE locker_id=? AND status IN ('deposited', 'ready_for_pickup')
            """, (locker_id,))
            if cursor.fetchone()[0] > 0:
                return {'success': False, 'message': 'Locker is currently occupied'}
            
            # Open locker for deposit
            cursor.execute("UPDATE lockers SET status='depositing', last_used=? WHERE locker_id=?", 
                         (datetime.now().isoformat(), locker_id))
            cursor.execute("UPDATE deliveries SET status='deposited', deposited_at=? WHERE delivery_id=?", 
                         (datetime.now().isoformat(), delivery_id))
            
            SecureLocker.log_access(locker_id, delivery_id, 'agent', qr_token, 'agent_deposit', cursor=cursor)
            conn.commit()
            
            return {
                'success': True,
                'message': 'Locker opened for deposit',
                'locker_id': locker_id,
                'delivery_id': delivery_id
            }
        finally:
            conn.close()
    
    def close_locker_after_deposit(self, locker_id: str) -> dict:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM lockers WHERE locker_id=?", (locker_id,))
        locker_status = cursor.fetchone()
        if not locker_status:
            conn.close()
            return {'success': False, 'message': 'Locker not found'}
            
        # Update locker status to occupied (not available for new deliveries)
        cursor.execute("UPDATE lockers SET status='occupied' WHERE locker_id=?", (locker_id,))
        cursor.execute("UPDATE deliveries SET status='ready_for_pickup' WHERE locker_id=? AND status='deposited'", (locker_id,))
        
        # Update locker usage statistics
        cursor.execute("UPDATE lockers SET total_deliveries = total_deliveries + 1 WHERE locker_id=?", (locker_id,))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Locker secured and ready for customer pickup'}
    
    def customer_pickup_parcel(self, qr_token: str, locker_id: str) -> dict:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM deliveries WHERE customer_qr=?", (qr_token,))
            delivery = cursor.fetchone()
            if not delivery:
                return {'success': False, 'message': 'Invalid QR code'}
            delivery_id = delivery[0]
            if delivery[3] != locker_id:  # locker_id is at index 3
                return {'success': False, 'message': 'Wrong locker for this delivery'}
            if delivery[6] != 'ready_for_pickup':  # status is at index 6
                return {'success': False, 'message': 'Parcel not ready for pickup'}
            # Open locker for pickup
            cursor.execute("UPDATE lockers SET status='pickup' WHERE locker_id=?", (locker_id,))
            cursor.execute("UPDATE deliveries SET status='picked_up', picked_up_at=? WHERE delivery_id=?", (datetime.now().isoformat(), delivery_id))
            SecureLocker.log_access(locker_id, delivery_id, 'customer', qr_token, 'customer_pickup', cursor=cursor)
            conn.commit()
            return {
                'success': True,
                'message': 'Locker opened for pickup',
                'locker_id': locker_id,
                'delivery_id': delivery_id
            }
        finally:
            conn.close()
    
    def close_locker_after_pickup(self, locker_id: str) -> dict:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM lockers WHERE locker_id=?", (locker_id,))
        locker_status = cursor.fetchone()
        if not locker_status:
            conn.close()
            return {'success': False, 'message': 'Locker not found'}
            
        # Make locker available for new deliveries
        cursor.execute("UPDATE lockers SET status='available', last_used=? WHERE locker_id=?", 
                     (datetime.now().isoformat(), locker_id))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Locker reset and ready for next delivery'}

    def reset_locker_state(self, locker_id: str):
        """Utility: Reset a locker to available and clear active/pending deliveries (demo-friendly)."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Ensure locker exists; if not, create as available with placeholder address
            cursor.execute("SELECT locker_id FROM lockers WHERE locker_id=?", (locker_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO lockers (locker_id, address, status) VALUES (?, ?, 'available')",
                               (locker_id, f'Auto-added {locker_id}'))
            # Reset locker status
            cursor.execute("UPDATE lockers SET status='available' WHERE locker_id=?", (locker_id,))
            # Remove any active/pending deliveries for this locker
            cursor.execute("DELETE FROM deliveries WHERE locker_id=? AND status IN ('pending_delivery','deposited','ready_for_pickup')",
                           (locker_id,))
            conn.commit()
        finally:
            conn.close()

    def reset_demo_lockers(self, locker_ids):
        for lid in locker_ids:
            self.reset_locker_state(lid)

    def get_locker_status(self, locker_id: str) -> dict:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT locker_id, address, status, total_deliveries, last_used 
            FROM lockers WHERE locker_id=?
        """, (locker_id,))
        locker = cursor.fetchone()
        
        if not locker:
            conn.close()
            return {'error': 'Locker not found'}
            
        status = {
            'locker_id': locker[0],
            'location': locker[1],
            'is_locked': locker[2] in ('available', 'occupied'),
            'has_parcel': False,
            'current_delivery': None,
            'total_deliveries': locker[3] or 0,
            'last_used': locker[4]
        }
        
        # Check for active deliveries
        cursor.execute("""
            SELECT delivery_id, customer_phone, status, priority, package_size, created_at
            FROM deliveries 
            WHERE locker_id=? AND status IN ('deposited', 'ready_for_pickup')
            ORDER BY created_at DESC LIMIT 1
        """, (locker_id,))
        
        delivery = cursor.fetchone()
        if delivery:
            status['has_parcel'] = True
            status['current_delivery'] = delivery[0]
            status['delivery_status'] = delivery[2]
            status['customer_phone'] = delivery[1][-4:] if delivery[1] else 'N/A'
            status['priority'] = delivery[3]
            status['package_size'] = delivery[4]
            status['delivery_created'] = delivery[5]
            
        conn.close()
        return status
    
    def generate_qr_image(self, token: str) -> str:
        """Generate QR code image as base64 string"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(token)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str

    def get_all_lockers(self) -> list:
        """Get status of all lockers"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT locker_id FROM lockers ORDER BY locker_id")
        locker_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [self.get_locker_status(locker_id) for locker_id in locker_ids]

    def get_available_lockers(self) -> list:
        """Get only available lockers for new deliveries"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get all lockers
        cursor.execute("SELECT locker_id FROM lockers ORDER BY locker_id")
        all_locker_ids = [row[0] for row in cursor.fetchall()]
        
        # Get lockers that have active deliveries (pending, deposited, or ready for pickup)
        cursor.execute("""
            SELECT DISTINCT locker_id, status FROM deliveries 
            WHERE status IN ('pending_delivery', 'deposited', 'ready_for_pickup')
        """)
        occupied_data = cursor.fetchall()
        occupied_locker_ids = set(row[0] for row in occupied_data)
        
        conn.close()
        
        # Return only lockers that are not occupied
        available_lockers = []
        for locker_id in all_locker_ids:
            if locker_id not in occupied_locker_ids:
                locker_status = self.get_locker_status(locker_id)
                available_lockers.append(locker_status)
        
        return available_lockers

    def get_dashboard_data(self) -> tuple:
        """Get comprehensive dashboard data"""
        lockers = self.get_all_lockers()
        
        available_count = sum(1 for l in lockers if not l.get('has_parcel'))
        occupied_count = sum(1 for l in lockers if l.get('has_parcel'))
        
        stats = {
            'total': len(lockers),
            'available': available_count,
            'occupied': occupied_count,
            'utilization_rate': round((occupied_count / len(lockers)) * 100, 1) if lockers else 0
        }
        
        return lockers, stats

    def get_delivery_analytics(self) -> dict:
        """Get comprehensive delivery analytics"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Today's deliveries
        today = datetime.now().date()
        cursor.execute("""
            SELECT COUNT(*) FROM deliveries 
            WHERE DATE(created_at) = ?
        """, (today,))
        today_deliveries = cursor.fetchone()[0]
        
        # Completed deliveries (picked up)
        cursor.execute("""
            SELECT COUNT(*) FROM deliveries 
            WHERE status = 'picked_up'
        """)
        completed = cursor.fetchone()[0]
        
        # Pending deliveries (deposited or ready for pickup)
        cursor.execute("""
            SELECT COUNT(*) FROM deliveries 
            WHERE status IN ('deposited', 'ready_for_pickup')
        """)
        pending = cursor.fetchone()[0]
        
        # Success rate calculation
        cursor.execute("""
            SELECT COUNT(*) FROM deliveries 
            WHERE status IN ('picked_up', 'deposited', 'ready_for_pickup')
        """)
        total_processed = cursor.fetchone()[0]
        
        success_rate = round((completed / total_processed) * 100, 1) if total_processed > 0 else 100
        
        # Average delivery time (from deposit to pickup)
        cursor.execute("""
            SELECT AVG(
                (julianday(picked_up_at) - julianday(deposited_at)) * 24
            ) as avg_hours
            FROM deliveries 
            WHERE picked_up_at IS NOT NULL AND deposited_at IS NOT NULL
        """)
        avg_delivery_time = cursor.fetchone()[0]
        avg_delivery_hours = round(avg_delivery_time, 1) if avg_delivery_time else 0
        
        # Weekly delivery counts
        cursor.execute("""
            SELECT 
                strftime('%w', created_at) as day_of_week,
                COUNT(*) as count
            FROM deliveries 
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY strftime('%w', created_at)
            ORDER BY day_of_week
        """)
        weekly_data = cursor.fetchall()
        
        # Peak hours analysis
        cursor.execute("""
            SELECT 
                strftime('%H', created_at) as hour,
                COUNT(*) as count
            FROM deliveries 
            WHERE created_at >= datetime('now', '-30 days')
            GROUP BY strftime('%H', created_at)
            ORDER BY count DESC
            LIMIT 1
        """)
        peak_hour_data = cursor.fetchone()
        peak_hours = f"{peak_hour_data[0]}:00-{int(peak_hour_data[0])+1}:00" if peak_hour_data else "N/A"
        
        # Customer satisfaction (simulated based on successful deliveries)
        customer_satisfaction = min(95 + (success_rate * 0.05), 99.9)
        
        conn.close()
        
        return {
            'today_deliveries': today_deliveries,
            'completed': completed,
            'pending': pending,
            'success_rate': success_rate,
            'avg_delivery_hours': avg_delivery_hours,
            'peak_hours': peak_hours,
            'customer_satisfaction': round(customer_satisfaction, 1),
            'weekly_data': dict(weekly_data) if weekly_data else {},
            'total_processed': total_processed
        }

    def get_recent_activity(self, limit: int = 10) -> list:
        """Get recent system activity"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                al.locker_id,
                al.delivery_id,
                al.role,
                al.action,
                al.timestamp,
                d.customer_phone
            FROM access_logs al
            LEFT JOIN deliveries d ON al.delivery_id = d.delivery_id
            ORDER BY al.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'locker_id': row[0],
                'delivery_id': row[1],
                'role': row[2],
                'action': row[3],
                'timestamp': row[4],
                'customer_phone': row[5][-4:] if row[5] else 'N/A'
            })
        
        conn.close()
        return activities


# Demo usage and testing
def demo():
    """Demonstrate the locker system workflow"""
    print("=== Secure Locker System Demo ===\n")
    
    # Initialize system
    system = DeliverySystem()
    
    # Add lockers
    system.add_locker("LOC001", "123 Main St, Apt Building A")
    system.add_locker("LOC002", "456 Oak Ave, Residential Complex B")
    
    print("1. Lockers added to system")
    
    # Ecommerce creates delivery
    delivery_id = "DEL12345"
    customer_phone = "+1234567890"
    locker_id = "LOC001"
    
    agent_qr, customer_qr = system.generate_delivery_qr(delivery_id, customer_phone, locker_id)
    
    print(f"2. QR codes generated:")
    print(f"   Agent QR: {agent_qr[:20]}...")
    print(f"   Customer QR: {customer_qr[:20]}...")
    
    # Check locker status
    print(f"\n3. Initial locker status:")
    print(json.dumps(system.get_locker_status(locker_id), indent=2))
    
    # Agent deposits parcel
    print(f"\n4. Agent scans QR to deposit parcel:")
    result = system.agent_deposit_parcel(agent_qr, locker_id)
    print(json.dumps(result, indent=2))
    
    # Agent closes locker
    print(f"\n5. Agent closes locker after deposit:")
    result = system.close_locker_after_deposit(locker_id)
    print(json.dumps(result, indent=2))
    
    # Check locker status after deposit
    print(f"\n6. Locker status after deposit:")
    print(json.dumps(system.get_locker_status(locker_id), indent=2))
    
    # Customer picks up parcel
    print(f"\n7. Customer scans QR to pickup parcel:")
    result = system.customer_pickup_parcel(customer_qr, locker_id)
    print(json.dumps(result, indent=2))
    
    # Customer closes locker
    print(f"\n8. Customer closes locker after pickup:")
    result = system.close_locker_after_pickup(locker_id)
    print(json.dumps(result, indent=2))
    
    # Final locker status
    print(f"\n9. Final locker status:")
    print(json.dumps(system.get_locker_status(locker_id), indent=2))


if __name__ == "__main__":
    demo()