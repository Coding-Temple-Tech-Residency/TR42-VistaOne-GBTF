from app import create_app
from models import db, User
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)


def seed():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email="admin@example.com").first():
            hashed = bcrypt.generate_password_hash("password").decode("utf-8")
            user = User(username="admin", email="admin@example.com", password_hash=hashed)
            db.session.add(user)
            db.session.commit()
            print("Seeded admin user.")
        else:
            print("Admin user already exists.")


if __name__ == "__main__":
    seed()
