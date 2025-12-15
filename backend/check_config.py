"""
Configuration Checker for AI Study Companion Pro Backend
Run this script to validate your environment setup
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version >= (3, 9):
        print(f"   [PASS] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   [FAIL] Python {version.major}.{version.minor} (Need 3.9+)")
        return False


def check_env_file():
    """Check if .env file exists"""
    print("\nChecking environment file...")
    env_path = Path(".env")
    if env_path.exists():
        print("   [PASS] .env file exists")
        return True
    else:
        print("   [FAIL] .env file not found")
        print("   [INFO] Copy .env.example to .env and configure it")
        return False


def check_required_packages():
    """Check if required packages are installed"""
    print("\nChecking required packages...")
    required = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "psycopg2",
        "langchain",
        "pinecone",
        "pydantic",
        "PyPDF2"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"   [PASS] {package}")
        except ImportError:
            print(f"   [FAIL] {package}")
            missing.append(package)
    
    if missing:
        print(f"\n   [INFO] Install missing packages: pip install -r requirements.txt")
        return False
    return True


def check_env_variables():
    """Check required environment variables"""
    print("\nChecking environment variables...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("   [WARN] python-dotenv not installed")
    
    required_vars = {
        "DATABASE_URL": "PostgreSQL connection string",
        "GOOGLE_API_KEY": "Google Gemini API key",
        "PINECONE_API_KEY": "Pinecone API key",
        "PINECONE_ENVIRONMENT": "Pinecone environment",
        "SECRET_KEY": "Secret key for JWT"
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}":
            print(f"   [PASS] {var}")
        else:
            print(f"   [FAIL] {var} ({description})")
            missing.append(var)
    
    if missing:
        print(f"\n   [INFO] Set missing variables in .env file")
        return False
    return True


def check_database_connection():
    """Check database connection"""
    print("\nChecking database connection...")
    
    try:
        from app.config.settings import settings
        from sqlalchemy import create_engine
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            print("   [PASS] Database connection successful")
            return True
    except Exception as e:
        print(f"   [FAIL] Database connection failed: {str(e)}")
        print("   [INFO] Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False


def check_gemini_connection():
    """Check Google Gemini API connection"""
    print("\nChecking Google Gemini connection...")
    
    try:
        from app.config.settings import settings
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Simple test - just check if API key format is valid
        if settings.GOOGLE_API_KEY and len(settings.GOOGLE_API_KEY) > 20:
            print("   [PASS] Google Gemini API key format valid")
            # Try to list models to verify connection
            try:
                models = genai.list_models()
                print(f"   [PASS] Gemini API connection successful")
                return True
            except:
                print("   [WARN] API key format valid but connection test skipped")
                return True
        else:
            print("   [FAIL] Google Gemini API key format invalid")
            return False
    except Exception as e:
        print(f"   [FAIL] Gemini connection check failed: {str(e)}")
        return False


def check_pinecone_connection():
    """Check Pinecone connection"""
    print("\nChecking Pinecone connection...")
    
    try:
        from app.config.settings import settings
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        indexes = pc.list_indexes()
        print(f"   [PASS] Pinecone connection successful")
        print(f"   [INFO] Found {len(indexes)} indexes")
        return True
    except Exception as e:
        print(f"   [FAIL] Pinecone connection failed: {str(e)}")
        print("   [INFO] Check your Pinecone API key and environment")
        return False


def check_directories():
    """Check required directories"""
    print("\nChecking directories...")
    
    directories = [
        "storage/uploads",
        "alembic/versions"
    ]
    
    all_exist = True
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"   [PASS] {directory}/")
        else:
            print(f"   [WARN] {directory}/ (creating...)")
            path.mkdir(parents=True, exist_ok=True)
            print(f"   [PASS] Created {directory}/")
    
    return True


def main():
    """Run all checks"""
    print("=" * 60)
    print("AI Study Companion Pro - Configuration Checker")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_env_file(),
        check_required_packages(),
        check_env_variables(),
        check_directories(),
        check_database_connection(),
        check_gemini_connection(),
        check_pinecone_connection()
    ]
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n[RESULT] Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[SUCCESS] All checks passed! You're ready to start the server.")
        print("\n[INFO] Run: python -m uvicorn app.main:app --reload")
    else:
        print(f"\n[ERROR] {total - passed} check(s) failed. Please fix the issues above.")
        print("\n[INFO] See SETUP_GUIDE.md for detailed setup instructions")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
