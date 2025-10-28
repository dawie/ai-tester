"""
File Utilities

Manages directory structure for draft/approved test separation and file operations.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..lib.error_handling import FileSystemError, ValidationError, print_success, print_info


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to project root directory
    """
    # Start from current file and search up for project indicators
    current_path = Path(__file__).parent.parent.parent
    
    # Look for project indicators
    indicators = ['Dockerfile', 'docker-compose.yml', 'requirements.txt', '.git']
    
    while current_path != current_path.parent:
        if any((current_path / indicator).exists() for indicator in indicators):
            return current_path
        current_path = current_path.parent
    
    # Default to current working directory if no indicators found
    return Path.cwd()


def count_test_files(directory: Path) -> int:
    """
    Count test files in a directory.
    
    Args:
        directory: Directory to count files in
        
    Returns:
        Number of test files found
    """
    if not directory.exists():
        return 0
    
    count = 0
    for file_path in directory.rglob("*.py"):
        if file_path.stem.startswith("test_") or file_path.stem.endswith("_test"):
            count += 1
    
    return count


def get_latest_report_summary(reports_dir: Path) -> Optional[dict]:
    """
    Get summary of the latest test report.
    
    Args:
        reports_dir: Directory containing test reports
        
    Returns:
        Dictionary with report summary or None if no reports found
    """
    if not reports_dir.exists():
        return None
    
    # Find the most recent JSON report file
    json_files = list(reports_dir.glob("*.json"))
    if not json_files:
        return None
    
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        # Extract summary information
        summary = {
            'timestamp': data.get('timestamp', 'Unknown'),
            'total_tests': data.get('total_tests', 0),
            'passed': data.get('passed', 0),
            'failed': data.get('failed', 0),
            'success_rate': data.get('success_rate', 0.0)
        }
        
        return summary
    except (json.JSONDecodeError, KeyError, IOError):
        return None


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory_path: Path to directory
        
    Raises:
        FileSystemError: If directory cannot be created
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise FileSystemError(f"Cannot create directory {directory_path}: {str(e)}", directory_path)


def get_draft_tests_directory() -> str:
    """Get path to draft tests directory."""
    return os.path.join("tests", "draft")


def get_approved_tests_directory() -> str:
    """Get path to approved tests directory.""" 
    return os.path.join("tests", "approved")


def get_captures_directory() -> str:
    """Get path to captures directory."""
    return "captures"


def get_reports_directory() -> str:
    """Get path to reports directory."""
    return "reports"


def generate_test_filename(url: str, timestamp: Optional[datetime] = None) -> str:
    """
    Generate test filename from URL and timestamp.
    
    Args:
        url: Target URL
        timestamp: Timestamp for filename (defaults to now)
        
    Returns:
        Generated filename
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # Sanitize URL for filename
    sanitized_domain = url.replace("https://", "").replace("http://", "")
    sanitized_domain = sanitized_domain.replace("/", "_").replace(":", "_")
    sanitized_domain = "".join(c for c in sanitized_domain if c.isalnum() or c in "_-")
    
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    return f"test_{sanitized_domain}_{timestamp_str}.py"


def generate_capture_filename(url: str, extension: str, timestamp: Optional[datetime] = None) -> str:
    """
    Generate capture filename from URL and timestamp.
    
    Args:
        url: Target URL
        extension: File extension (html, png, etc.)
        timestamp: Timestamp for filename (defaults to now)
        
    Returns:
        Generated filename
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # Sanitize URL for filename
    sanitized_domain = url.replace("https://", "").replace("http://", "")
    sanitized_domain = sanitized_domain.replace("/", "_").replace(":", "_") 
    sanitized_domain = "".join(c for c in sanitized_domain if c.isalnum() or c in "_-")
    
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    return f"{sanitized_domain}_{timestamp_str}.{extension}"


