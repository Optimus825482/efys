#!/usr/bin/env python3
"""
EFYS - Endpoint Verification Script
Tests all 50+ pages to ensure they load without 500 errors
"""

import requests
from colorama import init, Fore, Style
import sys

init(autoreset=True)

BASE_URL = "http://localhost:5000"

# All endpoints to test
ENDPOINTS = {
    "Dashboard": [
        "/",
        "/live",
        "/reactive",
        "/alarms",
    ],
    "Subscribers": [
        "/subscribers/",
        "/subscribers/list",
        "/subscribers/card",
        "/subscribers/add",
        "/subscribers/meters",
        "/subscribers/contracts",
        "/subscribers/groups",
    ],
    # "Readings" modülü sistemden kaldırıldı (Okuma işlemleri artık otomatik)
    "Billing": [
        "/billing/",
        "/billing/tariff",
        "/billing/period",
        "/billing/calculate",
        "/billing/bulk",
        "/billing/preview",
        "/billing/additional",
        "/billing/cancel",
        "/billing/print",
    ],
    "Monitoring": [
        "/monitoring/",
        "/monitoring/last-indexes",
        "/monitoring/load-profile",
        "/monitoring/vee",
        "/monitoring/missing-data",
        "/monitoring/loss-analysis",
    ],
    "Reports": [
        "/reports/",
        "/reports/index-report",
        "/reports/consumption",
        "/reports/invoice-report",
        "/reports/reading-success",
        "/reports/loss-report",
        "/reports/reactive-report",
        "/reports/demand-report",
    ],
}

def test_endpoint(url):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code, response.elapsed.total_seconds()
    except requests.exceptions.RequestException as e:
        return None, str(e)

def main():
    """Main test function"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}EFYS - Endpoint Verification Test")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for module, endpoints in ENDPOINTS.items():
        print(f"\n{Fore.YELLOW}Testing {module}...")
        print(f"{Fore.YELLOW}{'-'*70}")
        
        for endpoint in endpoints:
            url = BASE_URL + endpoint
            status_code, response_time = test_endpoint(url)
            total_tests += 1
            
            if status_code == 200:
                passed_tests += 1
                print(f"{Fore.GREEN}✓ {endpoint:40} [{status_code}] {response_time:.3f}s")
            elif status_code == 404:
                failed_tests += 1
                print(f"{Fore.RED}✗ {endpoint:40} [404 NOT FOUND]")
            elif status_code == 500:
                failed_tests += 1
                print(f"{Fore.RED}✗ {endpoint:40} [500 SERVER ERROR]")
            elif status_code is None:
                failed_tests += 1
                print(f"{Fore.RED}✗ {endpoint:40} [CONNECTION ERROR: {response_time}]")
            else:
                failed_tests += 1
                print(f"{Fore.YELLOW}⚠ {endpoint:40} [{status_code}]")
    
    # Summary
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}Test Summary")
    print(f"{Fore.CYAN}{'='*70}")
    print(f"Total Tests:  {total_tests}")
    print(f"{Fore.GREEN}Passed:       {passed_tests}")
    print(f"{Fore.RED}Failed:       {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    # Exit code
    if failed_tests == 0:
        print(f"{Fore.GREEN}✓ All tests passed! System is ready.{Style.RESET_ALL}\n")
        sys.exit(0)
    else:
        print(f"{Fore.RED}✗ Some tests failed. Please check the errors above.{Style.RESET_ALL}\n")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user.{Style.RESET_ALL}\n")
        sys.exit(1)
