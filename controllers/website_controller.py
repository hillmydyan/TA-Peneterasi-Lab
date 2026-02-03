from flask import Blueprint, render_template, request, redirect, url_for, session, g, current_app
import sqlite3
import os
from datetime import datetime

website_bp = Blueprint('website', __name__, url_prefix='/lab/website')

# Configuration for the specific lab database
DB_PATH = "lab.db"

def get_db():
    if "db" not in g:
        # Ensure we look for lab.db in the application root or instance folder
        db_path = os.path.join(current_app.root_path, DB_PATH)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def seed_db():
    db = get_db()
    # wipe for predictable practice
    db.execute("DELETE FROM products;")
    db.execute("DELETE FROM guestbook;")

    products = [
        ("RouterLab-100", "Network"),
        ("WebApp Dummy", "Web"),
        ("Forensic Image", "Forensics"),
        ("Log Bundle", "Forensics"),
    ]
    db.executemany("INSERT INTO products (name, category) VALUES (?, ?);", products)

    db.execute(
        "INSERT INTO guestbook (name, message, created_at) VALUES (?, ?, ?);",
        ("Admin", "Welcome to the training guestbook!", datetime.utcnow().isoformat()),
    )
    db.commit()

# Register teardown function to close db connection
# Note: In a blueprint, we use record to register teardown on the app
@website_bp.record
def record_params(setup_state):
    app = setup_state.app
    app.teardown_appcontext(close_db)

@website_bp.before_request
def ensure_setup():
    # Simple check if table exists, if not seed? 
    # Or just rely on separate setup. For now, let's keep it simple.
    # We'll assume the DB file is copied and has structure, or we can init it.
    pass

@website_bp.route('/')
def index():
    return render_template('lab/website/main.html')

# -------------------------------------------------------------------------
# SQL INJECTION
# -------------------------------------------------------------------------
@website_bp.route("/sql-injection", methods=["GET", "POST"])
def sql_injection():
    # Difficulty handling - defaults to easy if not set
    difficulty = session.get("difficulty", "easy")
    
    # Allow changing difficulty via query param for easier testing/UI
    if request.args.get('difficulty'):
        difficulty = request.args.get('difficulty')
        session['difficulty'] = difficulty

    db = get_db()
    result = None
    shown_query = None
    error = None
    product_id = ""

    if request.method == "POST":
        product_id = (request.form.get("product_id") or "").strip()

        if difficulty == "easy":
            # VULNERABLE: No validation, direct injection possible
            # We strictly enforce digit check ONLY for the "error" message simulation 
            # OR we allow text.
            # Malik's logic: 
            # if not product_id.isdigit(): error
            # This actually PREVENTS injection if implemented strictly in Python.
            # WAIT, Malik's code:
            # if not product_id.isdigit(): error
            # else: show_query; execute( ? ) -> this is parameterized!
            
            # Let's re-read Malik's "Easy" logic carefully from exploration:
            # if not product_id.isdigit(): error ... 
            # else: execute("... WHERE id = ?", (pid,)) 
            # Malik's "Easy" code in the snippet provided IS ACTUALLY SECURE via parameter binding (?!).
            # "NOTE: edukasi aman (kita tetap pakai parameter binding)" -> comment in Malik's code.
            # The USER wants "SQL injection", so I should probably MAKE it vulnerable for "easy".
            
            # Let's implement actual VULNERABLE code for 'easy' so the lab works as expected.
            try:
                # VULNERABLE: Direct string concatenation
                shown_query = f"SELECT id, name, category FROM products WHERE id = {product_id}"
                result = db.execute(shown_query).fetchall()
            except Exception as e:
                error = f"SQL Error: {str(e)}"

        elif difficulty == "medium":
            # Medium: Check if digit, but maybe allow some bypass? 
            # Or just use parameterized to show the fix.
            # Usually "Medium" might have a weak filter.
            # For now, let's follow a standard pattern:
            # Easy: Vulnerable
            # Medium/Hard: Secure (or harder to exploit)
            
            # Let's stick closer to Malik's intent but fix the "Easy" mode to be actually vulnerable 
            # if the user wants to practice Injection.
            
            # Re-reading Malik's code:
            # It seems Malik's code might have been "safe by default" or I misread the snippet.
            # Line 159: shown_query = f"... {product_id}" (Shows vulnerable query)
            # Line 161: db.execute("... ?", (pid,)) (Executes SECURE query)
            # So Malik's code was a SIMULATION. It SHOWED a vulnerable query but EXECUTED a secure one?
            # That's confusing for a lab. I will make 'easy' ACTUALLY vulnerable.
            
            try:
                shown_query = f"SELECT id, name, category FROM products WHERE id = {product_id}"
                # ACTUALLY RUN THE INJECTION
                script = f"SELECT id, name, category FROM products WHERE id = {product_id}"
                result = db.execute(script).fetchall()
            except Exception as e:
                error = f"Database Error: {e}"

        else:  # hard (Secure)
            if not product_id.isdigit():
                error = "Input tidak valid (Validasi Server-Side Aktif)."
            else:
                pid = int(product_id)
                shown_query = "SELECT id, name, category FROM products WHERE id = ?"
                result = db.execute(
                    "SELECT id, name, category FROM products WHERE id = ?",
                    (pid,),
                ).fetchall()

    return render_template(
        "lab/website/sql_injection.html",
        difficulty=difficulty,
        result=result,
        shown_query=shown_query,
        error=error,
        product_id=product_id,
    )

# -------------------------------------------------------------------------
# XSS
# -------------------------------------------------------------------------
@website_bp.route("/xss", methods=["GET", "POST"])
def xss_simulation():
    difficulty = session.get("difficulty", "easy")
    
    if request.args.get('difficulty'):
        difficulty = request.args.get('difficulty')
        session['difficulty'] = difficulty

    db = get_db()
    error = None

    # Reflected XSS
    q = request.args.get("q", "")
    q_filtered = q

    if difficulty == "medium":
        # Simple filter (easily bypassed)
        q_filtered = q_filtered.replace("<", "").replace(">", "")
    
    # Hard would be handled by template autoescape=True (default in Flask)
    # But for Easy/Medium we pass it to template to be used with |safe

    reflected_output = q_filtered

    # Stored XSS (Guestbook)
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        message = (request.form.get("message") or "").strip()

        if not name or not message:
            error = "Name dan message wajib diisi."
        else:
            if difficulty == "hard":
                # Hard: server-side truncation/validation
                name = name[:40]
                message = message[:200]
                # Note: Real protection is escaping output, which we toggle in template

            db.execute(
                "INSERT INTO guestbook (name, message, created_at) VALUES (?, ?, ?);",
                (name, message, datetime.utcnow().isoformat()),
            )
            db.commit()
            return redirect(url_for("website.xss_simulation"))

    entries = db.execute(
        "SELECT id, name, message, created_at FROM guestbook ORDER BY id DESC;"
    ).fetchall()

    return render_template(
        "lab/website/xss_modul.html",
        difficulty=difficulty,
        q=q,
        reflected_output=reflected_output,
        entries=entries,
        error=error,
    )

@website_bp.post("/reset")
def reset_data():
    seed_db()
    return redirect(request.referrer or url_for('website.index'))
