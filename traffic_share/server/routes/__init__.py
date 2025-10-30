"""
API Routes package
Import all route modules
"""

from traffic_share.server.routes import auth_routes
from traffic_share.server.routes import user_routes
from traffic_share.server.routes import traffic_routes
from traffic_share.server.routes import payment_routes
from traffic_share.server.routes import buyer_routes
from traffic_share.server.routes import admin_routes
from traffic_share.server.routes import system_routes
from traffic_share.server.routes import update_routes

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
