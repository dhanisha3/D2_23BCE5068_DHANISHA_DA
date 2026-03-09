#!/usr/bin/env python3
"""
Demo script to showcase the complete locker system workflow
"""

import time
import webbrowser
import subprocess
import sys
from threading import Thread
from main import DeliverySystem

def run_web_app():
    """Run the web application in a separate thread"""
    subprocess.run([sys.executable, 'web_app.py'])

def demo_workflow():
    """Demonstrate the system with sample data"""
    print("=== Secure Locker System Demo ===\n")
    
    # Initialize system
    system = DeliverySystem()
    
    # Ensure clean demo state and add demo lockers
    demo_lockers = ["LOC001", "LOC002", "LOC003"]
    for lid in demo_lockers:
        system.reset_locker_state(lid)
    system.add_locker("LOC001", "123 Main St, Building A")
    system.add_locker("LOC002", "456 Oak Ave, Complex B")
    system.add_locker("LOC003", "789 Pine Rd, Residential Area")
    
    print("✅ Demo lockers created")
    
    # Create a sample delivery
    from datetime import datetime
    delivery_id = "DEMO" + datetime.now().strftime("%Y%m%d%H%M%S")
    customer_phone = "+1234567890"
    locker_id = "LOC001"
    agent_qr, customer_qr = system.generate_delivery_qr(delivery_id, customer_phone, locker_id)
    
    print(f"✅ Sample delivery created:")
    print(f"   Delivery ID: {delivery_id}")
    print(f"   Customer: {customer_phone}")
    print(f"   Locker: {locker_id}")
    print(f"   Agent QR: {agent_qr}")
    print(f"   Customer QR: {customer_qr}")
    
    print(f"\n🌐 Web interface will open at: http://localhost:5001")
    print(f"\n📋 Demo Instructions:")
    print(f"1. Go to Ecommerce portal to create new deliveries")
    print(f"2. Use Agent portal with this QR: {agent_qr}")
    print(f"3. Use Customer portal with this QR: {customer_qr}")
    print(f"4. Monitor everything on the Dashboard")
    
    return agent_qr, customer_qr

if __name__ == "__main__":
    print("🚀 Starting Secure Locker System Demo...\n")
    
    # Create demo data
    agent_qr, customer_qr = demo_workflow()
    
    print(f"\n⏳ Starting web server...")
    
    # Start web app in background
    web_thread = Thread(target=run_web_app, daemon=True)
    web_thread.start()
    
    # Wait a moment for server to start
    time.sleep(3)
    
    # Open browser
    try:
        webbrowser.open('http://localhost:5001')
        print(f"✅ Web browser opened")
    except:
        print(f"❌ Could not open browser automatically")
        print(f"   Please visit: http://localhost:5001")
    
    print(f"\n🎯 Quick Test Tokens:")
    print(f"   Agent QR Token: {agent_qr}")
    print(f"   Customer QR Token: {customer_qr}")
    print(f"\n📝 Copy these tokens to test the agent and customer portals")
    print(f"\n⚡ Press Ctrl+C to stop the demo")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n👋 Demo stopped. Thanks for trying the Secure Locker System!")