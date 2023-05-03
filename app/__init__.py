from flask import Flask
from .static.py.db_handler import DbHandler

db = DbHandler('app\\db.sqlite',
               'app\\static\\data\\users\\admins.json')

articles_on_page = 3

app = Flask(__name__)

app.config.from_object('config.Config')
# blueprint for auth routes
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for main routes
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)


if __name__ == "__main__":
    app.run(debug=True)