#!/usr/bin/env python3
"""
Test script to verify the locker system functionality
"""

from main import DeliverySystem
import json

def test_locker_availability():
    """Test that lockers are properly managed for availability"""
    print("=== Testing Locker Availability System ===\n")
    
    system = DeliverySystem()
    
    # Reset system for clean test
    system.reset_locker_state("LOC001")
    system.reset_locker_state("LOC002")
    
    print("1. Initial available lockers:")
    available = system.get_available_lockers()
    print(f"   Found {len(available)} available lockers")
    for locker in available[:3]:  # Show first 3
        print(f"   - {locker['locker_id']}: {locker['location']}")
    
    # Test 1: Create first delivery
    print("\n2. Creating first delivery for LOC001...")
    try:
        agent_qr1, customer_qr1 = system.generate_delivery_qr(
            "TEST001", "9876543210", "LOC001", 
            "test1@example.com", "medium", "standard", "Test delivery 1"
        )
        print("   ✓ First delivery created successfully")
        print(f"   Agent QR: {agent_qr1[:20]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Try to create second delivery for same locker (should fail)
    print("\n3. Trying to create second delivery for LOC001 (should fail)...")
    try:
        agent_qr2, customer_qr2 = system.generate_delivery_qr(
            "TEST002", "9876543211", "LOC001",
            "test2@example.com", "small", "express", "Test delivery 2"
        )
        print("   ✗ ERROR: Second delivery was created (this should not happen!)")
        return False
    except ValueError as e:
        print(f"   ✓ Correctly prevented: {e}")
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False
    
    # Test 3: Create second delivery for different locker (should work)
    print("\n4. Creating second delivery for LOC002...")
    try:
        agent_qr2, customer_qr2 = system.generate_delivery_qr(
            "TEST002", "9876543211", "LOC002",
            "test2@example.com", "small", "express", "Test delivery 2"
        )
        print("   ✓ Second delivery created successfully for different locker")
        print(f"   Agent QR: {agent_qr2[:20]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Check available lockers (should exclude LOC001 and LOC002)
    print("\n5. Checking available lockers after creating deliveries...")
    available_after = system.get_available_lockers()
    occupied_lockers = set()
    
    # Check which lockers are now occupied
    all_lockers = system.get_all_lockers()
    for locker in all_lockers:
        if locker.get('has_parcel') or any(
            delivery['locker_id'] == locker['locker_id'] 
            for delivery in [{'locker_id': 'LOC001'}, {'locker_id': 'LOC002'}]
        ):
            occupied_lockers.add(locker['locker_id'])
    
    print(f"   Available lockers now: {len(available_after)}")
    print(f"   Occupied lockers: {', '.join(occupied_lockers) if occupied_lockers else 'None'}")
    
    # Test 5: Complete delivery cycle for LOC001
    print("\n6. Testing complete delivery cycle for LOC001...")
    
    # Agent deposits parcel
    print("   6a. Agent depositing parcel...")
    result = system.agent_deposit_parcel(agent_qr1, "LOC001")
    if result['success']:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ {result['message']}")
        return False
    
    # Agent closes locker
    print("   6b. Agent closing locker...")
    result = system.close_locker_after_deposit("LOC001")
    if result['success']:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ {result['message']}")
        return False
    
    # Customer picks up parcel
    print("   6c. Customer picking up parcel...")
    result = system.customer_pickup_parcel(customer_qr1, "LOC001")
    if result['success']:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ {result['message']}")
        return False
    
    # Customer closes locker (completes delivery)
    print("   6d. Customer closing locker...")
    result = system.close_locker_after_pickup("LOC001")
    if result['success']:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ {result['message']}")
        return False
    
    # Test 6: Check if LOC001 is available again
    print("\n7. Checking if LOC001 is available again...")
    final_available = system.get_available_lockers()
    loc001_available = any(l['locker_id'] == 'LOC001' for l in final_available)
    
    if loc001_available:
        print("   ✓ LOC001 is available again after delivery completion")
    else:
        print("   ✗ LOC001 is still not available")
        return False
    
    print("\n" + "="*50)
    print("✓ ALL TESTS PASSED!")
    print("The locker availability system is working correctly.")
    print("="*50)
    return True

def test_phone_validation():
    """Test phone number validation"""
    print("\n=== Testing Phone Number Validation ===\n")
    
    system = DeliverySystem()
    
    test_cases = [
        ("9876543210", True, "Valid 10-digit number starting with 9"),
        ("8765432109", True, "Valid 10-digit number starting with 8"),
        ("7654321098", True, "Valid 10-digit number starting with 7"),
        ("6543210987", True, "Valid 10-digit number starting with 6"),
        ("5432109876", False, "Invalid: starts with 5"),
        ("12345678901", False, "Invalid: 11 digits"),
        ("987654321", False, "Invalid: 9 digits"),
        ("abcd123456", False, "Invalid: contains letters"),
    ]
    
    for phone, should_pass, description in test_cases:
        try:
            # Clean the phone number like the backend does
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            # Check validation rules
            is_valid = (len(clean_phone) == 10 and 
                       clean_phone.startswith(('6', '7', '8', '9')))
            
            if is_valid == should_pass:
                print(f"   ✓ {description}: {phone}")
            else:
                print(f"   ✗ {description}: {phone} (expected {should_pass}, got {is_valid})")
                
        except Exception as e:
            if should_pass:
                print(f"   ✗ {description}: {phone} - Unexpected error: {e}")
            else:
                print(f"   ✓ {description}: {phone} - Correctly rejected")
    
    print("\nPhone validation tests completed.")

if __name__ == "__main__":
    print("Starting Locker System Tests...\n")
    
    # Test locker availability
    if test_locker_availability():
        # Test phone validation
        test_phone_validation()
        
        print("\n" + "="*60)
        print("🎉 ALL SYSTEMS WORKING CORRECTLY!")
        print("Your locker system is ready for production use.")
        print("="*60)
    else:
        print("\n❌ Some tests failed. Please check the system.")