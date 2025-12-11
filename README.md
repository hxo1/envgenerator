# Environment Generator

## Description
This repository contains an environment generator script that uses encrypted configuration and connects to remote hosts.

## Components

### o.py
The main script that:
- Decrypts configuration using AES-GCM encryption
- Uses PBKDF2 key derivation with SHA256
- Connects to remote hosts based on decrypted configuration
- Supports password-based authentication

## Requirements
- Python 3
- cryptography package

## Installation
```bash
pip install cryptography
```

## Usage
```bash
python3 o.py --password <PASSWORD>
```

## Setup
Refer to [SETUP.md](SETUP.md) for detailed setup instructions and configuration details.

## Security Notes
- Uses strong encryption (AES-256-GCM)
- Password-based key derivation with 100,000 iterations
- Encrypted configuration protects sensitive connection details
