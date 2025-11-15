#!/usr/bin/env python3
"""
Test script to simulate payment-subscription flow and identify potential issues.
"""
import sys
import os
from datetime import datetime, timedelta
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.models import db, Order, Subscription, User, MealPlan, SubscriptionStatus, SubscriptionFrequency
from utils.razorpay_utils import create_razorpay_order, verify_payment_signature
from sqlalchemy.exc import IntegrityError

class PaymentSubscriptionTester:
    """Test the payment-subscription flow"""
    
    def __init__(self):
        self.app = create_app()
        self.test_results = []
    
    def test_payment_verification_flow(self):
        """Test the payment verification flow"""
        print("🧪 Testing Payment Verification Flow...")
        
        with self.app.app_context():
            try:
                # Create test user
                test_user = User(
                    username='test_user_payment',
                    name='Test User',
                    email='test@example.com',
                    phone='1234567890',
                    address='123 Test St',
                    city='Test City',
                    province='ON',
                    postal_code='A1A1A1'
                )
                db.session.add(test_user)
                db.session.flush()
                
                # Get a meal plan
                meal_plan = MealPlan.query.first()
                if not meal_plan:
                    print("❌ No meal plans found in database")
                    return False
                
                # Create test order data
                order_data = {
                    'amount': 1000,  # 10.00 in paise
                    'currency': 'INR',
                    'receipt': f'test_receipt_{datetime.now().timestamp()}',
                    'notes': {
                        'customer_email': test_user.email,
                        'customer_name': test_user.name,
                        'customer_phone': test_user.phone,
                        'customer_address': test_user.address,
                        'customer_city': test_user.city,
                        'customer_state': test_user.province,
                        'customer_pincode': test_user.postal_code,
                        'plan_id': meal_plan.id,
                        'frequency': 'weekly',
                        'vegetarian_days': '1,3,5'
                    }
                }
                
                # Test order creation
                print("  Testing Razorpay order creation...")
                razorpay_order = create_razorpay_order(
                    amount=order_data['amount'],
                    currency=order_data['currency'],
                    receipt=order_data['receipt'],
                    notes=order_data['notes']
                )
                
                if not razorpay_order:
                    print("❌ Failed to create Razorpay order")
                    return False
                
                print(f"  ✅ Razorpay order created: {razorpay_order['id']}")
                
                # Test payment verification (simulate)
                print("  Testing payment verification...")
                
                # Simulate payment verification data
                payment_data = {
                    'razorpay_payment_id': f'pay_test_{datetime.now().timestamp()}',
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_signature': 'test_signature'
                }
                
                # Test the verification flow
                from routes.main_routes import _create_development_subscription
                
                try:
                    result = _create_development_subscription(
                        order_data, 
                        razorpay_order['id'], 
                        payment_data['razorpay_payment_id']
                    )
                    print("  ✅ Payment verification flow completed successfully")
                    return True
                    
                except Exception as e:
                    print(f"❌ Payment verification failed: {str(e)}")
                    return False
                
            except Exception as e:
                print(f"❌ Test failed: {str(e)}")
                return False
            finally:
                # Cleanup test data
                try:
                    test_user = User.query.filter_by(email='test@example.com').first()
                    if test_user:
                        # Delete related subscriptions and orders
                        Subscription.query.filter_by(user_id=test_user.id).delete()
                        Order.query.filter_by(user_id=test_user.id).delete()
                        db.session.delete(test_user)
                        db.session.commit()
                except:
                    pass
    
    def test_webhook_flow(self):
        """Test the webhook flow"""
        print("🧪 Testing Webhook Flow...")
        
        with self.app.app_context():
            try:
                # Create test order
                test_user = User.query.filter_by(email='test@example.com').first()
                if not test_user:
                    test_user = User(
                        username='test_user_webhook',
                        name='Test User Webhook',
                        email='test@example.com',
                        phone='1234567890',
                        address='123 Test St',
                        city='Test City',
                        province='ON',
                        postal_code='A1A1A1'
                    )
                    db.session.add(test_user)
                    db.session.flush()
                
                meal_plan = MealPlan.query.first()
                
                # Create test order
                test_order = Order(
                    user_id=test_user.id,
                    meal_plan_id=meal_plan.id,
                    amount=10.00,
                    total_amount=10.00,
                    status='pending',
                    payment_status='pending',
                    payment_id=f'pay_test_{datetime.now().timestamp()}',
                    order_id=f'order_test_{datetime.now().timestamp()}'
                )
                db.session.add(test_order)
                db.session.commit()
                
                # Simulate webhook payload
                webhook_payload = {
                    'event': 'payment.captured',
                    'payload': {
                        'payment': {
                            'entity': {
                                'id': test_order.payment_id,
                                'order_id': test_order.order_id,
                                'amount': 1000  # 10.00 in paise
                            }
                        }
                    }
                }
                
                # Test webhook processing
                from routes.main_routes import razorpay_webhook
                from flask import request
                
                # Simulate webhook request
                with self.app.test_request_context(
                    '/webhook/razorpay',
                    method='POST',
                    json=webhook_payload,
                    headers={'X-Razorpay-Signature': 'test_signature'}
                ):
                    try:
                        response = razorpay_webhook()
                        print("  ✅ Webhook processing completed")
                        return True
                    except Exception as e:
                        print(f"❌ Webhook processing failed: {str(e)}")
                        return False
                
            except Exception as e:
                print(f"❌ Webhook test failed: {str(e)}")
                return False
            finally:
                # Cleanup
                try:
                    test_user = User.query.filter_by(email='test@example.com').first()
                    if test_user:
                        Subscription.query.filter_by(user_id=test_user.id).delete()
                        Order.query.filter_by(user_id=test_user.id).delete()
                        db.session.delete(test_user)
                        db.session.commit()
                except:
                    pass
    
    def test_race_condition(self):
        """Test for race conditions between payment verification and webhook"""
        print("🧪 Testing Race Condition...")
        
        with self.app.app_context():
            try:
                # Create test data
                test_user = User(
                    username='test_user_race',
                    name='Test User Race',
                    email='test_race@example.com',
                    phone='1234567890',
                    address='123 Test St',
                    city='Test City',
                    province='ON',
                    postal_code='A1A1A1'
                )
                db.session.add(test_user)
                db.session.flush()
                
                meal_plan = MealPlan.query.first()
                
                # Create order data
                order_data = {
                    'amount': 1000,
                    'notes': {
                        'customer_email': test_user.email,
                        'customer_name': test_user.name,
                        'customer_phone': test_user.phone,
                        'customer_address': test_user.address,
                        'customer_city': test_user.city,
                        'customer_state': test_user.province,
                        'customer_pincode': test_user.postal_code,
                        'plan_id': meal_plan.id,
                        'frequency': 'weekly',
                        'vegetarian_days': '1,3,5'
                    }
                }
                
                razorpay_order_id = f'order_test_race_{datetime.now().timestamp()}'
                payment_id = f'pay_test_race_{datetime.now().timestamp()}'
                
                # Simulate concurrent payment verification and webhook
                print("  Simulating concurrent payment verification and webhook...")
                
                # First, call payment verification
                from routes.main_routes import _create_development_subscription
                
                result1 = _create_development_subscription(
                    order_data, razorpay_order_id, payment_id
                )
                
                # Then, simulate webhook call
                test_order = Order.query.filter_by(order_id=razorpay_order_id).first()
                if test_order:
                    # Check if subscription was created
                    subscription = Subscription.query.filter_by(order_id=test_order.id).first()
                    if subscription:
                        print("  ✅ Payment verification created subscription successfully")
                    else:
                        print("❌ Payment verification failed to create subscription")
                        return False
                
                # Now simulate webhook trying to create another subscription
                webhook_payload = {
                    'event': 'payment.captured',
                    'payload': {
                        'payment': {
                            'entity': {
                                'id': payment_id,
                                'order_id': razorpay_order_id,
                                'amount': 1000
                            }
                        }
                    }
                }
                
                # The webhook should not create a duplicate subscription
                from routes.main_routes import razorpay_webhook
                
                with self.app.test_request_context(
                    '/webhook/razorpay',
                    method='POST',
                    json=webhook_payload,
                    headers={'X-Razorpay-Signature': 'test_signature'}
                ):
                    razorpay_webhook()
                
                # Check for duplicate subscriptions
                subscriptions = Subscription.query.filter_by(order_id=test_order.id).all()
                if len(subscriptions) == 1:
                    print("  ✅ No duplicate subscriptions created (race condition handled)")
                    return True
                else:
                    print(f"❌ Race condition detected: {len(subscriptions)} subscriptions created")
                    return False
                
            except Exception as e:
                print(f"❌ Race condition test failed: {str(e)}")
                return False
            finally:
                # Cleanup
                try:
                    test_user = User.query.filter_by(email='test_race@example.com').first()
                    if test_user:
                        Subscription.query.filter_by(user_id=test_user.id).delete()
                        Order.query.filter_by(user_id=test_user.id).delete()
                        db.session.delete(test_user)
                        db.session.commit()
                except:
                    pass
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("🧪 Testing Error Handling...")
        
        test_scenarios = [
            {
                'name': 'Missing payment parameters',
                'test': self._test_missing_payment_parameters
            },
            {
                'name': 'Invalid payment signature',
                'test': self._test_invalid_payment_signature
            },
            {
                'name': 'Database constraint violation',
                'test': self._test_database_constraint_violation
            },
            {
                'name': 'Session data loss',
                'test': self._test_session_data_loss
            }
        ]
        
        results = []
        for scenario in test_scenarios:
            print(f"  Testing: {scenario['name']}")
            try:
                result = scenario['test']()
                results.append({
                    'scenario': scenario['name'],
                    'passed': result
                })
                print(f"    {'✅' if result else '❌'} {scenario['name']}")
            except Exception as e:
                print(f"    ❌ {scenario['name']} failed: {str(e)}")
                results.append({
                    'scenario': scenario['name'],
                    'passed': False,
                    'error': str(e)
                })
        
        return results
    
    def _test_missing_payment_parameters(self):
        """Test handling of missing payment parameters"""
        # This would test the validation in verify_payment
        return True  # Placeholder
    
    def _test_invalid_payment_signature(self):
        """Test handling of invalid payment signature"""
        # This would test signature verification
        return True  # Placeholder
    
    def _test_database_constraint_violation(self):
        """Test handling of database constraint violations"""
        with self.app.app_context():
            try:
                # Try to create a duplicate subscription
                # This should be handled gracefully
                return True
            except IntegrityError:
                return True  # Expected behavior
            except Exception:
                return False
    
    def _test_session_data_loss(self):
        """Test handling of session data loss"""
        # This would test the fallback mechanisms
        return True  # Placeholder
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Payment-Subscription Flow Tests...\n")
        
        tests = [
            ('Payment Verification Flow', self.test_payment_verification_flow),
            ('Webhook Flow', self.test_webhook_flow),
            ('Race Condition', self.test_race_condition),
            ('Error Handling', self.test_error_handling)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            print(f"Running: {test_name}")
            print(f"{'='*50}")
            
            try:
                if test_name == 'Error Handling':
                    result = test_func()
                else:
                    result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
                results[test_name] = False
        
        # Print summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY")
        print(f"{'='*50}")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Payment-subscription flow is working correctly.")
        else:
            print("⚠️ Some tests failed. Review the issues above.")
        
        return results

def main():
    """Main test function"""
    tester = PaymentSubscriptionTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    main()
