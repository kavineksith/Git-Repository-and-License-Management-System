#!/usr/bin/env python3
"""
Industrial-Grade Git Repository and License Management System
------------------------------------------------------------
A comprehensive system that provides:
- Full Git repository management
- License file generation
- Secure configuration
- Robust error handling and logging
"""

import os
import sys
import json
import logging
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum, auto

# ======================
# LOGGING CONFIGURATION
# ======================
class LogManager:
    """Centralized logging management for the application."""
    
    _configured = False
    
    @classmethod
    def configure_logging(cls, log_file: str = 'repo_manager.log', 
                         level: int = logging.DEBUG) -> None:
        """Configure application-wide logging."""
        if cls._configured:
            return
            
        # Create root logger
        logger = logging.getLogger()
        logger.setLevel(level)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        cls._configured = True
        logging.info("Logging configured successfully")

# Initialize logging
LogManager.configure_logging()

# ======================
# CUSTOM EXCEPTIONS
# ======================
class RepoManagerError(Exception):
    """Base exception for all repository management errors."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class GitOperationError(RepoManagerError):
    """Exception raised for Git-related errors."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class LicenseError(RepoManagerError):
    """Exception raised for license-related errors."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class InvalidLicenseError(LicenseError):
    """Exception raised for invalid license names."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class LicenseGenerationError(LicenseError):
    """Exception raised for license generation failures."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class ConfigError(RepoManagerError):
    """Exception raised for configuration issues."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

# ======================
# DATA STRUCTURES
# ======================
@dataclass
class LicenseInfo:
    """Represents license information."""
    name: str
    text: str
    requires_name: bool

class OperationType(Enum):
    """Enumeration of available operations."""
    INIT_REPO = auto()
    ADD_FILES = auto()
    COMMIT = auto()
    PUSH = auto()
    CREATE_BRANCH = auto()
    MERGE = auto()
    PULL = auto()
    CHECKOUT = auto()
    LIST_BRANCHES = auto()
    GENERATE_LICENSE = auto()

