"""
Status Command Handler

Handles the 'status' command for showing project status and statistics.
"""

import argparse
from pathlib import Path

from ..lib.file_utils import count_test_files, get_latest_report_summary
from ..lib.error_handling import AiTesterError


def run_status_command(args: argparse.Namespace, project_root: Path) -> int:
    """
    Execute the status command.
    
    Args:
        args: Parsed command line arguments
        project_root: Project root directory
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    print("📊 AI Tester Project Status")
    print("=" * 40)
    
    # Count test files
    try:
        draft_count = count_test_files(project_root / "tests" / "draft")
        approved_count = count_test_files(project_root / "tests" / "approved")
        
        print(f"📝 Draft Tests: {draft_count}")
        print(f"✅ Approved Tests: {approved_count}")
        
    except Exception as e:
        print(f"⚠️  Could not count test files: {e}")
    
    # Show latest report summary
    try:
        report_summary = get_latest_report_summary(project_root / "reports")
        if report_summary:
            print(f"\n📋 Latest Test Run:")
            print(f"   Date: {report_summary.get('timestamp', 'Unknown')}")
            print(f"   Tests: {report_summary.get('total_tests', 0)}")
            print(f"   Passed: {report_summary.get('passed', 0)}")
            print(f"   Failed: {report_summary.get('failed', 0)}")
            print(f"   Success Rate: {report_summary.get('success_rate', 0):.1f}%")
        else:
            print("\n📋 No test runs found")
    
    except Exception as e:
        print(f"⚠️  Could not load report summary: {e}")
    
    # Show project structure
    print(f"\n📁 Project Structure:")
    print(f"   Root: {project_root}")
    print(f"   Tests: {project_root / 'tests'}")
    print(f"   Reports: {project_root / 'reports'}")
    print(f"   Captures: {project_root / 'captures'}")
    
    if args.detailed:
        print(f"\n🔍 Detailed Information:")
        
        # Check for environment file
        env_file = project_root / ".env"
        if env_file.exists():
            print(f"   ✅ Environment file found: {env_file}")
        else:
            print(f"   ⚠️  Environment file missing: {env_file}")
        
        # Check for Docker files
        dockerfile = project_root / "Dockerfile"
        docker_compose = project_root / "docker-compose.yml"
        
        if dockerfile.exists():
            print(f"   ✅ Dockerfile found: {dockerfile}")
        else:
            print(f"   ⚠️  Dockerfile missing: {dockerfile}")
        
        if docker_compose.exists():
            print(f"   ✅ Docker Compose found: {docker_compose}")
        else:
            print(f"   ⚠️  Docker Compose missing: {docker_compose}")
    
    return 0