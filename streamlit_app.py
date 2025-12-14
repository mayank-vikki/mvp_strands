"""
Streamlit App Entry Point
Imports and runs the main application from app/streamlit_app.py
This file is used by Streamlit Cloud deployment.
"""

import sys
from pathlib import Path

# Add the app directory to the path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Import and run the main app
from streamlit_app import *  # noqa: F401, F403
