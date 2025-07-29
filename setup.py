#!/usr/bin/env python3
"""
Setup script for Tathya Case Management System deployment
"""
import os
import sqlite3

def setup_database():
    """Initialize database for deployment"""
    if not os.path.exists('case_management.db'):
        print("Creating database...")
        from database import init_database
        init_database()
        print("Database initialized successfully")
    else:
        print("Database already exists")

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'exports', 'static/images']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

if __name__ == "__main__":
    print("Setting up Tathya Case Management System...")
    create_directories()
    setup_database()
    print("Setup complete!")