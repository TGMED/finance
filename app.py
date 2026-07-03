import os, uuid, csv, io, json
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import text
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, send_from_directory, Response, jsonify)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tgm-finance-dev-key-change-in-prod")

SESSION_TIMEOUT_MINUTES = int(os.environ.get("SESSION_TIMEOUT_MINUTES", 30))
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=SESSION_TIMEOUT_MINUTES)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL environment variable is not set. Please configure your MySQL connection.")
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
    expansion_requested  = db.Column(db.Boolean, default=False)
    contract_status      = db.Column(db.String(40), default="Active")
    renewal_options      = db.Column(db.String(200))
    duration             = db.Column(db.String(60))
    region               = db.Column(db.String(60))
    additional_comments  = db.Column(db.Text)
    commission_type      = db.Column(db.String(30))
    commission_rules     = db.Column(db.Text)       # JSON rule engine

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
    notes                      = db.Column(db.Text)
    programme_category         = db.Column(db.String(60))
    year_of_study              = db.Column(db.Integer, default=1)
    commission_amount_override = db.Column(db.Float)
    created_at                 = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def effective_rate(self):
        if self.commission_rate is not None:
            return self.commission_rate
        return self.university.commission_rate if self.university else 0.0

    @property
    def commission_amount(self):
        if self.commission_amount_override is not None:
            return self.commission_amount_override
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
    with db.engine.connect() as conn:
        dialect = db.engine.dialect.name

        def get_existing(table):
            if dialect == "sqlite":
                r = conn.execute(text(f"PRAGMA table_info({table})"))
                return {row[1] for row in r}
            else:
                r = conn.execute(text(
                    "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t"
                ), {"t": table})
                return {row[0] for row in r}

        existing_uni = get_existing("universities")
        for col, dtype in {
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
            "additional_comments": "TEXT",
            "commission_type":     "VARCHAR(30)",
            "commission_rules":    "TEXT",
        }.items():
            if col not in existing_uni:
                conn.execute(text(f"ALTER TABLE universities ADD COLUMN {col} {dtype}"))

        existing_stu = get_existing("students")
        for col, dtype in {
            "programme_category":         "VARCHAR(60)",
            "year_of_study":              "INTEGER DEFAULT 1",
            "commission_amount_override": "FLOAT",
        }.items():
            if col not in existing_stu:
                conn.execute(text(f"ALTER TABLE students ADD COLUMN {col} {dtype}"))

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


# ── COMMISSION CALCULATOR ─────────────────────────────────────────────────────

PROGRAMME_CATEGORIES = [
    "Undergraduate", "Postgraduate / Masters", "PhD / Doctoral",
    "Diploma", "Advanced Diploma", "EAP / ESL / English",
    "Engineering", "Post-Graduate Certificate", "Certificate",
    "Foundation", "MBA", "Other",
]

def _eval_rule(rules, programme, year, tuition, student_count):
    t = rules.get("type", "")
    prog_lower = (programme or "").lower()

    if t == "flat_pct":
        rate = rules.get("rate", 0)
        return round(tuition * rate / 100, 2), f"{rate}% of tuition", False, []

    if t == "tiered_by_year":
        tiers = rules.get("tiers", [])
        rate = rules.get("default_rate", 0)
        for tier in tiers:
            if tier.get("year") == year:
                rate = tier.get("rate", rate)
                break
        return round(tuition * rate / 100, 2), f"{rate}% of tuition (Year {year})", False, []

    if t == "tiered_by_volume":
        tiers = sorted(rules.get("tiers", []), key=lambda x: x.get("min", 0), reverse=True)
        rate, bonus = 0, 0
        for tier in tiers:
            min_s = tier.get("min", 0)
            max_s = tier.get("max")
            if student_count >= min_s and (max_s is None or student_count <= max_s):
                rate = tier.get("rate", 0)
                bonus = tier.get("bonus_per_student", 0)
                break
        amount = round(tuition * rate / 100 + bonus, 2)
        desc = f"{rate}% of tuition"
        if bonus:
            desc += f" + {bonus:,.0f} bonus ({student_count} students at this uni)"
        return amount, desc, False, []

    if t == "by_programme":
        prog_rules = rules.get("rules", [])
        default_rate = rules.get("default_rate", 0)
        rate, fixed = default_rate, None
        for r in prog_rules:
            if r.get("programme", "").lower() in prog_lower or prog_lower in r.get("programme", "").lower():
                fixed = r.get("amount")
                if fixed is None:
                    rate = r.get("rate", default_rate)
                break
        if fixed is not None:
            return float(fixed), f"Fixed fee for {programme or 'this programme'}", False, []
        return round(tuition * rate / 100, 2), f"{rate}% for {programme or 'programme'}", False, []

    if t == "fixed_by_programme":
        prog_rules = rules.get("rules", [])
        default_amount = rules.get("default_amount", 0)
        amount = float(default_amount)
        for r in prog_rules:
            if r.get("programme", "").lower() in prog_lower or prog_lower in r.get("programme", "").lower():
                amount = float(r.get("amount", default_amount))
                break
        return amount, f"Fixed fee for {programme or 'programme'}", False, []

    if t == "fixed_amount":
        return float(rules.get("amount", 0)), "Fixed fee per student", False, []

    if t == "milestone":
        by_prog = rules.get("by_programme", [])
        if by_prog:
            milestones = []
            for bp in by_prog:
                if bp.get("programme", "").lower() in prog_lower or prog_lower in bp.get("programme", "").lower():
                    milestones = bp.get("milestones", [])
                    break
            if not milestones:
                milestones = by_prog[0].get("milestones", [])
        else:
            milestones = rules.get("milestones", [])
        total = sum(float(m.get("amount", 0)) for m in milestones)
        return total, f"Milestone-based ({len(milestones)} payments)", True, milestones

    return 0.0, "Unknown rule type", False, []


