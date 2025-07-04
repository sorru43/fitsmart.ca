#!/usr/bin/env python3
"""
Test Redis connection for Flask-Limiter
"""
import redis
import sys

def test_redis_connection():
    """Test Redis connection"""
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        r.delete('test_key')
        
        if value == 'test_value':
            print("✅ Redis connection successful!")
            print("✅ Basic operations working")
            return True
        else:
            print("❌ Redis test failed")
            return False
            
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Redis error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Redis connection...")
    success = test_redis_connection()
    sys.exit(0 if success else 1) 