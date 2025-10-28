"""
Test Report Model

Represents results from executing a set of test cases.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class TestResult:
    """Individual test execution result."""
    test_name: str
    status: str  # PASSED, FAILED, SKIPPED
    duration_ms: int
    error_message: Optional[str] = None
    failure_screenshot_path: Optional[str] = None
    failure_html_path: Optional[str] = None
    console_logs: List[str] = field(default_factory=list)


@dataclass
class TestReport:
    """Results from executing a set of test cases."""
    
    id: str  # Unique report identifier
    execution_start: datetime
    execution_end: datetime
    test_results: List[TestResult] = field(default_factory=list)
    total_tests: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    junit_xml_path: str = ""
    html_report_path: Optional[str] = None
    
    def __post_init__(self):
        """Validate test report data."""
        if self.execution_end < self.execution_start:
            raise ValueError("Execution end must be after execution start")
        
        # Auto-calculate counts if not provided
        if not self.total_tests and self.test_results:
            self.total_tests = len(self.test_results)
            self.passed_count = sum(1 for r in self.test_results if r.status == "PASSED")
            self.failed_count = sum(1 for r in self.test_results if r.status == "FAILED")
            self.skipped_count = sum(1 for r in self.test_results if r.status == "SKIPPED")
        
        # Validate counts sum to total
        if self.passed_count + self.failed_count + self.skipped_count != self.total_tests:
            raise ValueError("Count fields must sum to total_tests")
    
    @property
    def duration_ms(self) -> int:
        """Total execution duration in milliseconds."""
        return int((self.execution_end - self.execution_start).total_seconds() * 1000)
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage (0.0-100.0)."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_count / self.total_tests) * 100.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'execution_start': self.execution_start.isoformat(),
            'execution_end': self.execution_end.isoformat(),
            'duration_ms': self.duration_ms,
            'test_results': [
                {
                    'test_name': result.test_name,
                    'status': result.status,
                    'duration_ms': result.duration_ms,
                    'error_message': result.error_message,
                    'failure_screenshot_path': result.failure_screenshot_path,
                    'failure_html_path': result.failure_html_path,
                    'console_logs': result.console_logs
                } for result in self.test_results
            ],
            'total_tests': self.total_tests,
            'passed_count': self.passed_count,
            'failed_count': self.failed_count,
            'skipped_count': self.skipped_count,
            'success_rate': self.success_rate,
            'junit_xml_path': self.junit_xml_path,
            'html_report_path': self.html_report_path
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TestReport':
        """Create TestReport from dictionary."""
        test_results = [
            TestResult(
                test_name=result['test_name'],
                status=result['status'],
                duration_ms=result['duration_ms'],
                error_message=result.get('error_message'),
                failure_screenshot_path=result.get('failure_screenshot_path'),
                failure_html_path=result.get('failure_html_path'),
                console_logs=result.get('console_logs', [])
            ) for result in data.get('test_results', [])
        ]
        
        return cls(
            id=data['id'],
            execution_start=datetime.fromisoformat(data['execution_start']),
            execution_end=datetime.fromisoformat(data['execution_end']),
            test_results=test_results,
            total_tests=data['total_tests'],
            passed_count=data['passed_count'],
            failed_count=data['failed_count'],
            skipped_count=data['skipped_count'],
            junit_xml_path=data['junit_xml_path'],
            html_report_path=data.get('html_report_path')
        )