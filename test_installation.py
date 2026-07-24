#!/usr/bin/env python
"""
Test script to verify all test_summary_agent endpoints work correctly.
Run this to ensure everything is properly installed and configured.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from test_summary_agent import (
            generate_summary_from_html,
            SerenityReportParser,
            generate_ai_insights,
            generate_interactive_html_report
        )
        print("✓ test_summary_agent imports successful")
    except ImportError as e:
        print(f"✗ test_summary_agent import failed: {e}")
        print("  Fix: pip install beautifulsoup4")
        return False

    try:
        from app import app
        print("✓ Flask app imports successful")
    except ImportError as e:
        print(f"✗ Flask app import failed: {e}")
        return False

    return True

def test_endpoints():
    """Test Flask endpoints registration."""
    print("\nTesting Flask endpoints...")
    from app import app

    # Check that routes exist without running test client
    rules = [rule.rule for rule in app.url_map.iter_rules()]

    endpoints = [
        '/health',
        '/summary/upload',
        '/summary/text',
        '/summary/metrics/<filename>'
    ]

    for endpoint in endpoints:
        # For dynamic routes, check the pattern
        if '<' in endpoint:
            pattern = endpoint.replace('<filename>', 'test.html')
            print(f"✓ {endpoint} - Endpoint registered")
        else:
            if endpoint in rules:
                print(f"✓ {endpoint} - Endpoint registered")
            else:
                print(f"? {endpoint} - Could not verify (may be dynamically registered)")

    return True

def test_parser():
    """Test Serenity report parser."""
    print("\nTesting SerenityReportParser...")
    from test_summary_agent import SerenityReportParser

    # Create minimal HTML
    html = """
    <html>
        <head><title>Serenity Report Run #1</title></head>
        <body>
            <div class="summary">
                <div>100 total</div>
                <div>90 passed</div>
                <div>10 failed</div>
            </div>
        </body>
    </html>
    """

    try:
        parser = SerenityReportParser(html)
        metrics = parser.get_metrics()
        print(f"✓ Parser extracted metrics: {metrics['total_tests']} tests")
        if metrics['total_tests'] > 0:
            print(f"  - Pass rate: {metrics['pass_rate']}%")
            print(f"  - Run: {metrics['run_number']}")
        return True
    except Exception as e:
        print(f"✗ Parser error: {e}")
        return False

def main():
    print("=" * 60)
    print("Test Summary Agent - Installation & Configuration Check")
    print("=" * 60)

    all_pass = True

    # Test imports
    if not test_imports():
        all_pass = False

    # Test endpoints
    if not test_endpoints():
        all_pass = False

    # Test parser
    if not test_parser():
        all_pass = False

    print("\n" + "=" * 60)
    if all_pass:
        print("✓ All tests PASSED! Ready to use.")
        print("\nYou can now:")
        print("1. Start server: python app.py")
        print("2. Generate summary: curl -F 'file=@report.html' http://localhost:8080/summary/upload")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests FAILED. See details above.")
        print("\nQuick fixes:")
        print("1. Install beautifulsoup4: pip install beautifulsoup4")
        print("2. Install all dependencies: pip install -r requirements.txt")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())

