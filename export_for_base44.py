# -*- coding: utf-8 -*-
"""
export_for_base44.py
Generates 3 CSV files + 1 skills manual for Base44 migration.
Run: python3 export_for_base44.py
"""

import sqlite3
import csv
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "nutrition_bot.db")
OUT_DIR  = os.path.dirname(__file__)

GOAL_LABELS = {
    "bulk":     "הגדלת מסה שרירית",
    "cut":      "ירידה במשקל",
    "maintain": "שמירה על המשקל",
}

def _conn():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


# ─────────────────────────────────────────────
# 1. users_social.csv
# ─────────────────────────────────────────────
def export_users():
    path = os.path.join(OUT_DIR, "users_social.csv")
    con = _conn()

    rows = con.execute("""
        SELECT
            u.phone                                        AS user_id,
            COALESCE(a.username, u.phone)                  AS username,
            a.password_hash,
            u.name                                         AS display_name,
            u.age,
            u.sex,
            u.weight_kg,
            u.height_cm,
            u.goal                                         AS goal_key,
            u.goal_kg,
            u.commitment_label,
            u.tdee,
            u.daily_delta,
            u.is_kosher,
            u.carb_pref,
            u.spice_pref,
            u.disliked_foods                               AS dietary_restrictions,
            u.activity,
            u.state                                        AS profile_state,
            u.created_at,
            rt.token                                       AS remember_me_token,
            rt.created_at                                  AS token_created_at
        FROM users u
        LEFT JOIN auth_accounts a   ON a.phone = u.phone
        LEFT JOIN remember_tokens rt ON rt.phone = u.phone
        ORDER BY u.created_at
    """).fetchall()

    fields = [
        "user_id", "username", "password_hash", "display_name",
        "age", "sex", "weight_kg", "height_cm",
        "goal_key", "goal_label", "goal_kg", "commitment_label",
        "tdee", "daily_delta", "is_kosher", "carb_pref", "spice_pref",
        "dietary_restrictions", "activity", "profile_state",
        "created_at", "remember_me_token", "token_created_at",
    ]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            d = dict(r)
            d["goal_label"] = GOAL_LABELS.get(d.get("goal_key", ""), "")
            w.writerow({k: d.get(k, "") for k in fields})

    con.close()
    print(f"  ✓ users_social.csv        — {len(rows)} rows  →  {path}")
    return len(rows)


# ─────────────────────────────────────────────
# 2. community_recipes.csv
# ─────────────────────────────────────────────
def export_recipes():
    path = os.path.join(OUT_DIR, "community_recipes.csv")
    con = _conn()

    rows = con.execute("""
        SELECT
            cr.id              AS recipe_id,
            cr.phone           AS creator_user_id,
            COALESCE(a.username, cr.username) AS creator_username,
            cr.name,
            cr.description,
            cr.category,
            cr.calories,
            cr.protein,
            cr.carbs,
            cr.fat,
            cr.ingredients,
            cr.instructions,
            cr.prep_time,
            cr.difficulty,
            cr.media_url,
            cr.shared_at,
            COUNT(DISTINCT rl.id)  AS total_likes,
            COUNT(DISTINCT rs.id)  AS total_saves
        FROM community_recipes cr
        LEFT JOIN auth_accounts a  ON a.phone = cr.phone
        LEFT JOIN recipe_likes  rl ON rl.recipe_id = cr.id
        LEFT JOIN recipe_saves  rs ON rs.recipe_id = cr.id
        GROUP BY cr.id
        ORDER BY total_likes DESC, cr.shared_at DESC
    """).fetchall()

    fields = [
        "recipe_id", "creator_user_id", "creator_username",
        "name", "description", "category",
        "calories", "protein", "carbs", "fat",
        "ingredients", "instructions",
        "prep_time", "difficulty", "media_url",
        "shared_at", "total_likes", "total_saves",
    ]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: dict(r).get(k, "") for k in fields})

    con.close()
    print(f"  ✓ community_recipes.csv   — {len(rows)} rows  →  {path}")
    return len(rows)


# ─────────────────────────────────────────────
# 3. meal_logs.csv
# ─────────────────────────────────────────────
def export_meal_logs():
    path = os.path.join(OUT_DIR, "meal_logs.csv")
    con = _conn()

    rows = con.execute("""
        SELECT
            ml.id,
            ml.phone                                       AS user_id,
            COALESCE(a.username, ml.phone)                 AS username,
            ml.meal_id,
            ml.meal_name,
            ml.meal_type,
            ml.category,
            ml.calories,
            ml.logged_at,
            DATE(ml.logged_at)                             AS log_date,
            TIME(ml.logged_at)                             AS log_time
        FROM meal_logs ml
        LEFT JOIN auth_accounts a ON a.phone = ml.phone
        ORDER BY ml.logged_at DESC
    """).fetchall()

    fields = [
        "id", "user_id", "username",
        "meal_id", "meal_name", "meal_type", "category",
        "calories", "logged_at", "log_date", "log_time",
    ]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: dict(r).get(k, "") for k in fields})

    con.close()
    print(f"  ✓ meal_logs.csv           — {len(rows)} rows  →  {path}")
    return len(rows)


