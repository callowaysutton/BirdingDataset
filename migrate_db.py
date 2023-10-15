from flask_migrate import Migrate
from app import app, db

if __name__ == '__main__':
    with app.app_context():
        migrate = Migrate(app, db)