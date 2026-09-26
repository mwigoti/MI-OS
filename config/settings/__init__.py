"""
MwohaOS Settings Package
Default environment settings selector.
"""
import os

env_mode = os.environ.get("MWOHAOS_ENVIRONMENT", "development").lower()

if env_mode == "production":
    from .production import *
else:
    from .development import *
