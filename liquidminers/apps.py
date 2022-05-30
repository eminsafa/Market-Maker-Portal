from django.apps import AppConfig
import os

class MyAppConfig(AppConfig):
    name = 'liquidminers'

    def ready(self):

        stage = os.getenv('ENV_STAGE', 'DEV')
        print(f"STAGE: {stage}")
        if stage != 'TEST':
            from liquidminers.integrations.thread_factory import ThreadFactory
            ThreadFactory.run()
            #pass
