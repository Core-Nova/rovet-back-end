#!/usr/bin/env python3
"""
Generate RSA key pair for JWT token signing.

This script generates a private key (for signing tokens) and a public key
(for verifying tokens in other microservices).

Usage:
    python scripts/generate_rsa_keys.py

The keys will be saved to:
    - private_key.pem (keep this secret!)
    - public_key.pem (can be shared with other services)
"""

import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def generate_rsa_key_pair():
    """Generate a 2048-bit RSA key pair."""
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem.decode('utf-8'), public_pem.decode('utf-8')


def main():
    """Generate and save RSA key pair."""
    print("Generating RSA key pair...")
    private_key, public_key = generate_rsa_key_pair()
    
    # Get the project root directory (parent of scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    private_key_path = os.path.join(project_root, "private_key.pem")
    public_key_path = os.path.join(project_root, "public_key.pem")
    
    # Write private key
    with open(private_key_path, 'w') as f:
        f.write(private_key)
    os.chmod(private_key_path, 0o600)  # Read/write for owner only
    print(f"✓ Private key saved to: {private_key_path}")
    print("  ⚠️  KEEP THIS SECRET! Never commit to version control!")
    
    # Write public key
    with open(public_key_path, 'w') as f:
        f.write(public_key)
    os.chmod(public_key_path, 0o644)  # Readable by all
    print(f"✓ Public key saved to: {public_key_path}")
    print("  ✓ This can be shared with other microservices")
    
    print("\nNext steps:")
    print("1. Add private_key.pem to .gitignore")
    print("2. Store private key securely (e.g., environment variable or secret manager)")
    print("3. Share public_key.pem with other microservices")
    print("4. Update JWT_PRIVATE_KEY and JWT_PUBLIC_KEY in your .env file")


if __name__ == "__main__":
    main()

