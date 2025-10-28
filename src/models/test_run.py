"""
Test Run Model

Represents a single execution session encompassing all tests and artifacts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class TestRun:
    """Single execution session encompassing all tests and artifacts."""
    
    id: str  # Unique session identifier
    trigger_type: str = "MANUAL"  # MANUAL | CI_CD | SCHEDULED
    environment: Dict[str, str] = field(default_factory=dict)
    docker_image: str = "mcr.microsoft.com/playwright/python:v1.48.0-jammy"
    test_directory: str = "tests/approved/"
    artifacts_directory: str = "captures/"
    exit_code: int = 0  # Overall execution result (0 = success)
    console_output: str = ""
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate test run data."""
        if self.trigger_type not in ["MANUAL", "CI_CD", "SCHEDULED"]:
            raise ValueError(f"Invalid trigger_type: {self.trigger_type}")
    
    @property
    def duration_ms(self) -> int:
        """Execution duration in milliseconds."""
        if not self.completed_at:
            return 0
        return int((self.completed_at - self.started_at).total_seconds() * 1000)
    
    @property
    def is_success(self) -> bool:
        """Whether the test run was successful."""
        return self.exit_code == 0
    
    def complete(self, exit_code: int = 0) -> None:
        """Mark the test run as completed."""
        self.completed_at = datetime.utcnow()
        self.exit_code = exit_code
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'trigger_type': self.trigger_type,
            'environment': self.environment,
            'docker_image': self.docker_image,
            'test_directory': self.test_directory,
            'artifacts_directory': self.artifacts_directory,
            'exit_code': self.exit_code,
            'console_output': self.console_output,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms,
            'is_success': self.is_success
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TestRun':
        """Create TestRun from dictionary."""
        return cls(
            id=data['id'],
            trigger_type=data.get('trigger_type', 'MANUAL'),
            environment=data.get('environment', {}),
            docker_image=data.get('docker_image', 'mcr.microsoft.com/playwright/python:v1.48.0-jammy'),
            test_directory=data.get('test_directory', 'tests/approved/'),
            artifacts_directory=data.get('artifacts_directory', 'captures/'),
            exit_code=data.get('exit_code', 0),
            console_output=data.get('console_output', ''),
            started_at=datetime.fromisoformat(data['started_at']),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None
        )