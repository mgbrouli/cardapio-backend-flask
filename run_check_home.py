from app import create_app
from flask import url_for
app = create_app()
with app.test_request_context():
    print('empresa.subscribe ->', url_for('empresa.subscribe', empresa_id=1))
    print('config (legacy) ->', url_for('empresa.config', empresa_id=1))
    print('empresa.home ->', url_for('empresa.home'))
