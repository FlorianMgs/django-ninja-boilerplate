from .base import *

# Development-specific settings
DEBUG = True

# Additional development settings
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]

# Development logging overrides (more verbose)
LOGGING["loggers"]["django"]["level"] = "DEBUG"
LOGGING["loggers"]["db"]["level"] = "DEBUG"

# Disable secure settings for development
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
