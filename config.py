import os
import secrets

# Generate a random secret key if not provided
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
