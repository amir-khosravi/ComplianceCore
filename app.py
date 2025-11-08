#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application file for Hugging Face Spaces deployment.
This file serves as the entry point for the CAELUS compliance system.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

# Import the main app
from app import main

if __name__ == "__main__":
    main() 