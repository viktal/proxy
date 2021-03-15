import os
SERVER_ADDRESS = ('0.0.0.0', 8081)
WEB_PORT = 8000
CONTENT_TYPES = ('application', 'text')
COUNT_REQUESTS = 100
COUNT_CPU = os.cpu_count()
DATABASE_NAME = 'sqlite:///proxy.db'
