import os, uuid
from datetime import datetime
from functools import wraps
from sqlalchemy import text
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, send_from_directory)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tgm-finance-dev-key-change-in-prod")

db_url = os.environ.get("DATABASE_URL", "sqlite:///tgm_finance.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "jpg", "jpeg", "png"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

db = SQLAlchemy(app)

# ── MODELS ────────────────────────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(40), default="Staff")
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw):    self.password_hash = generate_password_hash(pw)
    def check_password(self, pw):  return check_password_hash(self.password_hash, pw)


class University(db.Model):
    __tablename__ = "universities"
    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(200), nullable=False)
    country          = db.Column(db.String(100))
    city             = db.Column(db.String(100))
    commission_rate  = db.Column(db.Float, default=0.0)   # % of tuition
    contact_name     = db.Column(db.String(120))
    contact_email    = db.Column(db.String(120))
    contact_phone    = db.Column(db.String(60))
    website          = db.Column(db.String(200))
    agreement_signed = db.Column(db.Boolean, default=False)
    notes            = db.Column(db.Text)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    commission_notes    = db.Column(db.Text)
    incentives          = db.Column(db.Text)
    contract_start      = db.Column(db.String(40))
    contract_end        = db.Column(db.String(80))
    review_date         = db.Column(db.String(40))
    target_students     = db.Column(db.String(80))
    territory           = db.Column(db.Text)
    expansion_requested = db.Column(db.Boolean, default=False)
    contract_status     = db.Column(db.String(40), default="Active")
    renewal_options     = db.Column(db.String(200))
    duration            = db.Column(db.String(60))
    region              = db.Column(db.String(60))

    students  = db.relationship("Student",           backref="university", lazy=True, cascade="all, delete-orphan")
    documents = db.relationship("CommissionDocument", backref="university", lazy=True, cascade="all, delete-orphan")

    @property
    def active_students(self):
        return [s for s in self.students if s.status != "Cancelled"]

    @property
    def total_expected(self):
        return sum(s.commission_amount for s in self.active_students)

    @property
    def total_collected(self):
        return sum(s.amount_collected for s in self.active_students)

    @property
    def total_outstanding(self):
        return self.total_expected - self.total_collected


class Student(db.Model):
    __tablename__ = "students"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(160), nullable=False)
    email           = db.Column(db.String(120))
    phone           = db.Column(db.String(60))
    nationality     = db.Column(db.String(100))
    university_id   = db.Column(db.Integer, db.ForeignKey("universities.id"), nullable=False)
    program         = db.Column(db.String(200))
    intake          = db.Column(db.String(80))
    tuition_amount  = db.Column(db.Float, default=0.0)
    commission_rate = db.Column(db.Float, nullable=True)   # None → use university rate
    amount_collected= db.Column(db.Float, default=0.0)
    currency        = db.Column(db.String(10), default="USD")
    status          = db.Column(db.String(40), default="Prospect")
    notes           = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def effective_rate(self):
        if self.commission_rate is not None:
            return self.commission_rate
        return self.university.commission_rate if self.university else 0.0

    @property
    def commission_amount(self):
        return self.tuition_amount * self.effective_rate / 100

    @property
    def outstanding(self):
        return self.commission_amount - self.amount_collected

    @property
    def collection_pct(self):
        if self.commission_amount == 0:
            return 0
        return min(100, self.amount_collected / self.commission_amount * 100)


class CommissionDocument(db.Model):
    __tablename__ = "commission_documents"
    id                = db.Column(db.Integer, primary_key=True)
    university_id     = db.Column(db.Integer, db.ForeignKey("universities.id"), nullable=False)
    filename          = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    description       = db.Column(db.String(255))
    file_size         = db.Column(db.Integer)
    uploaded_at       = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by       = db.Column(db.String(120))

    @property
    def file_ext(self):
        return self.original_filename.rsplit(".", 1)[-1].lower() if "." in self.original_filename else "file"

    @property
    def size_display(self):
        if not self.file_size:
            return "—"
        kb = self.file_size / 1024
        if kb < 1024:
            return f"{kb:.1f} KB"
        return f"{kb / 1024:.1f} MB"


