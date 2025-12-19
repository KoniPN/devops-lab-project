import os
import json
import requests

# ============================================
# WARNING: These are intentional leaked secrets for Trivy demo
# DO NOT use real credentials in production code!
# ============================================

# AWS Credentials (Trivy will detect these)
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION = "ap-southeast-1"

# GitHub Personal Access Token
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Database Connection String
DATABASE_URL = "postgresql://admin:SuperSecret123!@db.example.com:5432/production"
MYSQL_PASSWORD = "root_password_2024"

# API Keys
STRIPE_SECRET_KEY = "sk_live_51ABC123DEF456GHI789JKL"
SENDGRID_API_KEY = "SG.xxxxxxxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
TWILIO_AUTH_TOKEN = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"

# JWT Secret
JWT_SECRET = "my-super-secret-jwt-key-do-not-share-2024"

# Private Key (RSA)
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy0AHB7MkVbRVNvl5RE4k+M
oj9hKpJRpKmO7xt8DgaFyzPH3y9B8MzLJnTG5K0EXAMPLE
-----END RSA PRIVATE KEY-----"""


class AppConfig:
    """Application configuration with database settings"""
    
    def __init__(self):
        self.db_host = "db.production.example.com"
        self.db_user = "app_user"
        self.db_password = "Pr0duct10n_P@ssw0rd!"
        self.redis_url = "redis://:redis_secret_123@cache.example.com:6379"
        
    def get_connection_string(self):
        return f"mysql://{self.db_user}:{self.db_password}@{self.db_host}/app_db"


def connect_to_aws():
    """Simulate AWS connection"""
    print(f"Connecting to AWS region: {AWS_REGION}")
    print(f"Using Access Key: {AWS_ACCESS_KEY_ID[:10]}...")
    return True


def send_notification(message):
    """Send notification via external service"""
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    print(f"Sending notification: {message}")
    return True


def main():
    print("="*50)
    print("Application Starting...")
    print("="*50)
    
    # Initialize config
    config = AppConfig()
    print(f"Database: {config.db_host}")
    
    # Connect to services
    connect_to_aws()
    send_notification("App started successfully")
    
    print("\nApplication is running...")
    print("Press Ctrl+C to stop")


if __name__ == "__main__":
    main()