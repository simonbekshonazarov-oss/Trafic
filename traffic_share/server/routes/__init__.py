"""
API Routes package
Import all route modules
"""

from . import (
    auth_routes,
    user_routes,
    traffic_routes,
    payment_routes,
    buyer_routes,
    admin_routes,
    system_routes,
    update_routes
)

__all__ = [
    "auth_routes",
    "user_routes",
    "traffic_routes",
    "payment_routes",
    "buyer_routes",
    "admin_routes",
    "system_routes",
    "update_routes"
]
