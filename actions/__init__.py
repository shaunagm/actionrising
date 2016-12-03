# -*- coding: utf-8 -*-
from django.apps import AppConfig

class ActionsConfig(AppConfig):
    """Setup our app."""
    name = 'actions'
    
    def ready(self):
        import actions.signals 
        
default_app_config = 'actions.ActionsConfig'  
