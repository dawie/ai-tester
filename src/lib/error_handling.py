"""
Error Handling Utilities

Implements fail-fast error handling approach per constitution and clarifications.
"""

import sys
from datetime import datetime
from typing import Optional


class AiTesterError(Exception):
    """Base exception for AI Tester application."""
    
    def __init__(self, message: str, error_code: int = 1):
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.utcnow()


class ApiError(AiTesterError):
    """Gemini API related errors - fail immediately per clarifications."""
    
    def __init__(self, message: str, api_response: Optional[dict] = None):
        super().__init__(message, error_code=2)
        self.api_response = api_response


class TargetAppError(AiTesterError):
    """Target web application errors - log and fail gracefully per clarifications."""
    
    def __init__(self, message: str, url: str, status_code: Optional[int] = None):
        super().__init__(message, error_code=1)
        self.url = url
        self.status_code = status_code


class FileSystemError(AiTesterError):
    """File system related errors."""
    
    def __init__(self, message: str, file_path: str):
        super().__init__(message, error_code=3)
        self.file_path = file_path


class ValidationError(AiTesterError):
    """Input validation errors."""
    
    def __init__(self, message: str, invalid_input: str):
        super().__init__(message, error_code=4)
        self.invalid_input = invalid_input


def log_error(error: Exception, context: str = "") -> None:
    """
    Log error details with timestamp.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    timestamp = datetime.utcnow().isoformat()
    error_type = type(error).__name__
    
    print(f"❌ [{timestamp}] {error_type}: {str(error)}")
    if context:
        print(f"   Context: {context}")
    
    # For API errors, include response details if available
    if isinstance(error, ApiError) and error.api_response:
        print(f"   API Response: {error.api_response}")
    
    # For target app errors, include URL and status code
    if isinstance(error, TargetAppError):
        print(f"   Target URL: {error.url}")
        if error.status_code:
            print(f"   HTTP Status: {error.status_code}")


def fail_fast(error: Exception, context: str = "") -> None:
    """
    Log error and exit immediately (fail-fast approach).
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    log_error(error, context)
    
    # Determine exit code based on error type
    exit_code = 1
    if isinstance(error, AiTesterError):
        exit_code = error.error_code
    
    print(f"❌ Exiting with code {exit_code}")
    sys.exit(exit_code)


def handle_api_error(error: Exception, operation: str) -> None:
    """
    Handle Gemini API errors with immediate failure per clarifications.
    
    Args:
        error: The API-related exception
        operation: Description of the operation that failed
    """
    error_str = str(error)
    
    # Log the actual error for debugging
    print(f"🔍 Debug - Actual API error: {error_str}")
    print(f"🔍 Debug - Error type: {type(error).__name__}")
    
    if "rate" in error_str.lower() or "quota" in error_str.lower() or "429" in error_str:
        api_error = ApiError(f"Gemini API rate limit exceeded during {operation}. Please check your quota at https://ai.google.dev/pricing")
    elif "auth" in error_str.lower() or "key" in error_str.lower() or "401" in error_str or "403" in error_str:
        api_error = ApiError(f"Gemini API authentication failed during {operation}. Please check your GOOGLE_API_KEY in .env file")
    elif "404" in error_str or "not found" in error_str.lower():
        api_error = ApiError(f"Gemini API model not found during {operation}. Please verify model access and name")
    else:
        api_error = ApiError(f"Gemini API error during {operation}: {error_str}")
    
    fail_fast(api_error, f"API operation: {operation}")


def handle_target_app_error(error: Exception, url: str, operation: str) -> None:
    """
    Handle target web application errors - log details and fail gracefully per clarifications.
    
    Args:
        error: The target app related exception
        url: The target URL that failed
        operation: Description of the operation that failed
    """
    status_code = None
    if hasattr(error, 'status_code'):
        status_code = error.status_code
    elif hasattr(error, 'response') and hasattr(error.response, 'status_code'):
        status_code = error.response.status_code
    
    target_error = TargetAppError(
        f"Target application error during {operation}: {str(error)}",
        url=url,
        status_code=status_code
    )
    
    fail_fast(target_error, f"Target URL: {url}, Operation: {operation}")


def validate_url(url: str) -> None:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError("URL cannot be empty", url)
    
    if not url.startswith(('http://', 'https://')):
        raise ValidationError("URL must start with http:// or https://", url)
    
    # Basic validation - more comprehensive validation happens in Playwright
    if ' ' in url:
        raise ValidationError("URL cannot contain spaces", url)


def validate_file_path(file_path: str, must_exist: bool = False) -> None:
    """
    Validate file path.
    
    Args:
        file_path: File path to validate
        must_exist: Whether the file must already exist
        
    Raises:
        ValidationError: If file path is invalid
        FileSystemError: If file doesn't exist when required
    """
    import os
    
    if not file_path:
        raise ValidationError("File path cannot be empty", file_path)
    
    if must_exist and not os.path.exists(file_path):
        raise FileSystemError(f"File does not exist: {file_path}", file_path)


def print_success(message: str) -> None:
    """Print success message with ✅ indicator per constitution."""
    print(f"✅ {message}")


def print_info(message: str) -> None:
    """Print info message with [*] indicator."""
    print(f"[*] {message}")


def print_warning(message: str) -> None:
    """Print warning message with ⚠️ indicator."""
    print(f"⚠️ {message}")