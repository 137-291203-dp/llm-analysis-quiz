"""
Setup script to initialize the project
"""
import os
import sys
import subprocess

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = ['downloads', 'temp', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ Created {directory}/")

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"  ✗ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """Install Python requirements"""
    print("\nInstalling Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("  ✓ Packages installed")
        return True
    except subprocess.CalledProcessError:
        print("  ✗ Failed to install packages")
        return False

def install_playwright():
    """Install Playwright browsers"""
    print("\nInstalling Playwright browsers...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("  ✓ Playwright browsers installed")
        return True
    except subprocess.CalledProcessError:
        print("  ✗ Failed to install Playwright browsers")
        return False

def check_env_file():
    """Check if .env file exists"""
    print("\nChecking environment configuration...")
    if os.path.exists('.env'):
        print("  ✓ .env file exists")
        return True
    else:
        print("  ⚠ .env file not found")
        print("  Creating .env from .env.example...")
        try:
            with open('.env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("  ✓ Created .env file")
            print("  ⚠ Please edit .env and fill in your credentials")
            return False
        except Exception as e:
            print(f"  ✗ Failed to create .env: {e}")
            return False

def main():
    """Run setup"""
    print("="*50)
    print("LLM Analysis Quiz - Setup")
    print("="*50)
    
    steps = [
        ("Python Version", check_python_version),
        ("Directories", lambda: (create_directories(), True)[1]),
        ("Requirements", install_requirements),
        ("Playwright", install_playwright),
        ("Environment", check_env_file)
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Error in {step_name}: {e}")
            results.append(False)
    
    print("\n" + "="*50)
    print("Setup Summary")
    print("="*50)
    
    for (step_name, _), result in zip(steps, results):
        status = "✓" if result else "✗"
        print(f"{status} {step_name}")
    
    if all(results):
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your credentials")
        print("2. Run: python app.py")
        print("3. Test: python test_endpoint.py")
    else:
        print("\n⚠️  Setup completed with warnings")
        print("Please check the errors above and fix them")
        if not results[-1]:  # env file check failed
            print("\nDon't forget to edit .env with your credentials!")

if __name__ == "__main__":
    main()
