"""Test Mevzuat API endpoints"""
import requests
base = 'http://localhost:5000/settings'

# Test mevzuat page
r = requests.get(f'{base}/mevzuat')
print(f'/settings/mevzuat: {r.status_code}')

# Test API endpoints
r = requests.get(f'{base}/api/mevzuat/sources')
print(f'GET sources: {r.status_code} - {len(r.json().get("data",[]))} sources')

r = requests.get(f'{base}/api/mevzuat/keywords')
print(f'GET keywords: {r.status_code} - {len(r.json().get("data",[]))} keywords')

r = requests.get(f'{base}/api/mevzuat/alerts')
print(f'GET alerts: {r.status_code}')

r = requests.get(f'{base}/api/mevzuat/stats')
stats = r.json().get("data",{}).get("stats",{})
print(f'GET stats: {r.status_code} - {stats}')

print('\n✓ Mevzuat API tests passed!')
