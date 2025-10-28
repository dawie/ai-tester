"""
Clean Command Handler

Handles the 'clean' command for removing generated files.
"""

import argparse
import shutil
from pathlib import Path

from ..lib.error_handling import AiTesterError


def run_clean_command(args: argparse.Namespace, project_root: Path) -> int:
    """
    Execute the clean command.
    
    Args:
        args: Parsed command line arguments
        project_root: Project root directory
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    print(f"🧹 Cleaning {args.target}")
    
    # Define directories to clean
    directories_to_clean = []
    
    if args.target == 'drafts' or args.target == 'all':
        directories_to_clean.append(project_root / "tests" / "draft")
    
    if args.target == 'reports' or args.target == 'all':
        directories_to_clean.append(project_root / "reports")
    
    if args.target == 'captures' or args.target == 'all':
        directories_to_clean.append(project_root / "captures")
    
    # Confirm cleanup unless forced
    if not args.force:
        print("\nDirectories to clean:")
        for directory in directories_to_clean:
            if directory.exists():
                file_count = len(list(directory.rglob("*"))) if directory.is_dir() else 0
                print(f"   {directory} ({file_count} files)")
            else:
                print(f"   {directory} (does not exist)")
        
        response = input("\nProceed with cleanup? [y/N]: ").strip().lower()
        if response not in ['y', 'yes']:
            print("Cleanup cancelled")
            return 0
    
    # Perform cleanup
    cleaned_count = 0
    for directory in directories_to_clean:
        if directory.exists():
            try:
                file_count = len(list(directory.rglob("*"))) if directory.is_dir() else 0
                
                # Remove all files in directory but keep the directory structure
                for item in directory.iterdir():
                    if item.is_file():
                        item.unlink()
                        cleaned_count += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        cleaned_count += len(list(item.rglob("*"))) if item.exists() else 0
                
                print(f"   ✅ Cleaned {directory} ({file_count} files removed)")
                
            except Exception as e:
                print(f"   ❌ Failed to clean {directory}: {e}")
                return 1
        else:
            print(f"   ⚠️  Directory does not exist: {directory}")
    
    print(f"\n🎉 Cleanup complete! Removed {cleaned_count} files")
    return 0