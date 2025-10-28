"""
Generate Command Handler

Handles the 'generate' command for creating test cases from web applications.
"""

import argparse
from pathlib import Path
from typing import Dict, Any

from ..lib.error_handling import AiTesterError, validate_url, print_success, print_info
from ..lib.file_utils import ensure_directory_exists, save_test_file
from ..services.playwright_service import PlaywrightService
from ..services.gemini_service import GeminiService


def run_generate_command(args: argparse.Namespace, project_root: Path) -> int:
    """
    Execute the generate command.
    
    Args:
        args: Parsed command line arguments
        project_root: Project root directory
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    print(f"🚀 Generating tests for: {args.url}")
    print(f"   Depth: {args.depth}")
    print(f"   Max pages: {args.max_pages}")
    print(f"   Headless: {args.headless}")
    print(f"   Timeout: {args.timeout}ms")
    print(f"   Rate limit delay: {args.rate_limit_delay}s")
    
    # Validate URL
    validate_url(args.url)
    
    # Setup output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "tests" / "draft"
    
    print(f"   Output: {output_dir}")
    
    try:
        # Ensure output directory exists
        ensure_directory_exists(str(output_dir))
        
        # Initialize services
        print_info("Initializing Playwright service...")
        playwright_service = PlaywrightService(
            headless=args.headless,
            timeout=args.timeout
        )
        
        print_info("Initializing Gemini service...")
        gemini_service = GeminiService(rate_limit_delay=args.rate_limit_delay)
        
        # Capture page content
        print_info("Capturing page content...")
        captures_dir = project_root / "captures"
        page_capture = playwright_service.capture_page_sync(
            args.url, 
            str(captures_dir)
        )
        
        # Generate test cases using AI
        print_info("Generating test cases with AI...")
        test_cases = gemini_service.generate_test_cases(page_capture)
        
        # Save test files
        saved_files = []
        for i, test_case in enumerate(test_cases, 1):
            filename = f"test_{test_case.name}_{i}.py"
            file_path = save_test_file(
                test_case.test_code,
                filename,
                str(output_dir)
            )
            saved_files.append(file_path)
            print_success(f"Saved test case: {file_path}")
        
        # Summary
        print()
        print_success(f"Test generation complete!")
        print(f"   📊 Generated: {len(test_cases)} test cases")
        print(f"   📁 Saved to: {output_dir}")
        print(f"   📸 Screenshot: {page_capture.screenshot_path}")
        print()
        print("Next steps:")
        print("1. Review the generated tests in the draft directory")
        print("2. Edit them if needed")
        print("3. Use 'ai-tester review' to approve them")
        print("4. Use 'ai-tester execute' to run approved tests")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test generation failed: {e}")
        return 1