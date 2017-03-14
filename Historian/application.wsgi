import os, sys

PROJECT_DIR = '/var/www/historian/'

activate_this = os.path.join(PROJECT_DIR, 'venv/bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
sys.path.append(PROJECT_DIR)

from historian import app as application
