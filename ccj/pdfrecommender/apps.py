from django.apps import AppConfig
from . import pdflist

class PdfrecommenderConfig(AppConfig):
    name = 'pdfrecommender'

    def ready(self):
        pdflist.preq()
