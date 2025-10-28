"""
Models package for AI Tester.

Contains data models for test cases, page captures, test reports, and test runs.
"""

from .test_case import TestCase, TestStatus, SelectorInfo
from .page_capture import PageCapture, CaptureMetadata, ErrorInfo
from .test_report import TestReport, TestResult
from .test_run import TestRun

__all__ = [
    'TestCase', 'TestStatus', 'SelectorInfo',
    'PageCapture', 'CaptureMetadata', 'ErrorInfo', 
    'TestReport', 'TestResult',
    'TestRun'
]