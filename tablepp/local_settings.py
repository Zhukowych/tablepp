"""
Local settings
"""

from tablepp.settings import *

DATABASES["default"]["OPTIONS"]["charset"] = "utf8mb4"
DATABASES["default"]["USER"] = "admin"
DATABASES["default"]["PASSWORD"] = "admin"
DATABASES["default"]["NAME"] = "tablepp"
