#!/usr/bin/env python3
"""
Test script for the Secure Locker System
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_complete_workflow():
    """Test the complete delivery workflow"""
    print("=== Testing Complete Locker System Workflow ===\n")
    
    # 1. Create a delivery
    print("1. Creating delivery...")
    delivery_data = {
        "delivery_id": "TEST001",
        "customer_phone": "+1234567890",
        "locker_id": "LOC001"
    }
    
    response = requests.post(f"{BASE_URL}/delivery/create", json=delivery_data)
    if response.status_code == 200:
        delivery_result = response.json()
        print(f"   ✓ Delivery created successfully")
        print(f"   Agent QR: {delivery_result['agent_qr_token'][:20]}...")
        print(f"   Customer QR: {delivery_result['customer_qr_token'][:20]}...")
        
        agent_qr = delivery_result['agent_qr_token']
        customer_qr = delivery_result['customer_qr_token']
        locker_id = delivery_result['locker_id']
    else:
        print(f"   ✗ Failed to create delivery: {response.text}")
        return
    
    # 2. Check initial locker status
    print(f"\n2. Checking locker status...")
    response = requests.get(f"{BASE_URL}/locker/{locker_id}/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   ✓ Locker status: {json.dumps(status, indent=4)}")
    
    # 3. Agent deposits parcel
    print(f"\n3. Agent depositing parcel...")
    deposit_data = {"qr_token": agent_qr}
    response = requests.post(f"{BASE_URL}/locker/{locker_id}/deposit", json=deposit_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ Deposit failed: {response.text}")
        return
    
    # 4. Close locker after deposit
    print(f"\n4. Closing locker after deposit...")
    response = requests.post(f"{BASE_URL}/locker/{locker_id}/close-deposit")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ {result['message']}")
    
    # 5. Check locker status after deposit
    print(f"\n5. Checking locker status after deposit...")
    response = requests.get(f"{BASE_URL}/locker/{locker_id}/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   ✓ Locker status: {json.dumps(status, indent=4)}")
    
    # 6. Customer picks up parcel
    print(f"\n6. Customer picking up parcel...")
    pickup_data = {"qr_token": customer_qr}
    response = requests.post(f"{BASE_URL}/locker/{locker_id}/pickup", json=pickup_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ Pickup failed: {response.text}")
        return
    
    # 7. Close locker after pickup
    print(f"\n7. Closing locker after pickup...")
    response = requests.post(f"{BASE_URL}/locker/{locker_id}/close-pickup")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ {result['message']}")
    
    # 8. Final locker status
    print(f"\n8. Final locker status...")
    response = requests.get(f"{BASE_URL}/locker/{locker_id}/status")
    if response.status_code == 200:
        status = response.json()
        print(f"   ✓ Final status: {json.dumps(status, indent=4)}")
    
    print(f"\n=== Workflow Complete ===")

def test_security_scenarios():
    """Test security scenarios"""
    print("\n=== Testing Security Scenarios ===\n")
    
    # Test invalid QR codes
    print("1. Testing invalid QR code...")
    invalid_data = {"qr_token": "invalid-token-123"}
    response = requests.post(f"{BASE_URL}/locker/LOC001/deposit", json=invalid_data)
    if response.status_code == 400:
        print(f"   ✓ Invalid QR rejected: {response.json()['message']}")
    
    # Test wrong locker
    print("\n2. Testing wrong locker access...")
    # This would need a valid QR for a different locker
    print("   (Would test with valid QR for different locker)")

if __name__ == "__main__":
    print("Make sure the API server is running (python api_server.py)")
    print("Press Enter to start tests...")
    input()
    
    try:
        test_complete_workflow()
        test_security_scenarios()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"Test error: {e}")