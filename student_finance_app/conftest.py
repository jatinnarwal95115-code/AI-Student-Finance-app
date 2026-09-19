"""
conftest.py — pytest configuration for student_finance_app.

Adds the project root to sys.path so that all test files can import
from models/, services/, ai/, and utils/ without needing package installs.
"""

import sys
import os

# Insert the project root (the folder containing app.py) onto sys.path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
