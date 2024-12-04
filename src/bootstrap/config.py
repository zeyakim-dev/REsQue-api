config = {
    'db': {
        'url': 'postgresql://user:pass@localhost/dbname',
    },
    'security': {
        'password_work_factor': 12,
        'jwt_secret': 'your-secret-key',
        'jwt_expiry_minutes': 60,
    },
    'rabbitmq': {
        'host': 'localhost',
        'port': 5672,
        'username': 'guest',
        'password': 'guest',
        'exchange_name': 'domain_events',
        'queue_name': 'my_app_queue'
    }
}