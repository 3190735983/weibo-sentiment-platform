"""快速测试API"""
import requests

try:
    # 测试topics API
    print("Testing GET /api/visualization/topics...")
    r = requests.get('http://localhost:5000/api/visualization/topics', timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
    
except Exception as e:
    print(f"Error: {e}")