# ─────────────────────────────────────────────
# 4. base44_skills_manual.txt
# ─────────────────────────────────────────────
SKILLS_TEXT = """=======================================================
  BASE44 SKILLS MANUAL — Nutrition Bot Social Logic
  Generated: {ts}
=======================================================

--- OVERVIEW ---
This app is a Hebrew-language social nutrition platform.
Users set fitness goals (bulk/cut/maintain), receive a
personalised daily meal plan, track calories, and
participate in a community feed and recipe library.

--- DATA MODEL ---

users_social.csv
  Primary key : user_id  (format: "web_<12hex>" for web users)
  Auth        : username + password_hash (SHA-256)
  Remember Me : remember_me_token — pass as Bearer token
                to API header:  Authorization: Bearer <token>
  Goal fields : goal_key (bulk|cut|maintain), goal_kg,
                commitment_label, tdee, daily_delta
  Preferences : is_kosher (1/0), carb_pref (carbs|fats),
                spice_pref (spicy|mild), dietary_restrictions

community_recipes.csv
  Primary key : recipe_id
  Owner link  : creator_user_id → users_social.user_id
  Engagement  : total_likes, total_saves (aggregated counts)
  Macros      : calories, protein, carbs, fat (integers)
  Category    : breakfast | lunch | dinner | snack

meal_logs.csv
  Primary key : id
  User link   : user_id → users_social.user_id
  Time keys   : log_date (YYYY-MM-DD), log_time (HH:MM:SS)
  Category    : breakfast | lunch | dinner | snack
  Type        : meat | dairy | pareve  (kosher classification)

--- SOCIAL LOGIC ---

1. RECIPE LIKES
   A user can like any community recipe once (toggle).
   Table: recipe_likes(recipe_id, user_id, liked_at)
   Logic: If row exists → remove (unlike). Else → insert (like).
   API  : POST /recipes/community/{{recipe_id}}/like
          Returns: {{"liked": true|false}}
   Display: show count from total_likes column.
            Heart icon filled (❤️) if liked_by_me=true.

2. RECIPE SAVES (Bookmarks)
   Identical toggle pattern to likes.
   Table: recipe_saves(recipe_id, user_id, saved_at)
   API  : POST /recipes/community/{{recipe_id}}/save
          Returns: {{"saved": true|false}}
   Personal feed: GET /users/me/saved-recipes

3. COMMUNITY FEED POSTS
   Any logged-in user can publish a short text update (≤500 chars).
   Posts are global (no following — everyone sees all posts).
   API  : POST /feed  {{"content": "..."}}
           GET /feed?limit=40   (newest first)
        DELETE /feed/{{post_id}}  (owner only)

4. USER-FOLLOW SYSTEM
   ⚠ NOT IMPLEMENTED in current version.
   The feed is a global timeline — all users see all posts.
   To implement following in Base44:
     a. Add a "user_follows" table: (follower_id, followee_id, followed_at)
     b. Filter GET /feed to only return posts from followed users.
     c. Add POST /users/{id}/follow  and  DELETE /users/{id}/follow endpoints.

5. RECIPE SHARING
   Authenticated users post new recipes via:
   POST /recipes/community
   Body: {{name, ingredients, category, calories, protein, carbs, fat,
           description?, instructions?, prep_time?, difficulty?, media_url?}}
   The system auto-fills creator_user_id and creator_username from the token.

6. KOSHER RULES (meal planning logic)
   is_kosher=1 means:
     • Meat and dairy meals cannot appear in the same day window.
     • After a meat meal, a 6-hour cooldown blocks dairy suggestions.
     • meal_type field: "meat" | "dairy" | "pareve"
   This logic lives in handler.py (_kosher_ok, _meat_wait_hours).

--- AUTH FLOW FOR BASE44 ---

Step 1: POST /auth/login  →  receive token
Step 2: Store token in Base44 component state.
Step 3: Attach to every API call:
        Header: Authorization: Bearer <token>
Step 4: Token persists 30 days (remember_tokens table).
        On logout: POST /auth/logout  (token deleted server-side).

--- PASSWORD MIGRATION ---

Passwords are stored as SHA-256 hashes (hex string, 64 chars).
To validate a login attempt in Base44:
  hash_input = sha256(user_input_password).hexdigest()
  match = (hash_input == stored password_hash)
No salt is used in the current scheme — plan to upgrade to
bcrypt or Argon2 before public launch.

--- API BASE URL ---

Production (ngrok): https://reluctant-granular-curliness.ngrok-free.dev
Local dev         : http://localhost:8000
Interactive docs  : <base_url>/docs

Required header for all protected endpoints:
  Authorization: Bearer <token>
  ngrok-skip-browser-warning: true   (ngrok free tier only)

=======================================================
"""

def export_skills_manual():
    path = os.path.join(OUT_DIR, "base44_skills_manual.txt")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = SKILLS_TEXT.replace("{ts}", ts)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ base44_skills_manual.txt            →  {path}")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Base44 Migration Export ===\n")
    n_users   = export_users()
    n_recipes = export_recipes()
    n_logs    = export_meal_logs()
    export_skills_manual()
    print(f"\nDone. Summary: {n_users} users | {n_recipes} recipes | {n_logs} meal logs")
    print("Files written to:", OUT_DIR)
