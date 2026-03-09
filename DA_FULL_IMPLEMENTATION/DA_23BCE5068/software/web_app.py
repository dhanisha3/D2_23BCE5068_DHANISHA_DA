#!/usr/bin/env python3
"""
Web UI for Secure Locker System
Flask web application with HTML interface
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from main import DeliverySystem
import uuid
from datetime import datetime, timedelta
import json

app = Flask(__name__)
import os
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Initialize the delivery system
system = DeliverySystem()

# Initialize dynamic lockers - these will be created as needed
def ensure_demo_lockers():
    """Ensure we have some demo lockers for testing"""
    demo_lockers = [
        ("LOC001", "123 Main St, Building A"),
        ("LOC002", "456 Oak Ave, Complex B"), 
        ("LOC003", "789 Pine Rd, Residential Area"),
        ("LOC004", "321 Elm St, Shopping Center"),
        ("LOC005", "654 Maple Ave, Office Complex")
    ]
    
    for locker_id, location in demo_lockers:
        try:
            system.add_locker(locker_id, location)
        except:
            pass  # Locker already exists

ensure_demo_lockers()

@app.route('/')
def index():
    """Dashboard showing all lockers and system status"""
    lockers, stats = system.get_dashboard_data()
    return render_template('index.html', lockers=lockers, stats=stats)

@app.route('/ecommerce', methods=['GET', 'POST'])
def ecommerce():
    """Ecommerce portal for creating deliveries"""
    available_lockers = system.get_available_lockers()
    stats = system.get_delivery_analytics()
    if request.method == 'POST':
        delivery_id = request.form.get('delivery_id')
        customer_phone = request.form.get('customer_phone')
        customer_email = request.form.get('customer_email', '')
        locker_id = request.form.get('locker_id')
        package_size = request.form.get('package_size', 'medium')
        priority = request.form.get('priority', 'standard')
        delivery_notes = request.form.get('delivery_notes', '')
        
        # Use clean phone number if provided
        clean_phone = request.form.get('clean_phone', '')
        if clean_phone:
            customer_phone = clean_phone
        
        # Validate phone number
        if customer_phone:
            # Remove any formatting characters
            phone_digits = ''.join(filter(str.isdigit, customer_phone))
            
            if len(phone_digits) != 10:
                return render_template('ecommerce.html',
                                     available_lockers=available_lockers,
                                     stats=stats,
                                     success=False,
                                     message="Phone number must be exactly 10 digits")
            
            if not phone_digits.startswith(('6', '7', '8', '9')):
                return render_template('ecommerce.html',
                                     available_lockers=available_lockers,
                                     stats=stats,
                                     success=False,
                                     message="Phone number must start with 6, 7, 8, or 9")
            
            # Use the cleaned phone number
            customer_phone = phone_digits
        
        try:
            agent_qr, customer_qr = system.generate_delivery_qr(
                delivery_id, customer_phone, locker_id, 
                customer_email, package_size, priority, delivery_notes
            )
            agent_qr_image = system.generate_qr_image(agent_qr)
            customer_qr_image = system.generate_qr_image(customer_qr)
            return render_template('ecommerce.html',
                                 available_lockers=available_lockers,
                                 stats=stats,
                                 success=True,
                                 message="Delivery created successfully!",
                                 qr_codes=True,
                                 delivery_id=delivery_id,
                                 locker_id=locker_id,
                                 agent_qr_token=agent_qr,
                                 customer_qr_token=customer_qr,
                                 agent_qr_image=agent_qr_image,
                                 customer_qr_image=customer_qr_image)
        except ValueError as e:
            # Handle specific validation errors (like locker already occupied)
            return render_template('ecommerce.html',
                                 available_lockers=available_lockers,
                                 stats=stats,
                                 success=False,
                                 message=str(e))
        except Exception as e:
            # Handle other unexpected errors
            return render_template('ecommerce.html',
                                 available_lockers=available_lockers,
                                 stats=stats,
                                 success=False,
                                 message=f"Error creating delivery: {str(e)}")
    return render_template('ecommerce.html', available_lockers=available_lockers, stats=stats)

@app.route('/agent', methods=['GET', 'POST'])
def agent():
    """Delivery agent portal"""
    lockers = system.get_all_lockers()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'deposit':
            qr_token = request.form.get('qr_token')
            locker_id = request.form.get('locker_id')
            result = system.agent_deposit_parcel(qr_token, locker_id)
            if result['success']:
                return render_template('agent.html',
                                     lockers=lockers,
                                     success=True,
                                     message=result['message'],
                                     step='deposit_success',
                                     locker_id=locker_id,
                                     delivery_id=result['delivery_id'])
            else:
                return render_template('agent.html',
                                     lockers=lockers,
                                     success=False,
                                     message=result['message'])
        elif action == 'close_deposit':
            locker_id = request.form.get('locker_id')
            result = system.close_locker_after_deposit(locker_id)
            return render_template('agent.html',
                                 lockers=lockers,
                                 success=result['success'],
                                 message=result['message'],
                                 step='deposit_complete',
                                 locker_id=locker_id)
    return render_template('agent.html', lockers=lockers)

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    """Customer portal for pickup"""
    lockers = system.get_all_lockers()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'pickup':
            qr_token = request.form.get('qr_token')
            locker_id = request.form.get('locker_id')
            result = system.customer_pickup_parcel(qr_token, locker_id)
            if result['success']:
                return render_template('customer.html',
                                     lockers=lockers,
                                     success=True,
                                     message=result['message'],
                                     step='pickup_success',
                                     locker_id=locker_id,
                                     delivery_id=result['delivery_id'])
            else:
                return render_template('customer.html',
                                     lockers=lockers,
                                     success=False,
                                     message=result['message'])
        elif action == 'close_pickup':
            locker_id = request.form.get('locker_id')
            result = system.close_locker_after_pickup(locker_id)
            return render_template('customer.html',
                                 lockers=lockers,
                                 success=result['success'],
                                 message=result['message'],
                                 step='pickup_complete',
                                 locker_id=locker_id)
    return render_template('customer.html', lockers=lockers)

@app.route('/api/analytics')
def api_analytics():
    """API endpoint for real-time analytics"""
    return jsonify(system.get_delivery_analytics())

@app.route('/api/lockers')
def api_lockers():
    """API endpoint for locker status"""
    return jsonify(system.get_all_lockers())

@app.route('/api/add_locker', methods=['POST'])
def api_add_locker():
    """API endpoint to add new locker"""
    data = request.get_json()
    try:
        result = system.add_locker(data['locker_id'], data['location'])
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/reset_locker/<locker_id>', methods=['POST'])
def api_reset_locker(locker_id):
    """API endpoint to reset locker state"""
    try:
        system.reset_locker_state(locker_id)
        return jsonify({'success': True, 'message': f'Locker {locker_id} reset successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/reset_all_lockers', methods=['POST'])
def api_reset_all_lockers():
    """API endpoint to reset all locker states"""
    try:
        from db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get all locker IDs
        cursor.execute("SELECT locker_id FROM lockers")
        locker_ids = [row[0] for row in cursor.fetchall()]
        
        # Reset all lockers
        for locker_id in locker_ids:
            system.reset_locker_state(locker_id)
        
        conn.close()
        return jsonify({'success': True, 'message': f'Reset {len(locker_ids)} lockers successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

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
    
    app.run(debug=True, host='0.0.0.0', port=5001)