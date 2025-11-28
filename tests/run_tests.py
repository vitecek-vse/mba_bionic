import pytest
import sys
import os
import io
from datetime import datetime
from typing import Dict, List

class TestResult:
    def __init__(self, name, status, message="", logs="", test_type="unit"):
        self.name = name
        self.status = status  # "passed", "failed", or "error"
        self.message = message
        self.logs = logs
        self.timestamp = datetime.now()
        self.test_type = test_type

def get_test_list() -> Dict[str, List[str]]:
    """
    Get a list of all available tests organized by type.
    
    Returns:
        Dict[str, List[str]]: Dictionary with test types as keys and lists of test names as values
    """
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get unit tests
    unit_tests = []
    unit_dir = os.path.join(test_dir, 'unit')
    if os.path.exists(unit_dir):
        for file in os.listdir(unit_dir):
            if file.startswith('test_') and file.endswith('.py'):
                with open(os.path.join(unit_dir, file), 'r') as f:
                    content = f.read()
                    # Find all test functions
                    for line in content.split('\n'):
                        if line.strip().startswith('def test_'):
                            test_name = line.split('def ')[1].split('(')[0]
                            unit_tests.append(test_name)
    
    # Get integration tests
    integration_tests = []
    integration_dir = os.path.join(test_dir, 'integration')
    if os.path.exists(integration_dir):
        for file in os.listdir(integration_dir):
            if file.startswith('test_') and file.endswith('.py'):
                with open(os.path.join(integration_dir, file), 'r') as f:
                    content = f.read()
                    # Find all test functions
                    for line in content.split('\n'):
                        if line.strip().startswith('def test_'):
                            test_name = line.split('def ')[1].split('(')[0]
                            integration_tests.append(test_name)
    
    return {
        "unit": unit_tests,
        "integration": integration_tests
    }

def run_tests(test_type=None):
    """
    Run the test suite and return detailed results.
    
    Args:
        test_type (str, optional): Type of tests to run. Can be 'unit', 'integration', or None for all tests.
    
    Returns:
        tuple: (test_results, logs, test_list)
            - test_results: List of TestResult objects
            - logs: Full test logs
            - test_list: Dictionary of available tests by type
    """
    # Get the directory of this file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the project root to Python path
    project_root = os.path.dirname(test_dir)
    sys.path.insert(0, project_root)
    
    # Get list of available tests
    test_list = get_test_list()
    
    # Determine which tests to run
    if test_type == 'unit':
        test_path = os.path.join(test_dir, 'unit')
    elif test_type == 'integration':
        test_path = os.path.join(test_dir, 'integration')
    else:
        test_path = test_dir
    
    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # Run the tests with custom options
    args = [
        test_path,
        '-v',  # verbose output
        '--tb=short',  # shorter traceback format
        '--capture=sys',  # capture stdout/stderr
    ]
    
    # Run pytest and capture results
    result = pytest.main(args)
    
    # Get the captured output
    logs = stdout_capture.getvalue() + stderr_capture.getvalue()
    
    # Parse test results
    test_results = []
    
    # Add test results based on the output
    for line in logs.split('\n'):
        if 'test_' in line:
            test_name = line.split('::')[1].strip()
            test_type = 'unit' if 'unit' in line else 'integration'
            
            if 'PASSED' in line:
                test_results.append(TestResult(
                    name=test_name,
                    status="passed",
                    logs=line,
                    test_type=test_type
                ))
            elif 'FAILED' in line:
                test_results.append(TestResult(
                    name=test_name,
                    status="failed",
                    logs=line,
                    test_type=test_type
                ))
            elif 'ERROR' in line:
                test_results.append(TestResult(
                    name=test_name,
                    status="error",
                    logs=line,
                    test_type=test_type
                ))
    
    return test_results, logs, test_list

if __name__ == '__main__':
    # If run directly, run all tests and print results
    results, logs, test_list = run_tests()
    for result in results:
        print(f"{result.name}: {result.status}") 