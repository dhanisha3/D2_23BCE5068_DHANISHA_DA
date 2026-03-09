#!/usr/bin/env python3
"""
REST API Server for Secure Locker System
Simple Flask-based API for locker operations
"""

from flask import Flask, request, jsonify
from main import DeliverySystem
import json

app = Flask(__name__)
system = DeliverySystem()

# Initialize with some demo lockers
system.add_locker("LOC001", "123 Main St, Building A")
system.add_locker("LOC002", "456 Oak Ave, Complex B")

@app.route('/api/lockers', methods=['POST'])
def add_locker():
    """Add a new locker"""
    data = request.get_json()
    locker_id = data.get('locker_id')
    location = data.get('location')
    
    if not locker_id or not location:
        return jsonify({'error': 'locker_id and location required'}), 400
    
    try:
        result = system.add_locker(locker_id, location)
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delivery/create', methods=['POST'])
def create_delivery():
    """Create new delivery and generate QR codes"""
    data = request.get_json()
    delivery_id = data.get('delivery_id')
    customer_phone = data.get('customer_phone')
    locker_id = data.get('locker_id')
    
    if not all([delivery_id, customer_phone, locker_id]):
        return jsonify({'error': 'delivery_id, customer_phone, and locker_id required'}), 400
    
    try:
        agent_qr, customer_qr = system.generate_delivery_qr(delivery_id, customer_phone, locker_id)
        
        return jsonify({
            'success': True,
            'delivery_id': delivery_id,
            'agent_qr_token': agent_qr,
            'customer_qr_token': customer_qr,
            'locker_id': locker_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/locker/<locker_id>/deposit', methods=['POST'])
def agent_deposit(locker_id):
    """Agent deposits parcel using QR code"""
    data = request.get_json()
    qr_token = data.get('qr_token')
    
    if not qr_token:
        return jsonify({'error': 'qr_token required'}), 400
    
    result = system.agent_deposit_parcel(qr_token, locker_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/locker/<locker_id>/close-deposit', methods=['POST'])
def close_after_deposit(locker_id):
    """Close locker after agent deposit"""
    result = system.close_locker_after_deposit(locker_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/locker/<locker_id>/pickup', methods=['POST'])
def customer_pickup(locker_id):
    """Customer picks up parcel using QR code"""
    data = request.get_json()
    qr_token = data.get('qr_token')
    
    if not qr_token:
        return jsonify({'error': 'qr_token required'}), 400
    
    result = system.customer_pickup_parcel(qr_token, locker_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/locker/<locker_id>/close-pickup', methods=['POST'])
def close_after_pickup(locker_id):
    """Close locker after customer pickup"""
    result = system.close_locker_after_pickup(locker_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/locker/<locker_id>/status', methods=['GET'])
def get_locker_status(locker_id):
    """Get locker status"""
    status = system.get_locker_status(locker_id)
    
    if 'error' in status:
        return jsonify(status), 404
    
    return jsonify(status)

@app.route('/api/lockers', methods=['GET'])
def list_lockers():
    """List all lockers"""
    from db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT locker_id FROM lockers")
    locker_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    lockers = [system.get_locker_status(locker_id) for locker_id in locker_ids]
    return jsonify({'lockers': lockers})

if __name__ == '__main__':
    print("Starting Secure Locker API Server...")
    print("Available endpoints:")
    print("  POST /api/delivery/create - Create delivery and get QR codes")
    print("  POST /api/locker/<id>/deposit - Agent deposit parcel")
    print("  POST /api/locker/<id>/close-deposit - Close after deposit")
    print("  POST /api/locker/<id>/pickup - Customer pickup parcel")
    print("  POST /api/locker/<id>/close-pickup - Close after pickup")
    print("  GET  /api/locker/<id>/status - Get locker status")
    print("  GET  /api/lockers - List all lockers")
    
    app.run(debug=True, host='0.0.0.0', port=5000)