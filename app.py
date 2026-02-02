from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, bcrypt

# Import semua controller (blueprint)
from controllers.dashboard_controller import dashboard
from controllers.lab_controller import lab
from controllers.report_controller import report
from controllers.auth_controller import auth

# Inisialisasi Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi Extensions
db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)

# Registrasi semua route
app.register_blueprint(dashboard)
app.register_blueprint(lab)
app.register_blueprint(report)
app.register_blueprint(auth)

# Buat Database jika belum ada
with app.app_context():
    db.create_all()

# Jalankan server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
