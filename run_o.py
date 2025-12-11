#!/usr/bin/env python3
"""
Wrapper script to execute o.py with custom cryptography module.
This script monkey-patches our ctypes-based crypto_wrapper to replace the cryptography package.

Usage: python3 run_o.py --password <password> [additional args...]
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our custom crypto wrapper
import crypto_wrapper

# Monkey-patch the cryptography module into sys.modules
sys.modules['cryptography'] = crypto_wrapper
sys.modules['cryptography.hazmat'] = crypto_wrapper.hazmat
sys.modules['cryptography.hazmat.primitives'] = crypto_wrapper.hazmat.primitives
sys.modules['cryptography.hazmat.primitives.ciphers'] = crypto_wrapper.hazmat.primitives.ciphers
sys.modules['cryptography.hazmat.primitives.hashes'] = crypto_wrapper.hazmat.primitives.hashes
sys.modules['cryptography.hazmat.primitives.kdf'] = crypto_wrapper.hazmat.primitives.kdf
sys.modules['cryptography.hazmat.primitives.kdf.pbkdf2'] = crypto_wrapper.hazmat.primitives.kdf.pbkdf2
sys.modules['cryptography.hazmat.backends'] = crypto_wrapper.hazmat.backends

# Now execute o.py with the provided arguments
o_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'o.py')
with open(o_py_path, 'r') as f:
    code = f.read()
    exec(code)
