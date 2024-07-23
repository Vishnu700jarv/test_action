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


# Ensure the logging directory exists
LOG_DIR = os.path.join('media', 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '{asctime} {levelname} {module} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'yta_log.log'),
            'formatter': 'detailed'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'yta_app': {  # Replace 'myapp' with the actual name of your application
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'ytauser': {  # Replace 'myapp' with the actual name of your application
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
