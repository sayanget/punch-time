import requests
import uuid

BASE_URL = 'http://localhost:7778'
# Use a fresh user every time to avoid conflicts
USERNAME = f'verify_{uuid.uuid4().hex[:8]}'
PASSWORD = 'password123'

def setup_data():
    session = requests.Session()
    
    # 1. Register and Login
    print(f"Registering user: {USERNAME}")
    res = session.post(f'{BASE_URL}/register', data={'username': USERNAME, 'password': PASSWORD})
    print(f"Register: {res.status_code}")
    
    res = session.post(f'{BASE_URL}/login', data={'username': USERNAME, 'password': PASSWORD})
    print(f"Login: {res.status_code}")
    
    # 2. Add punches
    DATE = '2026-01-02'
    
    # Ghost punch (Early morning) - Should be HIDDEN in UI
    print("Adding Ghost Punch (04:00)...")
    session.post(f'{BASE_URL}/api/punch', json={'date': DATE, 'time': '04:00', 'lateShift': True})
    
    # Normal punches - Should be VISIBLE
    punches = ['08:00', '12:00', '13:00', '18:00']
    for t in punches:
        print(f"Adding Normal Punch ({t})...")
        session.post(f'{BASE_URL}/api/punch', json={'date': DATE, 'time': t})
        
    print("Data setup complete.")
    print(f"User credentials: {USERNAME} / {PASSWORD}")

if __name__ == '__main__':
    try:
        setup_data()
    except Exception as e:
        print(f"Error: {e}")
