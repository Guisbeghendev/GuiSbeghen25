# autenticad/apps.py

from django.apps import AppConfig

class AutenticadConfig(AppConfig):
    name = 'autenticad'

    def ready(self):
        # Certifique-se de que o signal é importado quando a app é inicializada
        import autenticad.signals