def calculate_commission(uni, programme, year, tuition, student_count=1):
    """Returns (amount, breakdown, is_milestone, milestones)."""
    if not uni.commission_rules:
        rate = uni.commission_rate or 0.0
        if rate:
            return round(tuition * rate / 100, 2), f"{rate}% of tuition (university default)", False, []
        return 0.0, "No commission rules defined", False, []
    try:
        rules = json.loads(uni.commission_rules)
    except (json.JSONDecodeError, TypeError):
        return 0.0, "Invalid rules configuration", False, []
    return _eval_rule(rules, programme or "", year or 1, tuition or 0.0, student_count)


# ── SESSION TIMEOUT ───────────────────────────────────────────────────────────

@app.before_request
def enforce_session_timeout():
    if "user_id" not in session:
        return
    last_active = session.get("last_active")
    now = datetime.utcnow()
    if last_active:
        try:
            elapsed = now - datetime.fromisoformat(last_active)
            if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                session.clear()
                flash("Your session expired after inactivity. Please log in again.", "error")
                from flask import request as _req
                return redirect(url_for("login", next=_req.path))
        except (ValueError, TypeError):
            pass
    session["last_active"] = now.isoformat()


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
            session.permanent = False
            session["user_id"]    = u.id
            session["user_name"]  = u.name
            session["user_role"]  = u.role
            session["last_active"] = datetime.utcnow().isoformat()
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

    currency_totals = {}
    for cur in ["USD", "GBP", "EUR"]:
        cur_students = [s for s in all_students if s.currency == cur]
        due       = sum(s.commission_amount for s in cur_students)
        collected = sum(s.amount_collected  for s in cur_students)
        currency_totals[cur] = {
            "due": due, "collected": collected, "outstanding": due - collected,
            "students": len(cur_students),
        }

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
        currency_totals=currency_totals,
    )


# ── COMMISSION CALC API ───────────────────────────────────────────────────────

@app.route("/api/commission-calc")
@login_required
def api_commission_calc():
    uni_id    = request.args.get("university_id", "")
    programme = request.args.get("programme_category", "")
    try:
        year = int(request.args.get("year_of_study") or 1)
    except ValueError:
        year = 1
    tuition = parse_float(request.args.get("tuition_amount", 0))

    if not uni_id:
        return jsonify({"amount": 0, "breakdown": "Select a university first", "is_milestone": False, "milestones": []})
    uni = db.session.get(University, int(uni_id))
    if not uni:
        return jsonify({"amount": 0, "breakdown": "University not found", "is_milestone": False, "milestones": []})

    student_count = len(uni.active_students) + 1
    amount, breakdown, is_milestone, milestones = calculate_commission(
        uni, programme, year, tuition, student_count
    )
    return jsonify({"amount": amount, "breakdown": breakdown, "is_milestone": is_milestone, "milestones": milestones})


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


@app.route("/universities/<int:uid>/comments", methods=["POST"])
@login_required
def university_comments(uid):
    u = db.get_or_404(University, uid)
    u.additional_comments = request.form.get("additional_comments", "").strip() or None
    db.session.commit()
    flash("Comments saved.", "success")
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


# ── UNIVERSITY IMPORT / EXPORT ────────────────────────────────────────────────

UNI_FIELDS = [
    "name","country","city","region","commission_rate","commission_notes",
    "incentives","contract_start","contract_end","review_date","target_students",
    "territory","expansion_requested","contract_status","renewal_options",
    "duration","contact_name","contact_email","contact_phone","website",
    "agreement_signed","notes",
]

