"""
Some configuration variables, is not included in
git because contains sensitive data
"""


LOGGING = {
    'version': 1,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-30s:%(lineno)d %(levelname)-8s %(processName)-15s %(message)s'
            }
        },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'level': 'DEBUG'
            },
        },
    'loggers': {
        '__main__': {
            'level': 'DEBUG',
            'handlers': ['console']
            },
        },
    }
