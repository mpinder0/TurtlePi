"""
Brings all of historian's modules together
- import all of historian's modules to apply any flask decorators
- run the flask instance
"""
from app import app
from models import *
from api import *
from views import *

# call config and setup methods for api etc

if __name__ == "__main__":
    app.run()