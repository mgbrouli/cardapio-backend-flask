from app import create_app
app = create_app()
print('ASGI application ->', app.title)
print('OpenAPI routes ->', ', '.join(app.openapi()['paths']))