# ======================
# CORE SERVICES
# ======================
class GitManager:
    """Handles all Git repository operations."""
    
    def __init__(self, repo_path: str):
        """
        Initialize Git manager.
        
        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = Path(repo_path).absolute()
        self._validate_git_installation()
    
    def _validate_git_installation(self) -> None:
        """Verify Git is installed and available."""
        try:
            subprocess.run(["git", "--version"], check=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise GitOperationError("Git is not installed or not in PATH") from e
    
    def _run_git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run a Git command in the repository.
        
        Args:
            args: List of command arguments
            check: Whether to raise exception on failure
            
        Returns:
            CompletedProcess object
            
        Raises:
            GitOperationError: If command fails and check=True
        """
        try:
            return subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"Git command failed: {' '.join(args)}\n{e.stderr}"
            logging.error(error_msg)
            raise GitOperationError(error_msg) from e
    
    def init_repo(self) -> None:
        """Initialize a new Git repository."""
        if (self.repo_path / ".git").exists():
            raise GitOperationError(f"Repository already exists at {self.repo_path}")
        
        try:
            self.repo_path.mkdir(parents=True, exist_ok=True)
            self._run_git_command(["init"])
            logging.info(f"Initialized Git repository at {self.repo_path}")
        except OSError as e:
            raise GitOperationError(f"Failed to create repository: {e}") from e
    
    def add_files(self, file_paths: List[str]) -> None:
        """Add files to the staging area."""
        if not file_paths:
            raise GitOperationError("No files specified to add")
        
        # Convert to absolute paths relative to repo
        abs_paths = []
        for path in file_paths:
            abs_path = (self.repo_path / path).absolute()
            if not abs_path.exists():
                raise GitOperationError(f"File not found: {abs_path}")
            abs_paths.append(str(abs_path.relative_to(self.repo_path)))
        
        self._run_git_command(["add"] + abs_paths)
        logging.info(f"Added files to staging: {', '.join(abs_paths)}")
    
    def commit(self, message: str) -> None:
        """Create a commit with staged changes."""
        if not message:
            raise GitOperationError("Commit message cannot be empty")
        
        self._run_git_command(["commit", "-m", message])
        logging.info(f"Created commit: {message}")
    
    def push(self, remote: str = "origin", branch: str = "main") -> None:
        """Push changes to a remote repository."""
        self._run_git_command(["push", "-u", remote, branch])
        logging.info(f"Pushed changes to {remote}/{branch}")
    
    def create_branch(self, branch_name: str) -> None:
        """Create and checkout a new branch."""
        if not branch_name:
            raise GitOperationError("Branch name cannot be empty")
        
        self._run_git_command(["checkout", "-b", branch_name])
        logging.info(f"Created and switched to branch: {branch_name}")
    
    def merge(self, branch_name: str) -> None:
        """Merge another branch into current branch."""
        self._run_git_command(["merge", branch_name])
        logging.info(f"Merged branch: {branch_name}")
    
    def pull(self, remote: str = "origin", branch: str = "main") -> None:
        """Pull changes from remote repository."""
        self._run_git_command(["pull", remote, branch])
        logging.info(f"Pulled changes from {remote}/{branch}")
    
    def checkout(self, branch_name: str) -> None:
        """Checkout an existing branch."""
        self._run_git_command(["checkout", branch_name])
        logging.info(f"Switched to branch: {branch_name}")
    
    def list_branches(self) -> List[str]:
        """List all branches in the repository."""
        result = self._run_git_command(["branch"])
        branches = [b.strip() for b in result.stdout.split("\n") if b.strip()]
        current = [b for b in branches if b.startswith("*")]
        
        if current:
            current_branch = current[0][2:]
            branches = [b for b in branches if not b.startswith("*")]
            branches.insert(0, current_branch)
        
        logging.info(f"Found branches: {', '.join(branches)}")
        return branches
    
    def status(self) -> str:
        """Get repository status."""
        result = self._run_git_command(["status"])
        return result.stdout
    
    def is_repository(self) -> bool:
        """Check if the path is a Git repository."""
        return (self.repo_path / ".git").exists()

