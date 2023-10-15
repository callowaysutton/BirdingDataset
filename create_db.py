from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.reflect()
        db.create_all()