@app.route("/universities/export")
@login_required
def universities_export():
    unis = University.query.order_by(University.name).all()
    si = io.StringIO()
    w = csv.DictWriter(si, fieldnames=UNI_FIELDS)
    w.writeheader()
    for u in unis:
        w.writerow({
            "name": u.name, "country": u.country or "", "city": u.city or "",
            "region": u.region or "", "commission_rate": u.commission_rate or 0,
            "commission_notes": u.commission_notes or "", "incentives": u.incentives or "",
            "contract_start": u.contract_start or "", "contract_end": u.contract_end or "",
            "review_date": u.review_date or "", "target_students": u.target_students or "",
            "territory": u.territory or "", "expansion_requested": int(u.expansion_requested or 0),
            "contract_status": u.contract_status or "Active",
            "renewal_options": u.renewal_options or "", "duration": u.duration or "",
            "contact_name": u.contact_name or "", "contact_email": u.contact_email or "",
            "contact_phone": u.contact_phone or "", "website": u.website or "",
            "agreement_signed": int(u.agreement_signed or 0), "notes": u.notes or "",
        })
    output = si.getvalue()
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=universities.csv"})


@app.route("/universities/import-template")
@login_required
def universities_import_template():
    si = io.StringIO()
    w = csv.DictWriter(si, fieldnames=UNI_FIELDS)
    w.writeheader()
    w.writerow({
        "name": "Example University", "country": "United Kingdom", "city": "London",
        "region": "UK", "commission_rate": "15", "commission_notes": "15% of first year tuition",
        "incentives": "Bonus 2% if >20 students", "contract_start": "01/09/2024",
        "contract_end": "01/09/2027", "review_date": "01/03/2026",
        "target_students": "20 per year", "territory": "Nigeria, Ghana",
        "expansion_requested": "0", "contract_status": "Active",
        "renewal_options": "2 x 1 year", "duration": "3 years",
        "contact_name": "Jane Smith", "contact_email": "j.smith@example.ac.uk",
        "contact_phone": "+44 20 1234 5678", "website": "https://www.example.ac.uk",
        "agreement_signed": "1", "notes": "Key partner for West Africa",
    })
    output = si.getvalue()
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=universities_template.csv"})


