"""Tariff API Test Script"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_create_osb_tariff():
    print("Testing OSB Distribution Tariff Creation...")
    payload = {
        'period_year': 2027,
        'tariff_type': 'dual_term',
        'og_rate': 26.5,
        'ag_rate': 31.0,
        'capacity_rate': 4300,
        'is_active': True
    }
    
    r = requests.post(f'{BASE_URL}/billing/api/osb-distribution-tariffs', json=payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
    return r.status_code == 200 or r.status_code == 201

def test_create_edas_tariff():
    print("\nTesting EDAŞ Tariff Creation...")
    payload = {
        'edas_name': 'Uludağ EDAŞ',
        'period_year': 2027,
        'single_term_og_rate': 33.0,
        'single_term_ag_rate': 39.5,
        'dual_term_capacity_rate': 4600,
        'dual_term_energy_rate': 19.0,
        'is_active': True
    }
    
    r = requests.post(f'{BASE_URL}/billing/api/edas-tariffs', json=payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
    return r.status_code == 200 or r.status_code == 201

def test_update_settings():
    print("\nTesting Billing Settings Update...")
    payload = {
        'kdv_rate': 0.20,
        'btv_rate': 0.05,
        'transmission_fee_rate': 0.035,
        'energy_unit_cost': 2.85,
        'reactive_penalty_rate': 0.89,
        'inductive_limit': 0.20,
        'capacitive_limit': 0.15,
        'loss_percentage': 2.5
    }
    
    r = requests.put(f'{BASE_URL}/billing/api/billing-settings', json=payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
    return r.status_code == 200

if __name__ == '__main__':
    print("="*60)
    print("TARIFF API TEST SUITE")
    print("="*60)
    
    results = []
    results.append(("OSB Distribution Tariff", test_create_osb_tariff()))
    results.append(("EDAŞ Tariff", test_create_edas_tariff()))
    results.append(("Billing Settings", test_update_settings()))
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")
    
    print("\nAll tests completed!")
