# Git Repository and License Management System

A comprehensive Python-based system for managing Git repositories and generating license files with robust error handling and logging.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Supported Licenses](#supported-licenses)
- [Disclaimer](#disclaimer)
- [License](#license)

## Introduction

This system provides a complete solution for:
- Initializing and managing Git repositories
- Generating professional license files
- Performing common Git operations through an intuitive CLI
- Handling errors gracefully with comprehensive logging

Designed for developers, teams, and organizations that need a reliable way to manage repositories and ensure proper licensing from the start.

## Features

- **Git Repository Management**:
  - Initialize new repositories
  - Add files to staging
  - Create commits with messages
  - Push to remote repositories
  - Branch management (create, merge, checkout)
  - Pull changes from remotes

- **License Management**:
  - Generate standard open-source licenses
  - Automatic inclusion of current year and author info
  - Add license files to repository

- **Robust Infrastructure**:
  - Comprehensive error handling
  - Detailed logging
  - Type hints for better code maintenance
  - Configuration management

## Installation

### Prerequisites
- Python 3.10+
- Git installed and in system PATH

### Installation Steps
1. Clone the repository or download the script
2. (Optional) Create a virtual environment
3. Install required dependencies

## Usage

Run the application:
```bash
python git_manager.py
```

### Main Menu Options
1. **Initialize Repository**: Create a new Git repository
2. **Add Files**: Add files to staging area
3. **Commit Changes**: Commit staged changes with a message
4. **Push to Remote**: Push commits to a remote repository
5. **Create Branch**: Create and switch to a new branch
6. **Merge Branch**: Merge another branch into current branch
7. **Pull from Remote**: Pull changes from a remote repository
8. **Checkout Branch**: Switch to an existing branch
9. **List Branches**: View all branches in repository
10. **Generate License**: Create and add a license file
11. **Exit**: Quit the application

## Supported Licenses

The system supports the following open-source licenses:
- MIT License
- Apache License 2.0
- BSD 2-Clause License
- BSD 3-Clause License
- Apache License 1.1
- BSD 4-Clause License

Additional licenses can be added by creating a `licenses.json` file in the working directory.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is provided "as is" without warranty of any kind, express or implied. The authors are not responsible for any legal implications of generated license files or repository management actions. Users should verify that selected licenses meet their specific requirements.This is a personal project intended for educational purposes. The developer makes no guarantees about the reliability or security of this software. Use at your own risk.

Always review generated license files before using them in your projects.

