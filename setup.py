#!/usr/bin/env python3
"""
video2music Setup Script
Initializes the development environment for the video2music project.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd: str, description: str, cwd: str = None) -> bool:
    """Run a command and return True if successful."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js is not installed")
            return False
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm is not installed")
            return False
    except FileNotFoundError:
        print("❌ npm is not installed")
        return False
    
    return True

def setup_python_environment():
    """Set up Python virtual environment and install dependencies."""
    print("\n🐍 Setting up Python environment...")
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = r"venv\Scripts\activate"
        pip_cmd = r"venv\Scripts\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install Python dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    return True

def setup_frontend():
    """Set up frontend dependencies."""
    print("\n⚛️ Setting up frontend environment...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install npm dependencies
    if not run_command("npm install", "Installing frontend dependencies", cwd="frontend"):
        return False
    
    return True

def create_env_files():
    """Create environment files from examples."""
    print("\n📝 Creating environment files...")
    
    # Backend .env
    if not Path(".env").exists() and Path("env.example").exists():
        print("Creating .env from env.example...")
        with open("env.example", "r") as f:
            content = f.read()
        with open(".env", "w") as f:
            f.write(content)
        print("✅ Created .env file (please update with your credentials)")
    
    # Frontend .env
    frontend_env = Path("frontend/.env")
    frontend_example = Path("frontend/env.example")
    if not frontend_env.exists() and frontend_example.exists():
        print("Creating frontend/.env from frontend/env.example...")
        with open(frontend_example, "r") as f:
            content = f.read()
        with open(frontend_env, "w") as f:
            f.write(content)
        print("✅ Created frontend/.env file (please update with your credentials)")

def main():
    """Main setup function."""
    print("🎵 video2music Setup Script")
    print("=" * 50)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing tools.")
        sys.exit(1)
    
    if not setup_python_environment():
        print("\n❌ Python environment setup failed.")
        sys.exit(1)
    
    if not setup_frontend():
        print("\n❌ Frontend setup failed.")
        sys.exit(1)
    
    create_env_files()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update .env files with your Supabase credentials")
    print("2. Set up your Supabase project and database")
    print("3. Deploy the edge function to Supabase")
    print("4. Run 'python -m uvicorn app.main:app --reload' to start the backend")
    print("5. Run 'npm run dev' in the frontend directory to start the frontend")

if __name__ == "__main__":
    main() 