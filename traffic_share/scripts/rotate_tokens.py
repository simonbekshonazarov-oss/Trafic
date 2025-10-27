"""
Rotate buyer tokens
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from traffic_share.server.database import get_db_context
from traffic_share.server.models import BuyerToken
from traffic_share.core.security import SecurityManager
from traffic_share.server.logger import logger


def rotate_buyer_token(buyer_id: int):
    """Rotate token for a specific buyer"""
    with get_db_context() as db:
        # Revoke old tokens
        old_tokens = db.query(BuyerToken).filter(
            BuyerToken.buyer_id == buyer_id,
            BuyerToken.is_revoked == False
        ).all()
        
        for token in old_tokens:
            token.is_revoked = True
        
        # Create new token
        plain_token = SecurityManager.generate_api_token(32)
        token_hash = SecurityManager.hash_token(plain_token)
        
        new_token = BuyerToken(
            buyer_id=buyer_id,
            token_hash=token_hash,
            description="Rotated token"
        )
        db.add(new_token)
        
        logger.info(f"Rotated token for buyer {buyer_id}")
        print(f"\n✅ New token for buyer {buyer_id}: {plain_token}\n")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python rotate_tokens.py <buyer_id>")
        sys.exit(1)
    
    try:
        buyer_id = int(sys.argv[1])
        rotate_buyer_token(buyer_id)
    except Exception as e:
        logger.error(f"Token rotation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
