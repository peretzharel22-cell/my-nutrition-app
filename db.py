# -*- coding: utf-8 -*-
import sqlite3
import os
import uuid
import hashlib
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "nutrition_bot.db")


def _conn():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    return con


def _hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    with _conn() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            phone            TEXT PRIMARY KEY,
            name             TEXT,
            age              INTEGER,
            weight_kg        REAL,
            height_cm        REAL,
            sex              TEXT,
            is_kosher        INTEGER NOT NULL DEFAULT 1,
            activity         INTEGER,
            goal             TEXT,
            goal_kg          REAL,
            commitment_label TEXT,
            daily_delta      INTEGER,
            tdee             INTEGER,
            state            TEXT NOT NULL DEFAULT 'NEW',
            last_meat_ts     TEXT,
            water_date       TEXT,
            water_cups       INTEGER NOT NULL DEFAULT 0,
            carb_pref        TEXT,
            spice_pref       TEXT,
            disliked_foods   TEXT,
            last_recipe_key  TEXT,
            last_recipe_cal  INTEGER NOT NULL DEFAULT 0,
            daily_calories   INTEGER NOT NULL DEFAULT 0,
            calories_date    TEXT,
            created_at       TEXT DEFAULT (datetime('now')),
            updated_at       TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS auth_accounts (
            username      TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            phone         TEXT NOT NULL UNIQUE,
            created_at    TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (phone) REFERENCES users(phone)
        );

        CREATE TABLE IF NOT EXISTS meal_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            phone       TEXT NOT NULL,
            meal_id     TEXT NOT NULL,
            meal_name   TEXT NOT NULL,
            meal_type   TEXT NOT NULL,
            category    TEXT NOT NULL,
            calories    INTEGER NOT NULL DEFAULT 0,
            logged_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (phone) REFERENCES users(phone)
        );

        CREATE TABLE IF NOT EXISTS weight_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            phone       TEXT NOT NULL,
            weight_kg   REAL NOT NULL,
            logged_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (phone) REFERENCES users(phone)
        );

        CREATE TABLE IF NOT EXISTS feed_posts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            phone      TEXT NOT NULL,
            username   TEXT NOT NULL,
            content    TEXT NOT NULL,
            posted_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (phone) REFERENCES users(phone)
        );

        CREATE TABLE IF NOT EXISTS community_recipes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            phone        TEXT NOT NULL,
            username     TEXT NOT NULL,
            name         TEXT NOT NULL,
            description  TEXT DEFAULT '',
            ingredients  TEXT DEFAULT '',
            instructions TEXT DEFAULT '',
            category     TEXT DEFAULT 'lunch',
            calories     INTEGER DEFAULT 0,
            protein      INTEGER DEFAULT 0,
            carbs        INTEGER DEFAULT 0,
            fat          INTEGER DEFAULT 0,
            media_url    TEXT DEFAULT '',
            prep_time    TEXT DEFAULT '',
            difficulty   TEXT DEFAULT '',
            shared_at    TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (phone) REFERENCES users(phone)
        );

        CREATE TABLE IF NOT EXISTS recipe_likes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            phone     TEXT NOT NULL,
            liked_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(recipe_id, phone),
            FOREIGN KEY (recipe_id) REFERENCES community_recipes(id),
            FOREIGN KEY (phone) REFERENCES users(phone)
        );

        CREATE TABLE IF NOT EXISTS recipe_saves (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            phone     TEXT NOT NULL,
            saved_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(recipe_id, phone),
            FOREIGN KEY (recipe_id) REFERENCES community_recipes(id),
            FOREIGN KEY (phone) REFERENCES users(phone)
        );
        """)
        _migrate(con)


def _migrate(con):
    # users columns (backward compat for old DBs)
    NEW_COLS = {
        "is_kosher":        "INTEGER NOT NULL DEFAULT 1",
        "water_date":       "TEXT",
        "water_cups":       "INTEGER NOT NULL DEFAULT 0",
        "goal_kg":          "REAL",
        "commitment_label": "TEXT",
        "daily_delta":      "INTEGER",
        "carb_pref":        "TEXT",
        "spice_pref":       "TEXT",
        "disliked_foods":   "TEXT",
        "last_recipe_key":  "TEXT",
        "last_recipe_cal":  "INTEGER NOT NULL DEFAULT 0",
        "daily_calories":   "INTEGER NOT NULL DEFAULT 0",
        "calories_date":    "TEXT",
    }
    existing = {r[1] for r in con.execute("PRAGMA table_info(users)")}
    for col, defn in NEW_COLS.items():
        if col not in existing:
            con.execute(f"ALTER TABLE users ADD COLUMN {col} {defn}")

    ml = {r[1] for r in con.execute("PRAGMA table_info(meal_logs)")}
    if "calories" not in ml:
        con.execute("ALTER TABLE meal_logs ADD COLUMN calories INTEGER NOT NULL DEFAULT 0")

    # community_recipes new columns
    cr_cols = {r[1] for r in con.execute("PRAGMA table_info(community_recipes)")}
    for col, defn in [("media_url", "TEXT DEFAULT ''"),
                      ("prep_time", "TEXT DEFAULT ''"),
                      ("difficulty", "TEXT DEFAULT ''")]:
        if col not in cr_cols:
            con.execute(f"ALTER TABLE community_recipes ADD COLUMN {col} {defn}")

    # Performance indices for social tables
    try:
        con.execute("CREATE INDEX IF NOT EXISTS idx_feed_phone   ON feed_posts(phone)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_cr_phone     ON community_recipes(phone)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_rl_recipe    ON recipe_likes(recipe_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_rs_phone     ON recipe_saves(phone)")
    except Exception:
        pass


# =============================================================================
# Core user functions (unchanged)
# =============================================================================

def get_user(phone):
    with _conn() as con:
        r = con.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
        return dict(r) if r else None


def get_or_create_user(phone):
    u = get_user(phone)
    if u is None:
        with _conn() as con:
            con.execute("INSERT INTO users (phone) VALUES (?)", (phone,))
        u = get_user(phone)
    return u


def update_user(phone, **kw):
    if not kw:
        return
    kw["updated_at"] = datetime.utcnow().isoformat()
    cols = ", ".join(f"{k}=?" for k in kw)
    with _conn() as con:
        con.execute(
            f"UPDATE users SET {cols} WHERE phone=?",
            list(kw.values()) + [phone],
        )


def set_state(phone, state):
    update_user(phone, state=state)


def record_meat_meal(phone):
    update_user(phone, last_meat_ts=datetime.utcnow().isoformat())


def add_water_cup(phone):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    u = get_user(phone)
    if not u:
        return 0
    if u.get("water_date") != today:
        update_user(phone, water_date=today, water_cups=1)
        return 1
    cups = (u.get("water_cups") or 0) + 1
    update_user(phone, water_cups=cups)
    return cups


def set_last_recipe(phone, key, cal):
    update_user(phone, last_recipe_key=key, last_recipe_cal=cal)


def add_daily_calories(phone, cal):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    u = get_user(phone)
    if not u:
        return 0
    if u.get("calories_date") != today:
        update_user(phone, calories_date=today, daily_calories=cal)
        return cal
    total = (u.get("daily_calories") or 0) + cal
    update_user(phone, daily_calories=total)
    return total


def get_daily_calories(phone):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    u = get_user(phone)
    if not u or u.get("calories_date") != today:
        return 0
    return u.get("daily_calories") or 0


def reset_daily_calories(phone):
    update_user(phone, daily_calories=0, calories_date=None)


def log_meal(phone, meal_id, meal_name, meal_type, category, calories=0):
    with _conn() as con:
        con.execute(
            "INSERT INTO meal_logs (phone,meal_id,meal_name,meal_type,category,calories) VALUES (?,?,?,?,?,?)",
            (phone, meal_id, meal_name, meal_type, category, calories),
        )
    if meal_type == "meat":
        record_meat_meal(phone)


def get_today_logs(phone):
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM meal_logs WHERE phone=? AND date(logged_at)=date('now') ORDER BY logged_at",
            (phone,),
        ).fetchall()
        return [dict(r) for r in rows]


def log_weight(phone, weight_kg):
    with _conn() as con:
        con.execute(
            "INSERT INTO weight_logs (phone, weight_kg) VALUES (?, ?)",
            (phone, weight_kg),
        )
    update_user(phone, weight_kg=weight_kg)


def get_weight_history(phone, days=30):
    with _conn() as con:
        rows = con.execute(
            """SELECT date(logged_at) as day, AVG(weight_kg) as weight_kg
               FROM weight_logs WHERE phone=?
               AND logged_at >= datetime('now', ? || ' days')
               GROUP BY date(logged_at) ORDER BY day""",
            (phone, f"-{days}"),
        ).fetchall()
        return [dict(r) for r in rows]


def get_calorie_history(phone, days=7):
    with _conn() as con:
        rows = con.execute(
            """SELECT date(logged_at) as day, SUM(calories) as total
               FROM meal_logs WHERE phone=?
               AND logged_at >= datetime('now', ? || ' days')
               GROUP BY date(logged_at) ORDER BY day""",
            (phone, f"-{days}"),
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_users():
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM users WHERE state='COMPLETED' AND tdee IS NOT NULL ORDER BY name",
        ).fetchall()
        return [dict(r) for r in rows]


# =============================================================================
# Authentication
# =============================================================================

def create_account(username, password):
    """
    Create a new account. Returns (True, phone_uid) on success
    or (False, error_message) on failure.
    """
    username = username.strip().lower()
    if not username or len(username) < 3:
        return False, "שם משתמש חייב להכיל לפחות 3 תווים"
    if get_account_by_username(username):
        return False, "שם המשתמש כבר תפוס"
    phone = f"web_{uuid.uuid4().hex[:12]}"
    pw_hash = _hash_pw(password)
    try:
        with _conn() as con:
            con.execute("INSERT INTO users (phone) VALUES (?)", (phone,))
            con.execute(
                "INSERT INTO auth_accounts (username, password_hash, phone) VALUES (?,?,?)",
                (username, pw_hash, phone),
            )
        return True, phone
    except Exception as exc:
        return False, f"שגיאת מסד נתונים: {exc}"


def authenticate(username, password):
    """
    Verify credentials. Returns (True, phone_uid) or (False, error_message).
    """
    username = username.strip().lower()
    acc = get_account_by_username(username)
    if not acc:
        return False, "שם משתמש לא קיים"
    if acc["password_hash"] != _hash_pw(password):
        return False, "סיסמה שגויה"
    return True, acc["phone"]


def get_account_by_username(username):
    username = username.strip().lower()
    with _conn() as con:
        r = con.execute(
            "SELECT * FROM auth_accounts WHERE username=?", (username,)
        ).fetchone()
        return dict(r) if r else None


def get_username_by_phone(phone):
    with _conn() as con:
        r = con.execute(
            "SELECT username FROM auth_accounts WHERE phone=?", (phone,)
        ).fetchone()
        return r["username"] if r else phone


# =============================================================================
# Community feed
# =============================================================================

def add_feed_post(phone, username, content):
    with _conn() as con:
        con.execute(
            "INSERT INTO feed_posts (phone, username, content) VALUES (?,?,?)",
            (phone, username, content.strip()),
        )


def get_feed_posts(limit=40):
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM feed_posts ORDER BY posted_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_feed_post(post_id, phone):
    """Delete a post only if it belongs to the requesting user."""
    with _conn() as con:
        con.execute(
            "DELETE FROM feed_posts WHERE id=? AND phone=?",
            (post_id, phone),
        )


def get_posts_by_user(phone):
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM feed_posts WHERE phone=? ORDER BY posted_at DESC",
            (phone,),
        ).fetchall()
        return [dict(r) for r in rows]


# =============================================================================
# Community recipes
# =============================================================================

def share_recipe(phone, username, name, description, ingredients,
                 instructions, category, calories, protein, carbs, fat,
                 media_url="", prep_time="", difficulty=""):
    """Insert a community recipe. Returns the new row id."""
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO community_recipes
               (phone, username, name, description, ingredients, instructions,
                category, calories, protein, carbs, fat,
                media_url, prep_time, difficulty)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (phone, username, name, description, ingredients, instructions,
             category, int(calories), int(protein), int(carbs), int(fat),
             str(media_url).strip(), str(prep_time).strip(), str(difficulty).strip()),
        )
        return cur.lastrowid


def get_community_recipes(limit=50):
    with _conn() as con:
        rows = con.execute(
            """SELECT cr.*,
               (SELECT COUNT(*) FROM recipe_likes  rl WHERE rl.recipe_id = cr.id) AS likes_count,
               (SELECT COUNT(*) FROM recipe_saves  rs WHERE rs.recipe_id = cr.id) AS saves_count
               FROM community_recipes cr
               ORDER BY cr.shared_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_top_community_recipes(category=None, limit=3):
    """Return top-rated community recipes sorted by likes count (ranking bias)."""
    with _conn() as con:
        if category:
            rows = con.execute(
                """SELECT cr.*,
                   (SELECT COUNT(*) FROM recipe_likes rl WHERE rl.recipe_id = cr.id) AS likes_count,
                   (SELECT COUNT(*) FROM recipe_saves rs WHERE rs.recipe_id = cr.id) AS saves_count
                   FROM community_recipes cr
                   WHERE cr.category = ?
                   ORDER BY likes_count DESC, cr.shared_at DESC
                   LIMIT ?""",
                (category, limit),
            ).fetchall()
        else:
            rows = con.execute(
                """SELECT cr.*,
                   (SELECT COUNT(*) FROM recipe_likes rl WHERE rl.recipe_id = cr.id) AS likes_count,
                   (SELECT COUNT(*) FROM recipe_saves rs WHERE rs.recipe_id = cr.id) AS saves_count
                   FROM community_recipes cr
                   ORDER BY likes_count DESC, cr.shared_at DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]


def get_recipes_by_user(phone):
    with _conn() as con:
        rows = con.execute(
            """SELECT cr.*,
               (SELECT COUNT(*) FROM recipe_likes rl WHERE rl.recipe_id = cr.id) AS likes_count
               FROM community_recipes cr
               WHERE cr.phone = ?
               ORDER BY cr.shared_at DESC""",
            (phone,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_saved_recipes(phone):
    with _conn() as con:
        rows = con.execute(
            """SELECT cr.*,
               (SELECT COUNT(*) FROM recipe_likes rl WHERE rl.recipe_id = cr.id) AS likes_count
               FROM community_recipes cr
               JOIN recipe_saves rs ON rs.recipe_id = cr.id
               WHERE rs.phone = ?
               ORDER BY rs.saved_at DESC""",
            (phone,),
        ).fetchall()
        return [dict(r) for r in rows]


def toggle_like(recipe_id, phone):
    """Like or unlike. Returns new like count."""
    with _conn() as con:
        existing = con.execute(
            "SELECT id FROM recipe_likes WHERE recipe_id=? AND phone=?",
            (recipe_id, phone),
        ).fetchone()
        if existing:
            con.execute(
                "DELETE FROM recipe_likes WHERE recipe_id=? AND phone=?",
                (recipe_id, phone),
            )
        else:
            con.execute(
                "INSERT INTO recipe_likes (recipe_id, phone) VALUES (?,?)",
                (recipe_id, phone),
            )
        count = con.execute(
            "SELECT COUNT(*) FROM recipe_likes WHERE recipe_id=?",
            (recipe_id,),
        ).fetchone()[0]
        return int(count)


def toggle_save(recipe_id, phone):
    """Save or unsave. Returns True if now saved."""
    with _conn() as con:
        existing = con.execute(
            "SELECT id FROM recipe_saves WHERE recipe_id=? AND phone=?",
            (recipe_id, phone),
        ).fetchone()
        if existing:
            con.execute(
                "DELETE FROM recipe_saves WHERE recipe_id=? AND phone=?",
                (recipe_id, phone),
            )
            return False
        con.execute(
            "INSERT INTO recipe_saves (recipe_id, phone) VALUES (?,?)",
            (recipe_id, phone),
        )
        return True


def get_liked_recipe_ids(phone):
    """Return set of recipe_ids liked by user."""
    with _conn() as con:
        rows = con.execute(
            "SELECT recipe_id FROM recipe_likes WHERE phone=?", (phone,)
        ).fetchall()
        return {r[0] for r in rows}


def get_saved_recipe_ids(phone):
    """Return set of recipe_ids saved by user."""
    with _conn() as con:
        rows = con.execute(
            "SELECT recipe_id FROM recipe_saves WHERE phone=?", (phone,)
        ).fetchall()
        return {r[0] for r in rows}
