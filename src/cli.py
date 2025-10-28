"""
CLI Framework

Main entry point and command routing for AI Tester.
"""

import argparse
import sys
from typing import List, Optional
from pathlib import Path

from .lib.error_handling import AiTesterError
from .lib.file_utils import get_project_root


def handle_errors(func):
    """Decorator to handle errors in CLI functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AiTesterError as e:
            print(f"Error: {e}")
            return e.error_code
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 1
    return wrapper


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with all commands."""
    parser = argparse.ArgumentParser(
        prog='ai-tester',
        description='AI-driven Playwright test automation system',
        epilog='Use "ai-tester <command> --help" for detailed command help'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='AI Tester 1.0.0'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--project-root',
        type=str,
        help='Override project root directory (defaults to current directory)'
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='<command>'
    )
    
    # Generate command
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate test cases from a web application',
        description='Analyze a web application and generate draft test cases using AI'
    )
    
    generate_parser.add_argument(
        'url',
        help='URL of the web application to analyze'
    )
    
    generate_parser.add_argument(
        '--depth',
        type=int,
        default=2,
        help='Maximum crawl depth (default: 2)'
    )
    
    generate_parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Maximum number of pages to analyze (default: 10)'
    )
    
    generate_parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    
    generate_parser.add_argument(
        '--no-headless',
        action='store_false',
        dest='headless',
        help='Run browser with GUI (useful for debugging)'
    )
    
    generate_parser.add_argument(
        '--timeout',
        type=int,
        default=30000,
        help='Page load timeout in milliseconds (default: 30000)'
    )
    
    generate_parser.add_argument(
        '--rate-limit-delay',
        type=float,
        default=2.0,
        help='Delay in seconds between API calls to avoid rate limits (default: 2.0)'
    )
    
    generate_parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for generated tests (defaults to tests/draft/)'
    )
    
    # Review command
    review_parser = subparsers.add_parser(
        'review',
        help='Review and approve draft test cases',
        description='Interactive review of draft test cases for approval or rejection'
    )
    
    review_parser.add_argument(
        '--test-file',
        type=str,
        help='Specific test file to review (if not provided, reviews all draft tests)'
    )
    
    review_parser.add_argument(
        '--auto-approve',
        action='store_true',
        help='Automatically approve all tests (use with caution)'
    )
    
    review_parser.add_argument(
        '--batch-size',
        type=int,
        default=5,
        help='Number of tests to review at once (default: 5)'
    )
    
    # Execute command
    execute_parser = subparsers.add_parser(
        'execute',
        help='Execute approved test cases',
        description='Run approved test cases and generate test reports'
    )
    
    execute_parser.add_argument(
        '--test-file',
        type=str,
        help='Specific test file to execute (if not provided, runs all approved tests)'
    )
    
    execute_parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run tests in parallel'
    )
    
    execute_parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of parallel workers (default: 1, requires --parallel)'
    )
    
    execute_parser.add_argument(
        '--browser',
        choices=['chromium', 'firefox', 'webkit'],
        default='chromium',
        help='Browser engine to use (default: chromium)'
    )
    
    execute_parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    
    execute_parser.add_argument(
        '--no-headless',
        action='store_false',
        dest='headless',
        help='Run browser with GUI (useful for debugging)'
    )
    
    execute_parser.add_argument(
        '--capture-screenshots',
        action='store_true',
        help='Capture screenshots on test failures'
    )
    
    execute_parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for test reports (defaults to reports/)'
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        'status',
        help='Show project status and test statistics',
        description='Display current status of draft tests, approved tests, and recent runs'
    )
    
    status_parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed statistics and test breakdowns'
    )
    
    # Clean command
    clean_parser = subparsers.add_parser(
        'clean',
        help='Clean up generated files',
        description='Remove draft tests, reports, or other generated files'
    )
    
    clean_parser.add_argument(
        'target',
        choices=['drafts', 'reports', 'captures', 'all'],
        help='What to clean (drafts, reports, captures, or all)'
    )
    
    clean_parser.add_argument(
        '--force',
        action='store_true',
        help='Force cleanup without confirmation'
    )
    
    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command arguments and raise errors for invalid combinations."""
    
    # Validate generate command
    if args.command == 'generate':
        if args.depth < 1 or args.depth > 10:
            raise AiTesterError("Crawl depth must be between 1 and 10")
        
        if args.max_pages < 1 or args.max_pages > 100:
            raise AiTesterError("Max pages must be between 1 and 100")
        
        if args.timeout < 5000 or args.timeout > 120000:
            raise AiTesterError("Timeout must be between 5000 and 120000 milliseconds")
    
    # Validate execute command
    elif args.command == 'execute':
        if args.parallel and args.workers < 1:
            raise AiTesterError("Number of workers must be at least 1 when using parallel execution")
        
        if not args.parallel and args.workers > 1:
            raise AiTesterError("Cannot specify workers without --parallel flag")
    
    # Validate review command
    elif args.command == 'review':
        if args.batch_size < 1 or args.batch_size > 50:
            raise AiTesterError("Batch size must be between 1 and 50")


def setup_project_root(args: argparse.Namespace) -> Path:
    """Setup and validate project root directory."""
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = get_project_root()
    
    if not project_root.exists():
        raise AiTesterError(f"Project root directory does not exist: {project_root}")
    
    return project_root


@handle_errors
def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI application."""
    
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        # Validate arguments
        validate_args(args)
        
        # Setup project root
        project_root = setup_project_root(args)
        
        # Import and execute appropriate command
        # These imports are done here to avoid circular imports
        # and to ensure faster startup for help/version commands
        
        if args.command == 'generate':
            from .commands.generate import run_generate_command
            return run_generate_command(args, project_root)
        
        elif args.command == 'review':
            from .commands.review import run_review_command
            return run_review_command(args, project_root)
        
        elif args.command == 'execute':
            from .commands.execute import run_execute_command
            return run_execute_command(args, project_root)
        
        elif args.command == 'status':
            from .commands.status import run_status_command
            return run_status_command(args, project_root)
        
        elif args.command == 'clean':
            from .commands.clean import run_clean_command
            return run_clean_command(args, project_root)
        
        else:
            # This should never happen due to argparse validation
            raise AiTesterError(f"Unknown command: {args.command}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130  # Standard exit code for Ctrl+C
    
    except AiTesterError as e:
        print(f"Error: {e}")
        return 1
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cli_main() -> None:
    """Entry point for console script."""
    sys.exit(main())


if __name__ == '__main__':
    cli_main()