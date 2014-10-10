"""
Brings all of historian's modules together
- import all of historian's modules to apply any flask decorators
- run the flask instance
"""
from app import app
from models import *
from api import *
from views import *


#if __name__ == "__main__":
create_tables()
app.run(host='0.0.0.0', debug=True)