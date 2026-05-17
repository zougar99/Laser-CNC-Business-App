#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for Laser PC Project 11
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Try different entry points
try:
    from laser_app_pc import LaserApp
    app = LaserApp()
    app.run()
except ImportError:
    try:
        from run_app import main
        main()
    except ImportError as e:
        print(f"Error: {e}")
