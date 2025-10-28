"""
Page Capture Model

Represents a snapshot of web page state used for AI analysis context.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CaptureMetadata:
    """Metadata about the page capture process."""
    browser_name: str = "chromium"  # chromium, firefox, webkit
    viewport_width: int = 1280
    viewport_height: int = 720
    user_agent: str = ""
    load_time_ms: int = 0
    network_idle_time_ms: int = 0


@dataclass
class ErrorInfo:
    """Information about capture errors."""
    error_type: str  # NETWORK_ERROR, TIMEOUT, HTTP_ERROR
    error_code: Optional[int] = None  # HTTP status code if applicable
    error_message: str = ""
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    retry_attempted: bool = False  # Always False per fail-fast policy


@dataclass
class PageCapture:
    """Snapshot of web page state used for AI analysis context."""
    
    id: str  # Unique identifier (timestamp-based)
    url: str  # Target web application URL
    html_content: str  # Captured DOM HTML (truncated if needed)
    screenshot_path: str  # Path to full-page screenshot file
    metadata: CaptureMetadata = field(default_factory=CaptureMetadata)
    captured_at: datetime = field(default_factory=datetime.utcnow)
    content_hash: str = ""  # SHA256 hash for deduplication
    error_info: Optional[ErrorInfo] = None
    
    def __post_init__(self):
        """Validate page capture data and generate content hash."""
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError(f"URL must be valid HTTP/HTTPS URL: {self.url}")
        
        # Generate content hash for deduplication
        if not self.content_hash:
            content_for_hash = self.html_content + self.url
            self.content_hash = hashlib.sha256(content_for_hash.encode()).hexdigest()
    
    def truncate_html(self, max_chars: int = 50000) -> None:
        """Truncate HTML content to prevent token overflow in AI prompts."""
        if len(self.html_content) > max_chars:
            self.html_content = self.html_content[:max_chars] + "\n<!-- HTML truncated for AI analysis -->"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'url': self.url,
            'html_content': self.html_content,
            'screenshot_path': self.screenshot_path,
            'metadata': {
                'browser_name': self.metadata.browser_name,
                'viewport_width': self.metadata.viewport_width,
                'viewport_height': self.metadata.viewport_height,
                'user_agent': self.metadata.user_agent,
                'load_time_ms': self.metadata.load_time_ms,
                'network_idle_time_ms': self.metadata.network_idle_time_ms
            },
            'captured_at': self.captured_at.isoformat(),
            'content_hash': self.content_hash,
            'error_info': {
                'error_type': self.error_info.error_type,
                'error_code': self.error_info.error_code,
                'error_message': self.error_info.error_message,
                'occurred_at': self.error_info.occurred_at.isoformat(),
                'retry_attempted': self.error_info.retry_attempted
            } if self.error_info else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PageCapture':
        """Create PageCapture from dictionary."""
        metadata = CaptureMetadata(
            browser_name=data['metadata']['browser_name'],
            viewport_width=data['metadata']['viewport_width'],
            viewport_height=data['metadata']['viewport_height'],
            user_agent=data['metadata']['user_agent'],
            load_time_ms=data['metadata']['load_time_ms'],
            network_idle_time_ms=data['metadata']['network_idle_time_ms']
        )
        
        error_info = None
        if data.get('error_info'):
            error_info = ErrorInfo(
                error_type=data['error_info']['error_type'],
                error_code=data['error_info']['error_code'],
                error_message=data['error_info']['error_message'],
                occurred_at=datetime.fromisoformat(data['error_info']['occurred_at']),
                retry_attempted=data['error_info']['retry_attempted']
            )
        
        return cls(
            id=data['id'],
            url=data['url'],
            html_content=data['html_content'],
            screenshot_path=data['screenshot_path'],
            metadata=metadata,
            captured_at=datetime.fromisoformat(data['captured_at']),
            content_hash=data['content_hash'],
            error_info=error_info
        )