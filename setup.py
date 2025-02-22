"""
This is a setup script for py2app.
"""
from setuptools import setup

APP = ['macOS.py']  # Replace with your main script filename
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,  # This makes drag-and-drop work
    'packages': [],          # List any extra packages if needed
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
