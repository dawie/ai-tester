"""
Test Case Model

Represents a generated or human-edited Playwright test function.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class TestStatus(Enum):
    """Test case status enumeration."""
    DRAFT = "draft"
    APPROVED = "approved" 
    DEPRECATED = "deprecated"


@dataclass
class SelectorInfo:
    """Information about element selectors used in tests."""
    element_type: str  # button, input, link, etc.
    selector_text: str  # actual CSS/text selector
    selector_type: str  # css, text, role, data-testid
    stability_score: float  # 0.0-1.0, higher = more stable
    fallback_selectors: List[str] = field(default_factory=list)


@dataclass
class TestCase:
    """Represents a generated or human-edited Playwright test function."""
    
    name: str  # Unique test function name following pytest conventions
    description: str  # Human-readable test purpose
    target_url: str  # Web application URL this test targets
    source_page_capture_id: str  # Reference to the page capture used for generation
    test_code: str  # Python Playwright test implementation
    status: TestStatus = TestStatus.DRAFT
    selectors: List[SelectorInfo] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    generated_by: str = "gemini-2.5-computer-use-preview-10-2025"
    
    def __post_init__(self):
        """Validate test case data."""
        if not self.name.isidentifier() or not self.name.startswith('test_'):
            raise ValueError(f"Test name must be valid Python identifier starting with 'test_': {self.name}")
        
        if not self.target_url.startswith(('http://', 'https://')):
            raise ValueError(f"Target URL must be valid HTTP/HTTPS URL: {self.target_url}")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'target_url': self.target_url,
            'source_page_capture_id': self.source_page_capture_id,
            'test_code': self.test_code,
            'status': self.status.value,
            'selectors': [
                {
                    'element_type': sel.element_type,
                    'selector_text': sel.selector_text,
                    'selector_type': sel.selector_type,
                    'stability_score': sel.stability_score,
                    'fallback_selectors': sel.fallback_selectors
                } for sel in self.selectors
            ],
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat(),
            'generated_by': self.generated_by
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TestCase':
        """Create TestCase from dictionary."""
        selectors = [
            SelectorInfo(
                element_type=sel['element_type'],
                selector_text=sel['selector_text'],
                selector_type=sel['selector_type'],
                stability_score=sel['stability_score'],
                fallback_selectors=sel.get('fallback_selectors', [])
            ) for sel in data.get('selectors', [])
        ]
        
        return cls(
            name=data['name'],
            description=data['description'],
            target_url=data['target_url'],
            source_page_capture_id=data['source_page_capture_id'],
            test_code=data['test_code'],
            status=TestStatus(data.get('status', 'draft')),
            selectors=selectors,
            created_at=datetime.fromisoformat(data['created_at']),
            last_modified=datetime.fromisoformat(data['last_modified']),
            generated_by=data.get('generated_by', 'unknown')
        )