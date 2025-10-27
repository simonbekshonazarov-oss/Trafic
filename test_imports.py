#!/usr/bin/env python3
"""Test all critical imports"""

import sys

print("Testing imports...")

tests = []

# Test 1: Core imports
try:
    from traffic_share.core import constants, exceptions, security
    tests.append(("Core modules", True, "OK"))
except Exception as e:
    tests.append(("Core modules", False, str(e)))

# Test 2: Server config
try:
    from traffic_share.server.config import Settings
    tests.append(("Server config", True, "OK"))
except Exception as e:
    tests.append(("Server config", False, str(e)))

# Test 3: Database
try:
    from traffic_share.server.database import Base
    tests.append(("Database setup", True, "OK"))
except Exception as e:
    tests.append(("Database setup", False, str(e)))

# Test 4: Models
try:
    from traffic_share.server.models import User, Buyer, Package
    tests.append(("Database models", True, "OK"))
except Exception as e:
    tests.append(("Database models", False, str(e)))

# Test 5: Schemas
try:
    from traffic_share.server.schemas import RegisterRequest, TokenResponse
    tests.append(("Pydantic schemas", True, "OK"))
except Exception as e:
    tests.append(("Pydantic schemas", False, str(e)))

# Test 6: Services
try:
    from traffic_share.server.services.auth_service import AuthService
    from traffic_share.server.services.payment_service import PaymentService
    tests.append(("Services", True, "OK"))
except Exception as e:
    tests.append(("Services", False, str(e)))

# Test 7: Routes
try:
    from traffic_share.server.routes import auth_routes, user_routes
    tests.append(("API Routes", True, "OK"))
except Exception as e:
    tests.append(("API Routes", False, str(e)))

print("\n" + "="*70)
print("IMPORT TEST NATIJALARI")
print("="*70)

passed = 0
failed = 0

for name, success, msg in tests:
    if success:
        print(f"✅ {name}: {msg}")
        passed += 1
    else:
        print(f"❌ {name}: {msg}")
        failed += 1

print("="*70)
print(f"Passed: {passed}/{len(tests)}")
print(f"Failed: {failed}/{len(tests)}")
print("="*70)

sys.exit(0 if failed == 0 else 1)

