#!/usr/bin/env python3
"""
Initialize the Secure Locker System with dynamic data
"""

from main import DeliverySystem
from datetime import datetime, timedelta
import random

def init_system():
    """Initialize system with sample data"""
    print("Initializing Secure Locker System...")
    
    system = DeliverySystem()
    
    # Add diverse lockers
    lockers = [
        ("LOC001", "123 Main St, Building A"),
        ("LOC002", "456 Oak Ave, Complex B"), 
        ("LOC003", "789 Pine Rd, Residential Area"),
        ("LOC004", "321 Elm St, Shopping Center"),
        ("LOC005", "654 Maple Ave, Office Complex"),
        ("LOC006", "987 Cedar Blvd, University Campus"),
        ("LOC007", "147 Birch Lane, Hospital District"),
        ("LOC008", "258 Spruce Ave, Metro Station")
    ]
    
    for locker_id, location in lockers:
        try:
            result = system.add_locker(locker_id, location)
            print(f"✓ {result}")
        except Exception as e:
            print(f"⚠ Locker {locker_id} already exists")
    
    # Create some sample deliveries for demonstration
    sample_deliveries = [
        {
            'delivery_id': 'DEL001',
            'customer_phone': '+1234567890',
            'customer_email': 'customer1@example.com',
            'locker_id': 'LOC001',
            'package_size': 'medium',
            'priority': 'standard',
            'notes': 'Fragile - Handle with care'
        },
        {
            'delivery_id': 'DEL002', 
            'customer_phone': '+1234567891',
            'customer_email': 'customer2@example.com',
            'locker_id': 'LOC003',
            'package_size': 'large',
            'priority': 'express',
            'notes': 'Birthday gift - urgent delivery'
        }
    ]
    
    print("\nCreating sample deliveries...")
    for delivery in sample_deliveries:
        try:
            agent_qr, customer_qr = system.generate_delivery_qr(
                delivery['delivery_id'],
                delivery['customer_phone'],
                delivery['locker_id'],
                delivery['customer_email'],
                delivery['package_size'],
                delivery['priority'],
                delivery['notes']
            )
            print(f"✓ Created delivery {delivery['delivery_id']}")
            print(f"  Agent QR: {agent_qr[:20]}...")
            print(f"  Customer QR: {customer_qr[:20]}...")
        except Exception as e:
            print(f"⚠ Error creating delivery {delivery['delivery_id']}: {e}")
    
    print("\n" + "="*50)
    print("System initialized successfully!")
    print("Available endpoints:")
    print("  Dashboard: http://localhost:5001/")
    print("  Ecommerce: http://localhost:5001/ecommerce")
    print("  Agent: http://localhost:5001/agent")
    print("  Customer: http://localhost:5001/customer")
    print("  Analytics API: http://localhost:5001/api/analytics")
    print("="*50)

if __name__ == "__main__":
    init_system()