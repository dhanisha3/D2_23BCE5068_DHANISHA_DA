#!/usr/bin/env python3
"""
Web UI for Secure Locker System
Flask web application with HTML interface

This serves the frontend templates with sample/mock data for demonstration.

TODO (Phase 2):
- Connect to real database backend via DeliverySystem
- Implement QR code generation and display
- Implement real-time analytics from database
- Implement agent deposit workflow  
- Implement customer pickup workflow
- Add API endpoints for AJAX calls
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# ============================================================
# Mock data for frontend demonstration (Phase 1 - UI Only)
# TODO: Phase 2 - Replace with real DeliverySystem backend
# ============================================================

MOCK_LOCKERS = [
    {'locker_id': 'LOC001', 'location': '123 Main St, Building A', 'is_locked': True, 'has_parcel': False, 
     'current_delivery': None, 'total_deliveries': 0, 'last_used': None},
    {'locker_id': 'LOC002', 'location': '456 Oak Ave, Complex B', 'is_locked': True, 'has_parcel': True, 
     'current_delivery': 'DEL001', 'total_deliveries': 3, 'last_used': '2026-03-07', 'delivery_status': 'ready_for_pickup',
     'customer_phone': '7890', 'priority': 'standard', 'package_size': 'medium'},
    {'locker_id': 'LOC003', 'location': '789 Pine Rd, Residential Area', 'is_locked': True, 'has_parcel': False, 
     'current_delivery': None, 'total_deliveries': 1, 'last_used': '2026-03-06'},
    {'locker_id': 'LOC004', 'location': '321 Elm St, Shopping Center', 'is_locked': True, 'has_parcel': False, 
     'current_delivery': None, 'total_deliveries': 0, 'last_used': None},
    {'locker_id': 'LOC005', 'location': '654 Maple Ave, Office Complex', 'is_locked': True, 'has_parcel': True, 
     'current_delivery': 'DEL002', 'total_deliveries': 5, 'last_used': '2026-03-07', 'delivery_status': 'deposited',
     'customer_phone': '4321', 'priority': 'express', 'package_size': 'large'},
]

MOCK_STATS = {
    'total': 5,
    'available': 3,
    'occupied': 2,
    'utilization_rate': 40.0
}

MOCK_ANALYTICS = {
    'today_deliveries': 2,
    'completed': 8,
    'pending': 2,
    'success_rate': 80.0,
    'avg_delivery_hours': 4.5,
    'peak_hours': '14:00-15:00',
    'customer_satisfaction': 96.5,
    'weekly_data': {},
    'total_processed': 10
}


@app.route('/')
def index():
    """Dashboard showing all lockers and system status"""
    return render_template('index.html', lockers=MOCK_LOCKERS, stats=MOCK_STATS)

@app.route('/ecommerce', methods=['GET', 'POST'])
def ecommerce():
    """Ecommerce portal for creating deliveries"""
    available_lockers = [l for l in MOCK_LOCKERS if not l.get('has_parcel')]
    
    if request.method == 'POST':
        # TODO: Phase 2 - Implement actual delivery creation with QR code generation
        delivery_id = request.form.get('delivery_id')
        customer_phone = request.form.get('customer_phone')
        locker_id = request.form.get('locker_id')
        
        return render_template('ecommerce.html',
                             available_lockers=available_lockers,
                             stats=MOCK_ANALYTICS,
                             success=False,
                             message="Backend not yet implemented. QR code generation coming in Phase 2.")
    
    return render_template('ecommerce.html', available_lockers=available_lockers, stats=MOCK_ANALYTICS)

@app.route('/agent', methods=['GET', 'POST'])
def agent():
    """Delivery agent portal"""
    if request.method == 'POST':
        # TODO: Phase 2 - Implement agent deposit workflow
        return render_template('agent.html',
                             lockers=MOCK_LOCKERS,
                             success=False,
                             message="Backend not yet implemented. Agent deposit coming in Phase 2.")
    return render_template('agent.html', lockers=MOCK_LOCKERS)

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    """Customer portal for pickup"""
    if request.method == 'POST':
        # TODO: Phase 2 - Implement customer pickup workflow
        return render_template('customer.html',
                             lockers=MOCK_LOCKERS,
                             success=False,
                             message="Backend not yet implemented. Customer pickup coming in Phase 2.")
    return render_template('customer.html', lockers=MOCK_LOCKERS)

@app.route('/api/analytics')
def api_analytics():
    """API endpoint for real-time analytics
    
    TODO (Phase 2): Return real analytics from database
    """
    return jsonify(MOCK_ANALYTICS)

@app.route('/api/lockers')
def api_lockers():
    """API endpoint for locker status
    
    TODO (Phase 2): Return real locker data from database
    """
    return jsonify(MOCK_LOCKERS)

@app.errorhandler(404)
def not_found(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html'), 500

if __name__ == '__main__':
    print("Starting Secure Locker Web Application...")
    print("Available at: http://localhost:5001")
    print("\nPortals:")
    print("  Dashboard: http://localhost:5001/")
    print("  Ecommerce: http://localhost:5001/ecommerce")
    print("  Agent: http://localhost:5001/agent")
    print("  Customer: http://localhost:5001/customer")
    print("\nNOTE: Running in frontend-only mode (Phase 1)")
    print("Backend integration planned for Phase 2")
    
    app.run(debug=True, host='0.0.0.0', port=5001)