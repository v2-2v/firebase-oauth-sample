from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth
from datetime import timedelta

app = Flask(__name__)
CORS(app, supports_credentials=True) # 開発用
app.secret_key = "www222www" # 開発用
app.permanent_session_lifetime = timedelta(days=7)
app.config.update({
    "SESSION_COOKIE_HTTPONLY": True,    # XSS対策
    "SESSION_COOKIE_SAMESITE": "Strict" # CSRF対策
})
app.config["SESSION_COOKIE_SECURE"] = not app.debug  # 本番だけTrue https only

cred = credentials.Certificate("adminsdk.json")
firebase_admin.initialize_app(cred)
ALLOWED_USERS={ #本番環境はdbを用いる
"xxx@gmail.com"
}
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/profile", methods=["POST"])
def get_profile():
    id_token = request.json.get("idToken")
    try:
        decoded = auth.verify_id_token(id_token)#正規ユーザーかを確認する
        user_email = decoded.get("email")
        if user_email not in ALLOWED_USERS:
            return jsonify({"success": False, "error": "Access denied"}), 403
        session.clear()
        session.permanent = True
        session["user"] = {
            "uid": decoded["uid"],
            "email": decoded.get("email"),
            "name": decoded.get("name"),
            "picture": decoded.get("picture")
        }
        return jsonify({"success": True, **session["user"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401

@app.route("/api/me")
def me():
    if "user" in session:
        return jsonify({"logged_in": True, **session["user"]})
    else:
        return jsonify({"logged_in": False}), 401

if __name__ == "__main__":
    app.run(debug=True, port=5151)