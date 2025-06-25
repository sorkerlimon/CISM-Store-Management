from django.apps import AppConfig


class CismAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cism_app'
    
    def ready(self):
        # Import and register template tags
        import cism_app.templatetags.custom_filters
