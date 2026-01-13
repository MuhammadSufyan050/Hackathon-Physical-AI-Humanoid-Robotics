#!/usr/bin/env python3
"""
Script to test connection to Qdrant Cloud
"""
import sys
import logging
from src.rag_validation.qdrant_client import qdrant_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to test Qdrant connection"""
    print("Testing Qdrant Cloud connection...")

    try:
        # Validate connection
        is_connected = qdrant_client.validate_connection()

        if is_connected:
            print("✅ Successfully connected to Qdrant Cloud")
            return 0
        else:
            print("❌ Failed to connect to Qdrant Cloud")
            return 1

    except Exception as e:
        logger.error(f"Error during connection test: {e}")
        print(f"❌ Error connecting to Qdrant Cloud: {e}")
        return 1
    finally:
        # Close the client
        qdrant_client.close()


if __name__ == "__main__":
    sys.exit(main())