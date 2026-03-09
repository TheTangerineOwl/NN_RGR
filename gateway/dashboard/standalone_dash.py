import sys
from pathlib import Path
from dash import Dash
from django import setup as dj_setup
from os import environ
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv()
environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings')
dj_setup()

from dashboard.callbacks import init_callbacks
from dashboard.layouts.main import create_layout
from django.conf import settings

DEBUG = settings.DEBUG

app = Dash(__name__, suppress_callback_exceptions=True)
app.layout = create_layout()
init_callbacks(app)


if __name__ == '__main__':
    app.run(debug=DEBUG, port=8050, dev_tools_ui=DEBUG)
