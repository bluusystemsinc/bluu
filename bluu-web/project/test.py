from project.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

MANAGERS = (
    ('Jakub Wisniowski', 'jwisniowski@milosolutions.com'),
)

try:
    from local_settings import *
except ImportError:
    pass