@app.route("/universities/import", methods=["POST"])
@login_required
def universities_import():
    f = request.files.get("csv_file")
    if not f or not f.filename.endswith(".csv"):
        flash("Please upload a valid CSV file.", "error")
        return redirect(url_for("universities"))
    stream = io.StringIO(f.stream.read().decode("utf-8-sig"))
    reader = csv.DictReader(stream)
    added = skipped = 0
    for row in reader:
        name = (row.get("name") or "").strip()
        if not name:
            skipped += 1
            continue
        exists = University.query.filter_by(name=name).first()
        if exists:
            skipped += 1
            continue
        def _bool(v): return str(v).strip() in ("1", "true", "True", "yes", "Yes")
        def _float(v):
            try: return float(v)
            except: return 0.0
        u = University(
            name=name,
            country=(row.get("country") or "").strip() or None,
            city=(row.get("city") or "").strip() or None,
            region=(row.get("region") or "").strip() or None,
            commission_rate=_float(row.get("commission_rate", 0)),
            commission_notes=(row.get("commission_notes") or "").strip() or None,
            incentives=(row.get("incentives") or "").strip() or None,
            contract_start=(row.get("contract_start") or "").strip() or None,
            contract_end=(row.get("contract_end") or "").strip() or None,
            review_date=(row.get("review_date") or "").strip() or None,
            target_students=(row.get("target_students") or "").strip() or None,
            territory=(row.get("territory") or "").strip() or None,
            expansion_requested=_bool(row.get("expansion_requested")),
            contract_status=(row.get("contract_status") or "Active").strip(),
            renewal_options=(row.get("renewal_options") or "").strip() or None,
            duration=(row.get("duration") or "").strip() or None,
            contact_name=(row.get("contact_name") or "").strip() or None,
            contact_email=(row.get("contact_email") or "").strip() or None,
            contact_phone=(row.get("contact_phone") or "").strip() or None,
            website=(row.get("website") or "").strip() or None,
            agreement_signed=_bool(row.get("agreement_signed")),
            notes=(row.get("notes") or "").strip() or None,
        )
        db.session.add(u)
        added += 1
    db.session.commit()
    log_activity("Imported", "Universities", f"Imported {added} universities via CSV")
    flash(f"Import complete: {added} added, {skipped} skipped (duplicate or blank name).", "success")
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
        programme_categories=PROGRAMME_CATEGORIES,
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
    override_str = request.form.get("commission_amount_override", "").strip()
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
        commission_amount_override=parse_float(override_str) if override_str else None,
        currency=request.form.get("currency", "USD"),
        status=request.form.get("status", "Prospect"),
        programme_category=request.form.get("programme_category", "").strip() or None,
        year_of_study=int(request.form.get("year_of_study") or 1),
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
    student_count = len(s.university.active_students)
    _, breakdown, is_milestone, milestones = calculate_commission(
        s.university, s.programme_category, s.year_of_study or 1,
        s.tuition_amount, student_count,
    )
    return render_template("student_detail.html",
        student=s,
        universities=University.query.order_by(University.name).all(),
        programme_categories=PROGRAMME_CATEGORIES,
        comm_breakdown=breakdown,
        comm_is_milestone=is_milestone,
        comm_milestones=milestones,
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
    override_str = request.form.get("commission_amount_override", "").strip()
    s.commission_amount_override = parse_float(override_str) if override_str else None
    s.currency             = request.form.get("currency", s.currency)
    s.status               = request.form.get("status", s.status)
    s.programme_category   = request.form.get("programme_category", "").strip() or None
    s.year_of_study        = int(request.form.get("year_of_study") or 1)
    s.notes                = request.form.get("notes", "").strip()
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


# ── STUDENT IMPORT / EXPORT ───────────────────────────────────────────────────

STU_FIELDS = [
    "name","nationality","email","phone","university_name",
    "program","intake","tuition_amount","currency","commission_rate","status","notes",
]

@app.route("/students/export")
@login_required
def students_export():
    stus = Student.query.order_by(Student.name).all()
    si = io.StringIO()
    w = csv.DictWriter(si, fieldnames=STU_FIELDS)
    w.writeheader()
    for s in stus:
        w.writerow({
            "name": s.name, "nationality": s.nationality or "",
            "email": s.email or "", "phone": s.phone or "",
            "university_name": s.university.name if s.university else "",
            "program": s.program or "", "intake": s.intake or "",
            "tuition_amount": s.tuition_amount or 0,
            "currency": s.currency or "USD",
            "commission_rate": s.commission_rate if s.commission_rate is not None else "",
            "status": s.status or "Prospect", "notes": s.notes or "",
        })
    output = si.getvalue()
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=students.csv"})


@app.route("/students/import-template")
@login_required
def students_import_template():
    si = io.StringIO()
    w = csv.DictWriter(si, fieldnames=STU_FIELDS)
    w.writeheader()
    w.writerow({
        "name": "John Doe", "nationality": "Nigerian", "email": "john@email.com",
        "phone": "+234 800 000 0000", "university_name": "University of Manchester",
        "program": "MSc Computer Science", "intake": "September 2025",
        "tuition_amount": "25000", "currency": "GBP",
        "commission_rate": "", "status": "Enrolled",
        "notes": "Scholarship student",
    })
    output = si.getvalue()
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=students_template.csv"})


@app.route("/students/import", methods=["POST"])
@login_required
def students_import():
    f = request.files.get("csv_file")
    if not f or not f.filename.endswith(".csv"):
        flash("Please upload a valid CSV file.", "error")
        return redirect(url_for("students"))
    stream = io.StringIO(f.stream.read().decode("utf-8-sig"))
    reader = csv.DictReader(stream)
    uni_cache = {u.name.lower(): u for u in University.query.all()}
    added = skipped = 0
    for row in reader:
        name = (row.get("name") or "").strip()
        uni_name = (row.get("university_name") or "").strip()
        if not name or not uni_name:
            skipped += 1
            continue
        uni = uni_cache.get(uni_name.lower())
        if not uni:
            skipped += 1
            continue
        def _float_or_none(v):
            v = (v or "").strip()
            if not v: return None
            try: return float(v)
            except: return None
        def _float(v):
            try: return float(v or 0)
            except: return 0.0
        s = Student(
            name=name,
            nationality=(row.get("nationality") or "").strip() or None,
            email=(row.get("email") or "").strip() or None,
            phone=(row.get("phone") or "").strip() or None,
            university_id=uni.id,
            program=(row.get("program") or "").strip() or None,
            intake=(row.get("intake") or "").strip() or None,
            tuition_amount=_float(row.get("tuition_amount")),
            currency=(row.get("currency") or "USD").strip(),
            commission_rate=_float_or_none(row.get("commission_rate")),
            status=(row.get("status") or "Prospect").strip(),
            notes=(row.get("notes") or "").strip() or None,
        )
        db.session.add(s)
        added += 1
    db.session.commit()
    log_activity("Imported", "Students", f"Imported {added} students via CSV")
    flash(f"Import complete: {added} added, {skipped} skipped (missing name, university not found, or blank row).", "success")
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