class ActivityLog(db.Model):
    __tablename__ = "activity_log"
    id         = db.Column(db.Integer, primary_key=True)
    user_name  = db.Column(db.String(120))
    action     = db.Column(db.String(30))
    entity     = db.Column(db.String(40))
    summary    = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def log_activity(action, entity, summary):
    db.session.add(ActivityLog(
        user_name=session.get("user_name", "System"),
        action=action, entity=entity, summary=summary,
    ))


def parse_float(s, default=0.0):
    if not s:
        return default
    try:
        return float(str(s).replace(",", "").strip())
    except ValueError:
        return default


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None


# ── DECORATORS ────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        u = current_user()
        if not u or u.role not in ("Admin", "MD/CEO"):
            flash("Admin access required.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# ── TEMPLATE FILTERS ──────────────────────────────────────────────────────────

@app.template_filter("money")
def money_filter(v, currency="USD"):
    if v is None:
        return "—"
    symbols = {"USD": "$", "GBP": "£", "EUR": "€", "NGN": "₦", "CAD": "CA$", "AUD": "A$"}
    sym = symbols.get(currency, currency + " ")
    return f"{sym}{v:,.2f}"


@app.template_filter("pct")
def pct_filter(v):
    return f"{v:.2f}%" if v is not None else "—"


@app.template_filter("fmtdate")
def fmtdate_filter(v):
    return v.strftime("%-d %b %Y") if v else "—"


# ── DB INIT ───────────────────────────────────────────────────────────────────

def ensure_columns():
    dialect = db.engine.dialect.name
    with db.engine.connect() as conn:
        if dialect == "sqlite":
            result = conn.execute(text("PRAGMA table_info(universities)"))
            existing = {row[1] for row in result}
        else:
            result = conn.execute(text(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'universities'"
            ))
            existing = {row[0] for row in result}
        new_cols = {
            "commission_notes":    "TEXT",
            "incentives":          "TEXT",
            "contract_start":      "VARCHAR(40)",
            "contract_end":        "VARCHAR(80)",
            "review_date":         "VARCHAR(40)",
            "target_students":     "VARCHAR(80)",
            "territory":           "TEXT",
            "expansion_requested": "BOOLEAN DEFAULT 0",
            "contract_status":     "VARCHAR(40) DEFAULT 'Active'",
            "renewal_options":     "VARCHAR(200)",
            "duration":            "VARCHAR(60)",
            "region":              "VARCHAR(60)",
        }
        for col, dtype in new_cols.items():
            if col not in existing:
                conn.execute(text(f"ALTER TABLE universities ADD COLUMN {col} {dtype}"))
        conn.commit()


def init_db():
    db.create_all()
    ensure_columns()
    if not User.query.first():
        u = User(
            name=os.environ.get("ADMIN_NAME", "TGM Admin"),
            email=os.environ.get("ADMIN_EMAIL", "admin@tgmfinance.com"),
            role="MD/CEO",
        )
        u.set_password(os.environ.get("ADMIN_PASSWORD", "tgm123"))
        db.session.add(u)
        db.session.commit()


with app.app_context():
    init_db()


# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        u = User.query.filter(db.func.lower(User.email) == email).first()
        if u and u.check_password(pw):
            session["user_id"]   = u.id
            session["user_name"] = u.name
            session["user_role"] = u.role
            return redirect(request.args.get("next") or url_for("dashboard"))
        error = "Invalid email or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def dashboard():
    all_students  = Student.query.filter(Student.status != "Cancelled").all()
    universities  = University.query.order_by(University.name).all()

    total_expected   = sum(s.commission_amount for s in all_students)
    total_collected  = sum(s.amount_collected  for s in all_students)
    total_outstanding= total_expected - total_collected
    total_students   = len(all_students)

    status_counts = {}
    for s in Student.query.all():
        status_counts[s.status] = status_counts.get(s.status, 0) + 1

    uni_rows = []
    for u in universities:
        active = u.active_students
        if active or u.documents:
            uni_rows.append({
                "university":  u,
                "students":    len(active),
                "expected":    u.total_expected,
                "collected":   u.total_collected,
                "outstanding": u.total_outstanding,
            })
    uni_rows.sort(key=lambda x: x["expected"], reverse=True)

    recent = Student.query.order_by(Student.created_at.desc()).limit(8).all()

    return render_template("dashboard.html",
        total_expected=total_expected,
        total_collected=total_collected,
        total_outstanding=total_outstanding,
        total_students=total_students,
        total_universities=len(universities),
        status_counts=status_counts,
        uni_rows=uni_rows,
        recent=recent,
    )


# ── UNIVERSITIES ──────────────────────────────────────────────────────────────

@app.route("/universities")
@login_required
def universities():
    q             = request.args.get("q", "").strip()
    region_filter = request.args.get("region", "").strip()
    status_filter = request.args.get("status", "").strip()
    query = University.query
    if q:
        query = query.filter(
            University.name.ilike(f"%{q}%") | University.country.ilike(f"%{q}%") |
            University.territory.ilike(f"%{q}%")
        )
    if region_filter:
        query = query.filter(University.region == region_filter)
    if status_filter:
        query = query.filter(University.contract_status == status_filter)
    return render_template("universities.html",
        universities=query.order_by(University.name).all(),
        q=q, region_filter=region_filter, status_filter=status_filter,
    )


@app.route("/universities/add", methods=["POST"])
@login_required
def university_add():
    name = request.form.get("name", "").strip()
    if not name:
        flash("University name is required.", "error")
        return redirect(url_for("universities"))
    u = University(
        name=name,
        country=request.form.get("country", "").strip(),
        city=request.form.get("city", "").strip(),
        region=request.form.get("region", "").strip(),
        commission_rate=parse_float(request.form.get("commission_rate")),
        commission_notes=request.form.get("commission_notes", "").strip(),
        incentives=request.form.get("incentives", "").strip(),
        contract_start=request.form.get("contract_start", "").strip(),
        contract_end=request.form.get("contract_end", "").strip(),
        review_date=request.form.get("review_date", "").strip(),
        target_students=request.form.get("target_students", "").strip(),
        territory=request.form.get("territory", "").strip(),
        duration=request.form.get("duration", "").strip(),
        renewal_options=request.form.get("renewal_options", "").strip(),
        contract_status=request.form.get("contract_status", "Active"),
        expansion_requested=bool(request.form.get("expansion_requested")),
        contact_name=request.form.get("contact_name", "").strip(),
        contact_email=request.form.get("contact_email", "").strip(),
        contact_phone=request.form.get("contact_phone", "").strip(),
        website=request.form.get("website", "").strip(),
        agreement_signed=bool(request.form.get("agreement_signed")),
        notes=request.form.get("notes", "").strip(),
    )
    db.session.add(u)
    log_activity("Created", "University", f"Added university: {name}")
    db.session.commit()
    flash(f"University '{name}' added.", "success")
    return redirect(url_for("university_detail", uid=u.id))


@app.route("/universities/<int:uid>")
@login_required
def university_detail(uid):
    u     = db.get_or_404(University, uid)
    docs  = CommissionDocument.query.filter_by(university_id=uid).order_by(CommissionDocument.uploaded_at.desc()).all()
    return render_template("university_detail.html", university=u, documents=docs)


@app.route("/universities/<int:uid>/edit", methods=["POST"])
@login_required
def university_edit(uid):
    u = db.get_or_404(University, uid)
    u.name               = request.form.get("name", u.name).strip()
    u.country            = request.form.get("country", "").strip()
    u.city               = request.form.get("city", "").strip()
    u.region             = request.form.get("region", "").strip()
    u.commission_rate    = parse_float(request.form.get("commission_rate"), u.commission_rate)
    u.commission_notes   = request.form.get("commission_notes", "").strip()
    u.incentives         = request.form.get("incentives", "").strip()
    u.contract_start     = request.form.get("contract_start", "").strip()
    u.contract_end       = request.form.get("contract_end", "").strip()
    u.review_date        = request.form.get("review_date", "").strip()
    u.target_students    = request.form.get("target_students", "").strip()
    u.territory          = request.form.get("territory", "").strip()
    u.duration           = request.form.get("duration", "").strip()
    u.renewal_options    = request.form.get("renewal_options", "").strip()
    u.contract_status    = request.form.get("contract_status", u.contract_status or "Active")
    u.expansion_requested= bool(request.form.get("expansion_requested"))
    u.contact_name       = request.form.get("contact_name", "").strip()
    u.contact_email      = request.form.get("contact_email", "").strip()
    u.contact_phone      = request.form.get("contact_phone", "").strip()
    u.website            = request.form.get("website", "").strip()
    u.agreement_signed   = bool(request.form.get("agreement_signed"))
    u.notes              = request.form.get("notes", "").strip()
    log_activity("Updated", "University", f"Edited: {u.name}")
    db.session.commit()
    flash("University updated.", "success")
    return redirect(url_for("university_detail", uid=uid))


@app.route("/universities/<int:uid>/delete", methods=["POST"])
@admin_required
def university_delete(uid):
    u = db.get_or_404(University, uid)
    for doc in u.documents:
        fp = os.path.join(app.config["UPLOAD_FOLDER"], doc.filename)
        if os.path.exists(fp):
            os.remove(fp)
    name = u.name
    log_activity("Deleted", "University", f"Deleted: {name}")
    db.session.delete(u)
    db.session.commit()
    flash(f"University '{name}' deleted.", "success")
    return redirect(url_for("universities"))


# ── STUDENTS ──────────────────────────────────────────────────────────────────

@app.route("/students")
@login_required
def students():
    q          = request.args.get("q", "").strip()
    sf         = request.args.get("status", "")
    uf         = request.args.get("university", "")
    query      = Student.query
    if q:
        query = query.filter(
            Student.name.ilike(f"%{q}%") | Student.email.ilike(f"%{q}%") | Student.program.ilike(f"%{q}%")
        )
    if sf:
        query = query.filter(Student.status == sf)
    if uf:
        query = query.filter(Student.university_id == int(uf))
    return render_template("students.html",
        students=query.order_by(Student.created_at.desc()).all(),
        universities=University.query.order_by(University.name).all(),
        q=q, status_filter=sf, uni_filter=uf,
    )


@app.route("/students/add", methods=["POST"])
@login_required
def student_add():
    name   = request.form.get("name", "").strip()
    uni_id = request.form.get("university_id", "").strip()
    if not name or not uni_id:
        flash("Name and university are required.", "error")
        return redirect(url_for("students"))
    uni = db.session.get(University, int(uni_id))
    if not uni:
        flash("University not found.", "error")
        return redirect(url_for("students"))
    rate_str = request.form.get("commission_rate", "").strip()
    s = Student(
        name=name,
        email=request.form.get("email", "").strip(),
        phone=request.form.get("phone", "").strip(),
        nationality=request.form.get("nationality", "").strip(),
        university_id=int(uni_id),
        program=request.form.get("program", "").strip(),
        intake=request.form.get("intake", "").strip(),
        tuition_amount=parse_float(request.form.get("tuition_amount")),
        commission_rate=parse_float(rate_str) if rate_str else None,
        currency=request.form.get("currency", "USD"),
        status=request.form.get("status", "Prospect"),
        notes=request.form.get("notes", "").strip(),
    )
    db.session.add(s)
    log_activity("Created", "Student", f"Added: {name} → {uni.name}")
    db.session.commit()
    flash(f"Student '{name}' added.", "success")
    return redirect(url_for("student_detail", sid=s.id))


@app.route("/students/<int:sid>")
@login_required
def student_detail(sid):
    s = db.get_or_404(Student, sid)
    return render_template("student_detail.html",
        student=s,
        universities=University.query.order_by(University.name).all(),
    )


@app.route("/students/<int:sid>/edit", methods=["POST"])
@login_required
def student_edit(sid):
    s = db.get_or_404(Student, sid)
    s.name          = request.form.get("name", s.name).strip()
    s.email         = request.form.get("email", "").strip()
    s.phone         = request.form.get("phone", "").strip()
    s.nationality   = request.form.get("nationality", "").strip()
    uni_id = request.form.get("university_id")
    if uni_id:
        s.university_id = int(uni_id)
    s.program         = request.form.get("program", "").strip()
    s.intake          = request.form.get("intake", "").strip()
    s.tuition_amount  = parse_float(request.form.get("tuition_amount"), s.tuition_amount)
    rate_str = request.form.get("commission_rate", "").strip()
    s.commission_rate = parse_float(rate_str) if rate_str else None
    s.currency        = request.form.get("currency", s.currency)
    s.status          = request.form.get("status", s.status)
    s.notes           = request.form.get("notes", "").strip()
    log_activity("Updated", "Student", f"Edited: {s.name}")
    db.session.commit()
    flash("Student updated.", "success")
    return redirect(url_for("student_detail", sid=sid))


@app.route("/students/<int:sid>/collect", methods=["POST"])
@login_required
def student_collect(sid):
    s = db.get_or_404(Student, sid)
    amount = parse_float(request.form.get("amount"))
    if amount <= 0:
        flash("Enter a valid amount.", "error")
        return redirect(url_for("student_detail", sid=sid))
    s.amount_collected += amount
    log_activity("Collected", "Commission", f"${amount:,.2f} from {s.university.name} for {s.name}")
    db.session.commit()
    sym = {"USD": "$", "GBP": "£", "EUR": "€", "NGN": "₦", "CAD": "CA$", "AUD": "A$"}.get(s.currency, s.currency + " ")
    flash(f"Commission of {sym}{amount:,.2f} recorded.", "success")
    return redirect(url_for("student_detail", sid=sid))


@app.route("/students/<int:sid>/delete", methods=["POST"])
@admin_required
def student_delete(sid):
    s = db.get_or_404(Student, sid)
    name = s.name
    log_activity("Deleted", "Student", f"Deleted: {name}")
    db.session.delete(s)
    db.session.commit()
    flash(f"Student '{name}' deleted.", "success")
    return redirect(url_for("students"))


# ── LEGAL DOCUMENTS ───────────────────────────────────────────────────────────

@app.route("/legal")
@login_required
def legal():
    uni_filter = request.args.get("university", "")
    query = CommissionDocument.query
    if uni_filter:
        query = query.filter_by(university_id=int(uni_filter))
    docs = query.order_by(CommissionDocument.uploaded_at.desc()).all()
    return render_template("legal.html",
        documents=docs,
        universities=University.query.order_by(University.name).all(),
        uni_filter=uni_filter,
    )


@app.route("/legal/upload", methods=["POST"])
@login_required
def legal_upload():
    uni_id = request.form.get("university_id", "").strip()
    if not uni_id:
        flash("Select a university.", "error")
        return redirect(url_for("legal"))
    uni = db.session.get(University, int(uni_id))
    if not uni:
        flash("University not found.", "error")
        return redirect(url_for("legal"))
    file = request.files.get("document")
    if not file or file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("legal"))
    if not allowed_file(file.filename):
        flash("Allowed types: PDF, DOC, DOCX, JPG, PNG.", "error")
        return redirect(url_for("legal"))
    orig = secure_filename(file.filename)
    ext  = orig.rsplit(".", 1)[-1].lower()
    stored = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], stored)
    file.save(save_path)
    doc = CommissionDocument(
        university_id=int(uni_id),
        filename=stored,
        original_filename=orig,
        description=request.form.get("description", "").strip(),
        file_size=os.path.getsize(save_path),
        uploaded_by=session.get("user_name"),
    )
    db.session.add(doc)
    log_activity("Uploaded", "Document", f"'{orig}' for {uni.name}")
    db.session.commit()
    flash(f"Document '{orig}' uploaded.", "success")
    return redirect(url_for("legal"))


