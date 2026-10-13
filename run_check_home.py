from app import create_app
app = create_app()
for route_name, values in (
    ('empresa.subscribe', {'empresa_id': 1}),
    ('empresa.config', {'empresa_id': 1}),
    ('empresa.home', {}),
):
    print(f'{route_name} -> {app.url_path_for(route_name, **values)}')
