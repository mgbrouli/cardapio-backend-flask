from app import create_app
app = create_app()
print('TEMPLATES_FOLDER ->', app.template_folder)
print('STATIC_FOLDER ->', app.static_folder)
