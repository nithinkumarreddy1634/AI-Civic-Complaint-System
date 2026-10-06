"""
Root pytest configuration for CivicAI.
Ensures backend package is on Python sys.path and inherits conftest fixtures.
"""
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

pytest_plugins = ["backend.tests.conftest"]