@app.route("/legal/download/<int:doc_id>")
@login_required
def legal_download(doc_id):
    doc = db.get_or_404(CommissionDocument, doc_id)
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], doc.filename,
        as_attachment=True, download_name=doc.original_filename,
    )


@app.route("/legal/delete/<int:doc_id>", methods=["POST"])
@login_required
def legal_delete(doc_id):
    doc = db.get_or_404(CommissionDocument, doc_id)
    fp = os.path.join(app.config["UPLOAD_FOLDER"], doc.filename)
    if os.path.exists(fp):
        os.remove(fp)
    name = doc.original_filename
    log_activity("Deleted", "Document", f"Deleted '{name}' from {doc.university.name}")
    db.session.delete(doc)
    db.session.commit()
    flash(f"Document '{name}' deleted.", "success")
    return redirect(url_for("legal"))


# ── TEAM ──────────────────────────────────────────────────────────────────────

@app.route("/team")
@admin_required
def team():
    return render_template("team.html", users=User.query.order_by(User.created_at).all())


@app.route("/team/add", methods=["POST"])
@admin_required
def team_add():
    name  = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    pw    = request.form.get("password", "")
    role  = request.form.get("role", "Staff")
    if not name or not email or not pw:
        flash("Name, email and password are required.", "error")
        return redirect(url_for("team"))
    if User.query.filter(db.func.lower(User.email) == email).first():
        flash("Email already in use.", "error")
        return redirect(url_for("team"))
    u = User(name=name, email=email, role=role)
    u.set_password(pw)
    db.session.add(u)
    log_activity("Created", "User", f"Added {name} ({role})")
    db.session.commit()
    flash(f"User '{name}' added.", "success")
    return redirect(url_for("team"))


