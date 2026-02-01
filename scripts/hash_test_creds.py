import os
import sys
import importlib.util

# Dynamically import hash_password and hash_pin from api.py
spec = importlib.util.spec_from_file_location("api", os.path.join(os.path.dirname(__file__), "../api.py"))
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

# Test credentials
password = "testpass"
pin = "1234"

hashed_password = api.hash_password(password)
hashed_pin = api.hash_pin(pin)

print(f"Hashed password: {hashed_password}")
print(f"Hashed pin: {hashed_pin}")
