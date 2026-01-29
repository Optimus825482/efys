"""
Comprehensive Route Testing Script
Tests all OSB panel routes for 200 OK response and no exceptions
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

# All routes grouped by module
ROUTES_TO_TEST = {
    "Dashboard": [
        "/",  # dashboard_bp has no prefix
        "/live",  # Fixed: /dashboard/live -> /live
        "/reactive",  # Fixed: /dashboard/reactive -> /reactive
        "/alarms"  # Fixed: /dashboard/alarms -> /alarms
    ],
    "Monitoring": [
        "/monitoring/last-indexes",
        "/monitoring/load-profile",
        "/monitoring/vee",
        "/monitoring/missing-data",
        "/monitoring/loss-analysis"
    ],
    "Billing": [
        "/billing/",
        "/billing/tariff",
        "/billing/period",
        "/billing/calculate",
        "/billing/bulk",  # Fixed: bulk-invoice -> bulk
        "/billing/preview",
        "/billing/additional",
        "/billing/cancel",
        "/billing/print"
    ],
    "Subscribers": [
        "/subscribers",
        "/subscribers/card",
        "/subscribers/contracts"
    ],
    "Reports": [
        "/reports/index-report",  # Fixed: /index -> /index-report
        "/reports/consumption",
        "/reports/invoice-report",  # Fixed: /invoice -> /invoice-report
        "/reports/reading-success",
        "/reports/loss-report",  # Fixed: /loss -> /loss-report
        "/reports/reactive-report"  # Fixed: /reactive -> /reactive-report
    ],
    "Smart Systems": [
        "/smart/regulation-bot",
        "/smart/penalty-prevention",
        "/smart/portal",
        "/smart/erp-bridge"
    ],
    "Settings": [
        "/settings/users",
        "/settings/roles",
        "/settings/parameters",
        "/settings/email-sms",
        "/settings/backup",
        "/settings/logs",
        "/settings/security",
        "/settings/mevzuat"
    ]
}

def test_route(url):
    """Test a single route"""
    try:
        response = requests.get(f"{BASE_URL}{url}", timeout=5)
        return {
            "url": url,
            "status": response.status_code,
            "success": response.status_code == 200,
            "error": None
        }
    except requests.exceptions.Timeout:
        return {
            "url": url,
            "status": "TIMEOUT",
            "success": False,
            "error": "Request timeout (>5s)"
        }
    except Exception as e:
        return {
            "url": url,
            "status": "ERROR",
            "success": False,
            "error": str(e)
        }

def main():
    print("=" * 80)
    print("EFYS OSB PANEL - COMPREHENSIVE ROUTE TEST")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_routes = sum(len(routes) for routes in ROUTES_TO_TEST.values())
    success_count = 0
    failed_routes = []
    
    for module, routes in ROUTES_TO_TEST.items():
        print(f"\n{'='*80}")
        print(f"MODULE: {module} ({len(routes)} routes)")
        print(f"{'='*80}")
        
        module_success = 0
        for route in routes:
            result = test_route(route)
            
            if result["success"]:
                status_symbol = "✅"
                module_success += 1
                success_count += 1
            else:
                status_symbol = "❌"
                failed_routes.append(result)
            
            print(f"{status_symbol} {result['url']:<40} [Status: {result['status']}]")
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        print(f"\nModule Summary: {module_success}/{len(routes)} passed")
    
    # Final Report
    print("\n" + "=" * 80)
    print("FINAL REPORT")
    print("=" * 80)
    print(f"Total Routes Tested: {total_routes}")
    print(f"✅ Passed: {success_count}")
    print(f"❌ Failed: {len(failed_routes)}")
    print(f"Success Rate: {success_count/total_routes*100:.1f}%")
    
    if failed_routes:
        print("\n" + "=" * 80)
        print("FAILED ROUTES DETAILS")
        print("=" * 80)
        for route in failed_routes:
            print(f"\n❌ {route['url']}")
            print(f"   Status: {route['status']}")
            print(f"   Error: {route['error']}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Return exit code
    return 0 if len(failed_routes) == 0 else 1

if __name__ == "__main__":
    exit(main())
