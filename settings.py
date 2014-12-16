from kombu import Exchange, Queue

RELENGAPI_PERMISSIONS = {
    'type': 'static',
    'permissions': {
        'gmiroshnykov@mozilla.com': [
            'transplant.transplant',
            'base.tokens.view',
            'base.tokens.issue',
            'base.tokens.revoke',
        ],
    },
}

CELERY_ACCEPT_CONTENT=['json']
CELERY_TASK_SERIALIZER='json'
CELERY_RESULT_SERIALIZER='json'
CELERY_BROKER_URL='redis://localhost:6379/0'
CELERY_BACKEND='redis://localhost:6379/1'
CELERY_QUEUES = (
    Queue('transplant', Exchange('transplant'), routing_key='transplant'),
)

TRANSPLANT_REPOSITORIES = [
    {
        "name": "transplant-src",
        "path": "ssh://hg@bitbucket.org/laggyluke/transplant-src"
    },
    {
        "name": "transplant-dst",
        "path": "ssh://hg@bitbucket.org/laggyluke/transplant-dst"
    }
]
