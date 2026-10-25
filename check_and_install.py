"""Quick script to check and install missing packages"""
import subprocess
import sys

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

# Required packages and their import names
packages = {
    'flask': 'flask',
    'flask-cors': 'flask_cors',
    'mysql-connector-python': 'mysql.connector',
    'tensorflow': 'tensorflow',
    'gensim': 'gensim',
    'numpy': 'numpy',
    'pandas': 'pandas',
    'nltk': 'nltk'
}

missing = []
for pkg, import_name in packages.items():
    if not check_package(pkg, import_name):
        missing.append(pkg)
        print(f"[X] {pkg} - NOT INSTALLED")
    else:
        print(f"[OK] {pkg} - installed")

if missing:
    print(f"\nMissing packages: {', '.join(missing)}")
    print("\nTo install, run in your terminal:")
    print(f"pip install {' '.join(missing)}")
    print("\nOr install all requirements:")
    print("pip install -r requirements.txt")
    sys.exit(1)
else:
    print("\n[OK] All required packages are installed!")
    sys.exit(0)
