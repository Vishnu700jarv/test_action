import os


# Environment detection
ENVIRONMENT = os.getenv('ENVIRONMENT', 'DEVELOPMENT').upper()

# Base configuration settings
DEBUG = False


# Override for development
if ENVIRONMENT == 'DEVELOPMENT':
    DEBUG = True
    from .dev import *
# Override for production
elif ENVIRONMENT == 'PRODUCTION':
    from .prod import *