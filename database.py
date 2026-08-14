"""
database.py – SQLite setup and all query helpers for CaliTrack.
"""
import sqlite3
import bcrypt
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "calitrack.db"

## Veritabanına bağlanarak dosya oluştur.
## Sorgu sonuçlarını sözlük gibi kullan
## Tablolar arası ilişkileri aktif et
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ── Schema ────────────────────────────────────────────────────────────────────

## Veritabanı tablolarını oluştur.
# Her satıra benzersiz numara var. Tablo yoksa oluştur.
# Her açılışta init_db fonsksiyonunu çağır, böylece mevcut verileri silme.
# init_db = veritabanını oluşyur.
# USERNAME benzersizliği için unique ifadesi kullanılmıştır.
# password hash ile şifrenin kendisi değil bcryp i saklanıyor.
# not null = boş bırakılamaz.
# on delete cascade ile user silinirse cihaz listesini de otomatik siler.
# INTEGER → id bir tam sayıdır.
# PRIMARY KEY → Her kaydı benzersiz şekilde tanımlar. Aynı id iki kayıtta olamaz.
# AUTOINCREMENT → Yeni kayıt eklenirken id otomatik olarak artırılır.
# ON DELETE CASCADE = user ile silinirse cihaz listesini de otomatik siler.
def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT, 
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            role          TEXT    NOT NULL DEFAULT 'user',  -- 'user' | 'admin'
            created_at    TEXT    NOT NULL DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS device_catalog (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            name                     TEXT NOT NULL,
            brand                    TEXT,
            model                    TEXT,
            calibration_interval_days INTEGER NOT NULL DEFAULT 365,
            created_at               TEXT NOT NULL DEFAULT (date('now'))
        );
        
        CREATE TABLE IF NOT EXISTS user_devices (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL REFERENCES users(id)          ON DELETE CASCADE,
            catalog_device_id INTEGER NOT NULL REFERENCES device_catalog(id) ON DELETE CASCADE,
            added_at         TEXT NOT NULL DEFAULT (date('now')),
            UNIQUE(user_id, catalog_device_id)
        );

        CREATE TABLE IF NOT EXISTS calibration_records (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            catalog_device_id   INTEGER NOT NULL REFERENCES device_catalog(id) ON DELETE CASCADE,
            calibration_date    TEXT NOT NULL,
            next_calibration_date TEXT NOT NULL,
            performed_by        TEXT NOT NULL,
            notes               TEXT,
            created_by          INTEGER REFERENCES users(id),
            created_at          TEXT NOT NULL DEFAULT (date('now'))
        );
        """)
        _seed_admin(conn)

# admin hesabı oluştur, şifresini admin123 yap.

def _seed_admin(conn):
    """Create a default admin account if none exists."""
    row = conn.execute("SELECT id FROM users WHERE role='admin' LIMIT 1").fetchone()
    if not row:
        hashed = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
            ("admin", hashed)
        )

# ── Auth ──────────────────────────────────────────────────────────────────────
# User ismi 3 karakterden büyük olmalıdır.
# Password 6 karakterden büyük olmalıdır.

def register_user(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed)
            )
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already taken."

# fetchone veritabanından bir sayır alır. dict(row) o satırı bir Python sözlüğüne dönüştürür.

def login_user(username: str, password: str):
    """Returns user dict or None."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return dict(row)
    return None

# ── Device catalog ────────────────────────────────────────────────────────────

# Cihaz katalogunu isim sırasına göre getirir. fetchall tüm satırları alır.

def get_catalog():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM device_catalog ORDER BY name"
        ).fetchall()]
        
def add_catalog_device(name, brand, model, interval_days):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO device_catalog (name, brand, model, calibration_interval_days) VALUES (?,?,?,?)",
            (name, brand, model, interval_days)
        )
        
def update_catalog_device(device_id, name, brand, model, interval_days):
    with get_conn() as conn:
        conn.execute(
            "UPDATE device_catalog SET name=?, brand=?, model=?, calibration_interval_days=? WHERE id=?",
            (name, brand, model, interval_days, device_id)
        )

def delete_catalog_device(device_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM device_catalog WHERE id=?", (device_id,))

# ── User devices ──────────────────────────────────────────────────────────────

def get_user_devices(user_id: int):
    """Return user's device list with latest calibration info."""
    sql = """
    SELECT
        ud.id            AS user_device_id,
        dc.id            AS catalog_id,
        dc.name,
        dc.brand,
        dc.model,
        dc.calibration_interval_days,
        cr.calibration_date,
        cr.next_calibration_date,
        cr.performed_by,
        cr.notes
    FROM user_devices ud
    JOIN device_catalog dc ON dc.id = ud.catalog_device_id
    LEFT JOIN calibration_records cr
        ON cr.id = (
            SELECT id FROM calibration_records
            WHERE catalog_device_id = dc.id
            ORDER BY calibration_date DESC
            LIMIT 1
        )
    WHERE ud.user_id = ?
    ORDER BY dc.name
    """
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, (user_id,)).fetchall()]


def add_user_device(user_id: int, catalog_device_id: int) -> tuple[bool, str]:
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO user_devices (user_id, catalog_device_id) VALUES (?,?)",
                (user_id, catalog_device_id)
            )
        return True, "Device added to your list."
    except sqlite3.IntegrityError:
        return False, "Device already in your list."


def remove_user_device(user_device_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM user_devices WHERE id=?", (user_device_id,))


# ── Calibration records ───────────────────────────────────────────────────────

def add_calibration_record(catalog_device_id, calibration_date, performed_by, notes, created_by):
    with get_conn() as conn:
        device = conn.execute(
            "SELECT calibration_interval_days FROM device_catalog WHERE id=?",
            (catalog_device_id,)
        ).fetchone()
        interval = device["calibration_interval_days"] if device else 365
        cal_dt = date.fromisoformat(calibration_date)
        next_dt = cal_dt + timedelta(days=interval)
        conn.execute(
            """INSERT INTO calibration_records
               (catalog_device_id, calibration_date, next_calibration_date, performed_by, notes, created_by)
               VALUES (?,?,?,?,?,?)""",
            (catalog_device_id, str(cal_dt), str(next_dt), performed_by, notes, created_by)
        )


def get_calibration_history(catalog_device_id: int):
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            """SELECT cr.*, u.username as entered_by
               FROM calibration_records cr
               LEFT JOIN users u ON u.id = cr.created_by
               WHERE cr.catalog_device_id = ?
               ORDER BY cr.calibration_date DESC""",
            (catalog_device_id,)
        ).fetchall()]


# ── Alerts (admin) ────────────────────────────────────────────────────────────

def get_overdue_devices():
    """Devices whose next calibration date has passed or is within 30 days."""
    today = str(date.today())
    warn_date = str(date.today() + timedelta(days=30))
    sql = """
    SELECT
        dc.id, dc.name, dc.brand, dc.model,
        cr.calibration_date,
        cr.next_calibration_date
    FROM device_catalog dc
    LEFT JOIN calibration_records cr
        ON cr.id = (
            SELECT id FROM calibration_records
            WHERE catalog_device_id = dc.id
            ORDER BY calibration_date DESC LIMIT 1
        )
    WHERE cr.next_calibration_date IS NULL
       OR cr.next_calibration_date <= ?
    ORDER BY cr.next_calibration_date ASC
    """
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, (warn_date,)).fetchall()]