@app.route("/team/<int:uid>/reset", methods=["POST"])
@admin_required
def team_reset(uid):
    u  = db.get_or_404(User, uid)
    pw = request.form.get("password", "")
    if not pw:
        flash("New password required.", "error")
        return redirect(url_for("team"))
    u.set_password(pw)
    log_activity("Updated", "User", f"Reset password for {u.name}")
    db.session.commit()
    flash(f"Password reset for {u.name}.", "success")
    return redirect(url_for("team"))


@app.route("/team/<int:uid>/role", methods=["POST"])
@admin_required
def team_role(uid):
    u       = db.get_or_404(User, uid)
    new_role = request.form.get("role", "Staff")
    u.role  = new_role
    log_activity("Updated", "User", f"Changed role of {u.name} to {new_role}")
    db.session.commit()
    flash(f"Role updated for {u.name}.", "success")
    return redirect(url_for("team"))


@app.route("/team/<int:uid>/delete", methods=["POST"])
@admin_required
def team_delete(uid):
    u = db.get_or_404(User, uid)
    if u.id == session.get("user_id"):
        flash("Cannot delete your own account.", "error")
        return redirect(url_for("team"))
    name = u.name
    log_activity("Deleted", "User", f"Removed {name}")
    db.session.delete(u)
    db.session.commit()
    flash(f"User '{name}' removed.", "success")
    return redirect(url_for("team"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
