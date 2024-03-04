"""
Local settings
"""
from tablepp.settings import *

DATABASES['default']['OPTIONS']['charset'] = 'utf8mb4'
DATABASES['default']['USER'] = 'max'
DATABASES['default']['PASSWORD'] = 'password'
DATABASES['default']['NAME'] = 'tablepp'