class LicenseManager:
    """Handles license generation and management."""
    
    def __init__(self, repo_path: str):
        """
        Initialize license manager.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = Path(repo_path).absolute()
        self.licenses = self._load_license_templates()
    
    def _load_license_templates(self) -> Dict[str, LicenseInfo]:
        """Load license templates from embedded data or file."""
        # Default licenses that will be used if licenses.json isn't found
        default_licenses = {
            "MIT": {
                "name": "MIT",
                "text": "MIT License\n\nCopyright (c) {year} {name}\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.",
                "requires_name": True
            },
            "Apache-2.0": {
                "name": "Apache-2.0",
                "text": "Apache License 2.0\n\nCopyright (c) {year} {name}\n\nLicensed under the Apache License, Version 2.0 (the \"License\"); you may not use this file except in compliance with the License. You may obtain a copy of the License at:\n\n    http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software distributed under the License is distributed on an \"AS IS\" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.",
                "requires_name": True
            },
            "BSD-2-Clause": {
                "name": "BSD-2-Clause",
                "text": "BSD 2-Clause License\n\nCopyright (c) {year} {name}\n\nRedistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:\n\n1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.\n\n2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.\n\nTHIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.",
                "requires_name": True
            },
            "BSD-3-Clause": {
                "name": "BSD-3-Clause",
                "text": "BSD 3-Clause License\n\nCopyright (c) {year} {name}\n\nRedistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:\n\n1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.\n\n2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.\n\n3. Neither the name of {name} nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.\n\nTHIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.",
                "requires_name": True
            },
            "Apache-1.1": {
                "name": "Apache-1.1",
                "text": "Apache License 1.1\n\nCopyright (c) {year} {name}\n\nThis product includes software developed by The Apache Group (http://www.apache.org/).\n\nRedistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:\n\n1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.\n\n2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.\n\n3. The end-user documentation included with the redistribution, if any, must include the following acknowledgment: \"This product includes software developed by the Apache Group (http://www.apache.org/).\"\n\n4. The names \"Apache Server\" and \"Apache Group\" must not be used to endorse or promote products derived from this software without prior written permission.\n\nTHIS SOFTWARE IS PROVIDED \"AS IS\" AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE APACHE GROUP OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.",
                "requires_name": True
            },
            "BSD-4-Clause": {
                "name": "BSD-4-Clause",
                "text": "BSD 4-Clause License\n\nCopyright (c) {year} {name}\n\nRedistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:\n\n1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.\n\n2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.\n\n3. All advertising materials mentioning features or use of this software must display the following acknowledgment: This product includes software developed by {name}.\n\n4. Neither the name of {name} nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.\n\nTHIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.",
                "requires_name": True
            }
        }

        try:
            # First try to load from licenses.json
            with open('licenses.json', 'r') as file:
                licenses = json.load(file)
            logging.info("Licenses loaded successfully from licenses.json")
            
            # Convert the loaded data to LicenseInfo objects
            return {
                name: LicenseInfo(
                    name=data.get('name', name),
                    text=data.get('text', ''),
                    requires_name=data.get('requires_name', True)
                )
                for name, data in licenses.items()
            }
        except FileNotFoundError:
            logging.warning("licenses.json file not found. Using default licenses.")
            # Convert default licenses to LicenseInfo objects
            return {
                name: LicenseInfo(
                    name=data['name'],
                    text=data['text'],
                    requires_name=data['requires_name']
                )
                for name, data in default_licenses.items()
            }
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from licenses.json: {e}")
            raise LicenseError(f"Error decoding JSON from licenses.json: {e}")
        except Exception as e:
            logging.error(f"Unexpected error loading licenses: {e}")
            raise LicenseError(f"Unexpected error loading licenses: {e}")
    
    def get_available_licenses(self) -> List[str]:
        """Get list of available license types."""
        return list(self.licenses.keys())
    
    def generate_license(self, license_name: str, author: str = None) -> str:
        """
        Generate license text.
        
        Args:
            license_name: Name of the license
            author: Author/organization name
            
        Returns:
            Generated license text
            
        Raises:
            InvalidLicenseError: If license name is invalid
            LicenseGenerationError: If generation fails
        """
        if license_name not in self.licenses:
            raise InvalidLicenseError(f"License '{license_name}' is not available")
        
        license_info = self.licenses[license_name]
        
        if license_info.requires_name and not author:
            raise LicenseGenerationError(
                f"License '{license_name}' requires an author/organization name"
            )
        
        try:
            year = datetime.now().year
            license_text = license_info.text.format(year=year, name=author or "")
            logging.info(f"Generated {license_name} license")
            return license_text
        except KeyError as e:
            raise LicenseGenerationError(f"Failed to format license text: {e}") from e
    
    def save_license_file(self, license_text: str) -> None:
        """
        Save license text to LICENSE file in repository.
        
        Args:
            license_text: License text to save
            
        Raises:
            LicenseError: If file cannot be saved
        """
        license_path = self.repo_path / "LICENSE"
        try:
            with open(license_path, "w") as f:
                f.write(license_text)
            logging.info(f"Saved LICENSE file to {license_path}")
        except IOError as e:
            raise LicenseError(f"Failed to save LICENSE file: {e}") from e

# ======================
# APPLICATION CORE
# ======================
class RepoManagerApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.git_manager = None
        self.license_manager = None
    
    def initialize_managers(self, repo_path: str) -> None:
        """
        Initialize Git and License managers.
        
        Args:
            repo_path: Path to the repository
        """
        self.git_manager = GitManager(repo_path)
        self.license_manager = LicenseManager(repo_path)
    
    def create_repository(self, repo_path: str) -> None:
        """
        Create a new Git repository.
        
        Args:
            repo_path: Path to create repository at
        """
        self.initialize_managers(repo_path)
        self.git_manager.init_repo()
    
    def generate_and_add_license(self, license_name: str, author: str) -> None:
        """
        Generate and add a license file to the repository.
        
        Args:
            license_name: Name of the license
            author: Author/organization name
        """
        if not self.git_manager or not self.license_manager:
            raise RepoManagerError("Managers not initialized")
        
        license_text = self.license_manager.generate_license(license_name, author)
        self.license_manager.save_license_file(license_text)
        self.git_manager.add_files(["LICENSE"])

# ======================
# USER INTERFACE
# ======================
class RepoManagerCLI:
    """Command-line interface for the repository manager."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.app = RepoManagerApp()
        self.operations = {
            '1': ('Initialize Repository', OperationType.INIT_REPO),
            '2': ('Add Files', OperationType.ADD_FILES),
            '3': ('Commit Changes', OperationType.COMMIT),
            '4': ('Push to Remote', OperationType.PUSH),
            '5': ('Create Branch', OperationType.CREATE_BRANCH),
            '6': ('Merge Branch', OperationType.MERGE),
            '7': ('Pull from Remote', OperationType.PULL),
            '8': ('Checkout Branch', OperationType.CHECKOUT),
            '9': ('List Branches', OperationType.LIST_BRANCHES),
            '10': ('Generate License', OperationType.GENERATE_LICENSE),
            '11': ('Exit', None)
        }
    
    def display_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("GIT REPOSITORY & LICENSE MANAGER".center(50))
        print("=" * 50)
        print("\nMain Menu:")
        for key, (description, _) in self.operations.items():
            print(f"{key}. {description}")
    
    def get_user_choice(self) -> Optional[OperationType]:
        """Get and validate user choice."""
        while True:
            choice = input("\nEnter your choice (1-11): ").strip()
            if choice in self.operations:
                return self.operations[choice][1]
            print("Invalid choice. Please enter a number between 1 and 11.")
    
    def handle_init_repo(self) -> None:
        """Handle repository initialization."""
        repo_path = input("Enter repository path: ").strip()
        if not repo_path:
            print("Error: Repository path cannot be empty")
            return
        
        try:
            self.app.create_repository(repo_path)
            print(f"Initialized Git repository at {repo_path}")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def handle_add_files(self) -> None:
        """Handle adding files to staging."""
        if not self._ensure_repository():
            return
        
        files = input("Enter file paths (space-separated): ").strip().split()
        if not files:
            print("Error: No files specified")
            return
        
        try:
            self.app.git_manager.add_files(files)
            print(f"Added {len(files)} files to staging")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def handle_commit(self) -> None:
        """Handle committing changes."""
        if not self._ensure_repository():
            return
        
        message = input("Enter commit message: ").strip()
        if not message:
            print("Error: Commit message cannot be empty")
            return
        
        try:
            self.app.git_manager.commit(message)
            print("Changes committed successfully")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def handle_push(self) -> None:
        """Handle pushing to remote."""
        if not self._ensure_repository():
            return
        
        remote = input("Enter remote name (default: origin): ").strip() or "origin"
        branch = input("Enter branch name (default: main): ").strip() or "main"
        
        try:
            self.app.git_manager.push(remote, branch)
            print(f"Pushed changes to {remote}/{branch}")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def handle_create_branch(self) -> None:
        """Handle branch creation."""
        if not self._ensure_repository():
            return
        
        branch = input("Enter new branch name: ").strip()
        if not branch:
            print("Error: Branch name cannot be empty")
            return
        
        try:
            self.app.git_manager.create_branch(branch)
            print(f"Created and switched to branch: {branch}")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def handle_merge(self) -> None:
        """Handle branch merging."""
        if not self._ensure_repository():
            return
        
        branch = input("Enter branch to merge: ").strip()
        if not branch:
            print("Error: Branch name cannot be empty")
            return
        
        try:
            self.app.git_manager.merge(branch)
            print(f"Merged branch: {branch}")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def handle_pull(self) -> None:
        """Handle pulling from remote."""
        if not self._ensure_repository():
            return
        
        remote = input("Enter remote name (default: origin): ").strip() or "origin"
        branch = input("Enter branch name (default: main): ").strip() or "main"
        
        try:
            self.app.git_manager.pull(remote, branch)
            print(f"Pulled changes from {remote}/{branch}")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def handle_checkout(self) -> None:
        """Handle branch checkout."""
        if not self._ensure_repository():
            return
        
        branch = input("Enter branch to checkout: ").strip()
        if not branch:
            print("Error: Branch name cannot be empty")
            return
        
        try:
            self.app.git_manager.checkout(branch)
            print(f"Switched to branch: {branch}")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def handle_list_branches(self) -> None:
        """Handle listing branches."""
        if not self._ensure_repository():
            return
        
        try:
            branches = self.app.git_manager.list_branches()
            print("\nBranches:")
            for branch in branches:
                print(f"  {branch}")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def handle_generate_license(self) -> None:
        """Handle license generation."""
        if not self._ensure_repository():
            return
        
        if not self.app.license_manager:
            print("Error: License manager not initialized")
            return
        
        print("\nAvailable licenses:")
        for license_name in self.app.license_manager.get_available_licenses():
            print(f"  {license_name}")
        
        license_name = input("\nEnter license name: ").strip()
        if not license_name:
            print("Error: License name cannot be empty")
            return
        
        author = input("Enter author/organization name: ").strip()
        
        try:
            self.app.generate_and_add_license(license_name, author)
            print(f"Generated and added {license_name} license")
        except RepoManagerError as e:
            print(f"Error: {e}")
    
    def _ensure_repository(self) -> bool:
        """Ensure we're working with a valid repository."""
        if not self.app.git_manager:
            print("Error: No repository initialized")
            return False
        
        if not self.app.git_manager.is_repository():
            print("Error: Not a Git repository")
            return False
        
        return True
    
    def run(self) -> None:
        """Run the CLI interface."""
        while True:
            try:
                self.display_menu()
                choice = self.get_user_choice()
                
                if choice is None:  # Exit
                    print("\nGoodbye!")
                    break
                
                if choice == OperationType.INIT_REPO:
                    self.handle_init_repo()
                elif choice == OperationType.ADD_FILES:
                    self.handle_add_files()
                elif choice == OperationType.COMMIT:
                    self.handle_commit()
                elif choice == OperationType.PUSH:
                    self.handle_push()
                elif choice == OperationType.CREATE_BRANCH:
                    self.handle_create_branch()
                elif choice == OperationType.MERGE:
                    self.handle_merge()
                elif choice == OperationType.PULL:
                    self.handle_pull()
                elif choice == OperationType.CHECKOUT:
                    self.handle_checkout()
                elif choice == OperationType.LIST_BRANCHES:
                    self.handle_list_branches()
                elif choice == OperationType.GENERATE_LICENSE:
                    self.handle_generate_license()
                
                # Prompt to continue
                if input("\nWould you like to perform another operation? (y/n): ").lower() != 'y':
                    print("\nGoodbye!")
                    break
                
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                break
            except Exception as e:
                print(f"\nAn unexpected error occurred: {e}")
                logging.error(f"CLI error: {e}")

# ======================
# MAIN EXECUTION
# ======================
if __name__ == "__main__":
    try:
        cli = RepoManagerCLI()
        cli.run()
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"\nFatal error: {e}")
        sys.exit(1)
    finally:
        sys.exit(0)
