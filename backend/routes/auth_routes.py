from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from models import db, User

bp = Blueprint("auth", __name__, url_prefix="/auth")
bcrypt = Bcrypt()


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(username=data["username"], email=data["email"], password_hash=hashed)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful", "user_id": user.id}), 200