def save_test_file(test_code: str, filename: str, directory: str = None) -> str:
    """
    Save test code to file in appropriate directory.
    
    Args:
        test_code: Python test code to save
        filename: Filename for the test
        directory: Target directory (defaults to draft)
        
    Returns:
        Full path to saved file
        
    Raises:
        FileSystemError: If file cannot be saved
    """
    if directory is None:
        directory = get_draft_tests_directory()
    
    ensure_directory_exists(directory)
    
    file_path = os.path.join(directory, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(test_code)
        print_success(f"Test saved to {file_path}")
        return file_path
    except OSError as e:
        raise FileSystemError(f"Cannot save test file {file_path}: {str(e)}", file_path)


def move_test_to_approved(draft_file_path: str) -> str:
    """
    Move test file from draft to approved directory.
    
    Args:
        draft_file_path: Path to draft test file
        
    Returns:
        New path in approved directory
        
    Raises:
        FileSystemError: If file cannot be moved
        ValidationError: If file is not in draft directory
    """
    if not os.path.exists(draft_file_path):
        raise FileSystemError(f"Draft file does not exist: {draft_file_path}", draft_file_path)
    
    # Ensure file is in draft directory
    draft_dir = get_draft_tests_directory()
    if not os.path.abspath(draft_file_path).startswith(os.path.abspath(draft_dir)):
        raise ValidationError(f"File is not in draft directory: {draft_file_path}", draft_file_path)
    
    # Get filename and create approved path
    filename = os.path.basename(draft_file_path)
    approved_dir = get_approved_tests_directory()
    ensure_directory_exists(approved_dir)
    approved_file_path = os.path.join(approved_dir, filename)
    
    # Check if approved file already exists
    if os.path.exists(approved_file_path):
        raise FileSystemError(f"Approved file already exists: {approved_file_path}", approved_file_path)
    
    try:
        shutil.move(draft_file_path, approved_file_path)
        print_success(f"Test approved: {approved_file_path}")
        return approved_file_path
    except OSError as e:
        raise FileSystemError(f"Cannot move file {draft_file_path} to {approved_file_path}: {str(e)}", draft_file_path)


def list_test_files(directory: str) -> List[str]:
    """
    List all test files in a directory.
    
    Args:
        directory: Directory to scan
        
    Returns:
        List of test file paths
    """
    if not os.path.exists(directory):
        return []
    
    test_files = []
    for filename in os.listdir(directory):
        if filename.startswith('test_') and filename.endswith('.py'):
            test_files.append(os.path.join(directory, filename))
    
    return sorted(test_files)


def get_test_file_count(directory: str) -> int:
    """
    Get count of test files in directory.
    
    Args:
        directory: Directory to count
        
    Returns:
        Number of test files
    """
    return len(list_test_files(directory))


def validate_test_file_syntax(file_path: str) -> bool:
    """
    Validate that test file has correct Python syntax.
    
    Args:
        file_path: Path to test file
        
    Returns:
        True if syntax is valid
        
    Raises:
        ValidationError: If syntax is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for basic pytest patterns
        if not content.strip():
            raise ValidationError("Test file is empty", file_path)
        
        if 'def test_' not in content:
            raise ValidationError("Test file must contain at least one test function (def test_...)", file_path)
        
        # Try to compile the Python code
        compile(content, file_path, 'exec')
        return True
        
    except SyntaxError as e:
        raise ValidationError(f"Python syntax error in {file_path}: {str(e)}", file_path)
    except OSError as e:
        raise FileSystemError(f"Cannot read file {file_path}: {str(e)}", file_path)


def save_json_metadata(data: dict, filename: str, directory: str) -> str:
    """
    Save metadata as JSON file.
    
    Args:
        data: Data to save
        filename: JSON filename
        directory: Target directory
        
    Returns:
        Full path to saved file
        
    Raises:
        FileSystemError: If file cannot be saved
    """
    ensure_directory_exists(directory)
    file_path = os.path.join(directory, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return file_path
    except (OSError, json.JSONEncodeError) as e:
        raise FileSystemError(f"Cannot save JSON file {file_path}: {str(e)}", file_path)


def load_json_metadata(file_path: str) -> dict:
    """
    Load metadata from JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded data
        
    Raises:
        FileSystemError: If file cannot be loaded
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise FileSystemError(f"Cannot load JSON file {file_path}: {str(e)}", file_path)