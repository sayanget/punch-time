import requests
import json

import uuid
# Configuration
BASE_URL = 'http://localhost:7778'
USERNAME = f'user_{uuid.uuid4()}'
PASSWORD = 'password123'

def register_and_login():
    session = requests.Session()
    # Register
    session.post(f'{BASE_URL}/register', data={'username': USERNAME, 'password': PASSWORD})
    # Login
    session.post(f'{BASE_URL}/login', data={'username': USERNAME, 'password': PASSWORD})
    return session

def reproduce():
    session = register_and_login()
    
    # Dates
    DAY_1 = '2026-01-01'
    DAY_2 = '2026-01-02'
    
    print(f"--- Simulating Scenario ---")
    
    # 1. Day 1 Late Shift Punch (Actually punched on Day 2, so punch_date=Day 2)
    # The system will dual-record it to Day 1.
    print(f"Punching Day 2 Early Morning (belongs to Day 1): {DAY_2} 04:00...")
    resp = session.post(f'{BASE_URL}/api/punch', json={
        'date': DAY_2, 
        'time': '04:00',
        'lateShift': True 
    })
    try:
        print(f"Response: {resp.json()}")
    except:
        print(f"Response Error: {resp.status_code} {resp.url}")
        print(f"Content: {resp.text[:200]}")

    # Verify Day 2 has the record
    resp = session.get(f'{BASE_URL}/api/punches')
    try:
        data = resp.json()
        print(f"Day 2 Punches (Expect 1): {data.get(DAY_2)}")
    except:
        print(f"Get Punches Error: {resp.text[:200]}")
        return
    
    # 2. Day 2 Normal Punches
    punches = ['08:00', '12:00', '13:00']
    for p in punches:
        print(f"Punching Day 2 Normal: {p}...")
        resp = session.post(f'{BASE_URL}/api/punch', json={
            'date': DAY_2,
            'time': p
        })
        try:
            print(f"Response: {resp.json()}")
        except:
             print(f"Response Error: {resp.status_code}")
             
    # 3. Day 2 End Punch (The problematic one?)
    print(f"Punching Day 2 End: 18:00...")
    resp = session.post(f'{BASE_URL}/api/punch', json={
        'date': DAY_2,
        'time': '18:00'
    })
    try:
        print(f"Response: {resp.json()}")
    except:
        print(f"Response Error: {resp.status_code} {resp.text[:100]}")
    data = resp.json()
    day2_punches = data.get(DAY_2, [])
    print(f"Day 2 Final Punches: {day2_punches}")
    print(f"Count: {len(day2_punches)}")
    
    if len(day2_punches) == 5:
        print("SUCCESS: Backend accepted 5 punches.")
    else:
        print(f"FAILURE: Backend count {len(day2_punches)} != 5")

if __name__ == '__main__':
    try:
        reproduce()
    except Exception as e:
        print(f"Error: {e}")
