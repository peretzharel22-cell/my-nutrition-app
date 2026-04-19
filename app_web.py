# -*- coding: utf-8 -*-
"""app_web.py - Streamlit nutrition dashboard — Netflix Dark Theme"""
import uuid
import streamlit as st
import pandas as pd
from datetime import date, datetime

import db
import handler
from handler import (
    RECIPES,
    COMMITMENT,
    _sorted_keys,
    _target,
    _tdee,
    fetch_web_recipe,
)

# ─── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="תזונה חכמה", layout="wide", page_icon="🍽️")

NETFLIX_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;900&display=swap" rel="stylesheet">
<style>
/* ── Base ─────────────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #141414 !important;
    color: #e5e5e5 !important;
    font-family: 'Heebo', sans-serif !important;
    direction: rtl;
    text-align: right;
}
[data-testid="stApp"] { background-color: #141414 !important; }
[data-testid="block-container"] { background-color: #141414 !important; }

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0d0d0d !important;
    border-right: 2px solid #E50914;
}
[data-testid="stSidebar"] * { color: #e5e5e5 !important; }
[data-testid="stSidebar"] button {
    background: #E50914 !important;
    border: none !important;
    color: #fff !important;
    border-radius: 4px !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
    transition: background .2s, transform .15s !important;
}
[data-testid="stSidebar"] button:hover {
    background: #b0060f !important;
    transform: scale(1.03) !important;
}

/* ── Headers ─────────────────────────────────────────────────────────────── */
h1, h2, h3, h4 {
    font-family: 'Heebo', sans-serif !important;
    color: #ffffff !important;
    font-weight: 900 !important;
}
h1 { font-size: 2.4rem !important; letter-spacing: -.5px; }
h2 { font-size: 1.9rem !important; }
h3 { font-size: 1.4rem !important; }

/* ── Progress bar ────────────────────────────────────────────────────────── */
.stProgress > div > div { background: #E50914 !important; border-radius: 4px; }
.stProgress > div { background: #2a2a2a !important; border-radius: 4px; }

/* ── Buttons ─────────────────────────────────────────────────────────────── */
button[kind="primary"] {
    background: #E50914 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    transition: background .2s, transform .15s !important;
}
button[kind="primary"]:hover {
    background: #b0060f !important;
    transform: scale(1.03) !important;
}
button[kind="secondary"] {
    background: transparent !important;
    color: #e5e5e5 !important;
    border: 1px solid #555 !important;
    border-radius: 4px !important;
    font-family: 'Heebo', sans-serif !important;
    transition: border-color .2s, transform .15s !important;
}
button[kind="secondary"]:hover {
    border-color: #E50914 !important;
    color: #E50914 !important;
    transform: scale(1.03) !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] button {
    background: transparent !important;
    color: #aaa !important;
    border-bottom: 2px solid transparent !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 8px 16px !important;
    transition: color .2s !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #E50914 !important;
    border-bottom: 2px solid #E50914 !important;
}
[data-testid="stTabs"] button:hover { color: #fff !important; }

/* ── Inputs & Selects ────────────────────────────────────────────────────── */
input, textarea, select, [data-baseweb="input"] input,
[data-baseweb="select"] div {
    background: #2a2a2a !important;
    color: #e5e5e5 !important;
    border: 1px solid #444 !important;
    border-radius: 4px !important;
    font-family: 'Heebo', sans-serif !important;
}
input:focus, textarea:focus { border-color: #E50914 !important; outline: none !important; }
label { color: #bbb !important; font-family: 'Heebo', sans-serif !important; }

/* ── Metrics ─────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #1e1e1e !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    padding: 12px !important;
}
[data-testid="stMetricValue"] { color: #E50914 !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #aaa !important; }

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr { border-color: #2a2a2a !important; }

/* ── Alerts ──────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: #1e1e1e !important;
    border-left: 4px solid #E50914 !important;
    border-radius: 4px !important;
    color: #e5e5e5 !important;
}

/* ── Tables ──────────────────────────────────────────────────────────────── */
table { background: #1e1e1e !important; color: #e5e5e5 !important; width: 100% !important; }
th { background: #E50914 !important; color: #fff !important; padding: 10px !important; }
td { padding: 8px 12px !important; border-bottom: 1px solid #2a2a2a !important; }

/* ── Expander ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #1e1e1e !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    margin-bottom: 4px !important;
}
[data-testid="stExpander"] summary {
    color: #e5e5e5 !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
}

/* ── Recipe Card ─────────────────────────────────────────────────────────── */
.recipe-card {
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 16px;
    transition: transform .2s, box-shadow .2s, border-color .2s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.recipe-card:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 32px rgba(229,9,20,.25);
    border-color: #E50914;
}
.recipe-card::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 4px;
    height: 100%;
    background: #E50914;
    border-radius: 0 10px 10px 0;
}
.recipe-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 6px;
}
.recipe-meta {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    font-size: .88rem;
    color: #aaa;
    margin-bottom: 8px;
}
.recipe-meta span { display: flex; align-items: center; gap: 4px; }
.badge {
    display: inline-block;
    background: #E50914;
    color: #fff;
    font-size: .75rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 12px;
    margin-right: 6px;
}
.badge-prep {
    background: #2a2a2a;
    border: 1px solid #444;
    color: #ccc;
}
.ing-chip {
    display: inline-block;
    background: #2a2a2a;
    border: 1px solid #333;
    color: #ccc;
    font-size: .8rem;
    padding: 2px 10px;
    border-radius: 20px;
    margin: 2px;
}
.community-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 16px;
    transition: transform .2s, border-color .2s, box-shadow .2s;
    height: 100%;
}
.community-card:hover {
    transform: scale(1.03);
    border-color: #E50914;
    box-shadow: 0 6px 24px rgba(229,9,20,.2);
}
.community-card .recipe-title { font-size: 1.05rem; }
.cal-badge {
    font-size: 1.3rem;
    font-weight: 900;
    color: #E50914;
}
</style>
"""

st.markdown(NETFLIX_CSS, unsafe_allow_html=True)

db.init_db()

# ─── Session state ─────────────────────────────────────────────────────────────
for _k, _v in [("uid", None), ("step", 1), ("reg", {}), ("registering", False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

for _cat in ("breakfast", "lunch", "dinner"):
    if ("swap_" + _cat) not in st.session_state:
        st.session_state["swap_" + _cat] = 0
    if ("web_" + _cat) not in st.session_state:
        st.session_state["web_" + _cat] = None


# ─── Helpers ───────────────────────────────────────────────────────────────────
def _next(d=None):
    if d:
        st.session_state.reg.update(d)
    st.session_state.step += 1
    st.rerun()


def _back():
    st.session_state.step = max(1, st.session_state.step - 1)
    st.rerun()


def _safe_web(cat):
    r = st.session_state.get("web_" + cat)
    if not isinstance(r, dict):
        return None
    if not {"name", "cal", "pro", "carb", "fat"}.issubset(r):
        return None
    return r


def _type_label(t):
    return {"meat": "בשרי", "dairy": "חלבי", "pareve": "פרווה"}.get(t, t)


def _render_recipe_card(r, key_prefix="", show_buttons=False, uid=None,
                         cat=None, idx=None, keys=None, web_r=None):
    """Render a Netflix-style recipe card with expander for full details."""
    src_badge = '<span class="badge">רשת</span>' if r.get("source") in ("web", "fallback") else ""
    type_badge = f'<span class="badge badge-prep">{_type_label(r.get("type",""))}</span>'
    prep_badge = f'<span class="badge badge-prep">⏱ {r.get("prep","---")}</span>'

    card_html = f"""
    <div class="recipe-card">
        <div class="recipe-title">{src_badge}{r.get('name','---')}</div>
        <div class="recipe-meta">
            <span>🔥 <b style="color:#E50914">{r.get('cal',0)}</b> קל'</span>
            <span>💪 {r.get('pro',0)}g חלבון</span>
            <span>🌾 {r.get('carb',0)}g פחמימות</span>
            <span>🥑 {r.get('fat',0)}g שומן</span>
        </div>
        <div>{type_badge}{prep_badge}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Expandable details
    with st.expander("פרטים מלאים ומרכיבים"):
        ings = r.get("ingredients") or []
        if ings:
            chips = "".join(f'<span class="ing-chip">{i}</span>' for i in ings)
            st.markdown(
                f'<div style="margin-bottom:10px"><b style="color:#E50914">מרכיבים:</b><br>{chips}</div>',
                unsafe_allow_html=True,
            )
        steps = r.get("steps") or []
        if steps:
            st.markdown('<b style="color:#E50914">הכנה:</b>', unsafe_allow_html=True)
            for s in steps:
                st.markdown(
                    f'<div style="color:#ccc;padding:3px 0;border-bottom:1px solid #2a2a2a">{s}</div>',
                    unsafe_allow_html=True,
                )

    if show_buttons and uid and cat is not None:
        b1, b2, b3, b4 = st.columns(4)
        if b1.button("✔ אכלתי", key=key_prefix + "ate", use_container_width=True, type="primary"):
            cal = int(r.get("cal", 0))
            db.add_daily_calories(uid, cal)
            db.log_meal(
                uid,
                keys[idx] if not web_r else "web",
                str(r.get("name", "")),
                str(r.get("type", "pareve")),
                cat,
                cal,
            )
            if r.get("type") == "meat":
                db.update_user(uid, last_meat_ts=datetime.utcnow().isoformat())
            st.toast(str(r.get("name", "")) + " — " + str(cal) + " קל'")
            st.rerun()

        if b2.button("🔄 החלף", key=key_prefix + "swap", use_container_width=True):
            st.session_state["web_" + cat] = None
            st.session_state["swap_" + cat] = (idx + 1) % len(keys)
            st.rerun()

        if b3.button("🌐 מהרשת", key=key_prefix + "web", use_container_width=True):
            off = st.session_state.get("web_off_" + cat, 0)
            with st.spinner("מחפש מתכון..."):
                wr = fetch_web_recipe(cat, st.session_state.get("_user_obj_", {}), off)
            if wr and isinstance(wr, dict):
                st.session_state["web_" + cat] = wr
                st.session_state["web_off_" + cat] = off + 1
            else:
                st.warning("לא נמצא מתכון, נסה שוב.")
            st.rerun()

        if web_r:
            if b4.button("📂 מקומי", key=key_prefix + "local", use_container_width=True):
                st.session_state["web_" + cat] = None
                st.rerun()


# ─── Registration Steps ────────────────────────────────────────────────────────
def _reg_step1():
    st.subheader("שלב 1/4 — פרטים אישיים")
    with st.form("s1"):
        name = st.text_input("שם מלא", placeholder="הזן שם...")
        sex = st.radio("מין ביולוגי", ["זכר", "נקבה"], horizontal=True)
        if st.form_submit_button("הבא ▶", use_container_width=True, type="primary"):
            if not name.strip():
                st.error("נא להזין שם")
            else:
                _next({"name": name.strip(), "sex": "M" if sex == "זכר" else "F"})


def _reg_step2():
    st.subheader("שלב 2/4 — נתונים פיזיים")
    d = st.session_state.reg
    with st.form("s2"):
        c1, c2 = st.columns(2)
        age = c1.number_input("גיל (שנים)", 16, 80, int(d.get("age", 25)), step=1)
        height = c2.number_input("גובה (ס\"מ)", 140, 220, int(d.get("height_cm", 170)), step=1)
        weight = c1.number_input(
            "משקל (ק\"ג)", 35.0, 200.0, float(d.get("weight_kg", 70)), step=0.5, format="%.1f"
        )
        act = c2.selectbox(
            "פעילות גופנית",
            [1, 2, 3, 4, 5],
            index=int(d.get("activity", 2)) - 1,
            format_func=lambda x: {
                1: "1 — יושבני", 2: "2 — קל", 3: "3 — מתון",
                4: "4 — פעיל", 5: "5 — אינטנסיבי",
            }[x],
        )
        bc, nc = st.columns(2)
        if bc.form_submit_button("◀ חזור", use_container_width=True):
            _back()
        if nc.form_submit_button("הבא ▶", use_container_width=True, type="primary"):
            _next({
                "age": int(age), "height_cm": int(height),
                "weight_kg": float(weight), "activity": int(act),
            })


def _reg_step3():
    st.subheader("שלב 3/4 — כשרות וטעם")
    d = st.session_state.reg
    with st.form("s3"):
        kosher = st.toggle("שמירת כשרות (הפרדת בשר/חלב 6 שעות)", value=bool(d.get("is_kosher", 1)))
        st.markdown("---")
        pref = st.radio(
            "העדפת מזון",
            ["פחמימות (פסטה, אורז, לחם)", "שומנים בריאים (אבוקדו, דגים, אגוזים)"],
            index=0 if d.get("carb_pref", "carbs") == "carbs" else 1,
        )
        spice = st.radio("טעם מועדף", ["חריף", "עדין"], index=0 if d.get("spice_pref") == "spicy" else 1, horizontal=True)
        dis = st.text_input("מאכלים שאינך אוהב (פסיק בין כל אחד)", value=d.get("disliked_foods", ""), placeholder="עגבנייה, גבינה...")
        bc, nc = st.columns(2)
        if bc.form_submit_button("◀ חזור", use_container_width=True):
            _back()
        if nc.form_submit_button("הבא ▶", use_container_width=True, type="primary"):
            _next({
                "is_kosher": 1 if kosher else 0,
                "carb_pref": "carbs" if "פחמימות" in pref else "fats",
                "spice_pref": "spicy" if "חריף" in spice else "mild",
                "disliked_foods": dis.strip(),
            })


def _reg_step4():
    st.subheader("שלב 4/4 — מטרה ומחויבות")
    d = st.session_state.reg
    GOAL_MAP = {"הגדלת מסה": "bulk", "ירידה במשקל": "cut", "שמירה על משקל": "maintain"}
    goal_opt = st.radio("מטרה", list(GOAL_MAP.keys()))
    goal = GOAL_MAP[goal_opt]

    gkg = None
    commit = None
    if goal != "maintain":
        verb = "לעלות" if goal == "bulk" else "לרדת"
        gkg = st.number_input("כמה ק\"ג תרצה " + verb + "?", 1.0, 60.0, float(d.get("goal_kg") or 10), 0.5, format="%.1f")
        ckeys = list(COMMITMENT.keys())
        commit = st.radio("רמת מחויבות", ckeys, index=1,
                          captions=["0.25 ק\"ג/שבוע", "0.5 ק\"ג/שבוע (מומלץ)", "0.8 ק\"ג/שבוע", "1 ק\"ג/שבוע"],
                          label_visibility="collapsed")

    if d.get("weight_kg") and d.get("height_cm"):
        tdee_v = _tdee(d["weight_kg"], d["height_cm"], d["age"], d["sex"], d["activity"])
        ci = COMMITMENT.get(commit, {}) if commit else {}
        delta = ci.get("delta", 0)
        bonus = ci.get("bulk_bonus", 0) if goal == "bulk" else 0
        if goal == "maintain":
            tgt = tdee_v
        elif goal == "cut":
            tgt = tdee_v - delta
        else:
            tgt = tdee_v + delta + bonus
        c1, c2, c3 = st.columns(3)
        c1.metric("TDEE", str(tdee_v) + " קל'")
        c2.metric("יעד יומי", str(tgt) + " קל'")
        if goal != "maintain" and commit:
            weeks = round((gkg or 10) / COMMITMENT[commit]["kg_week"])
            c3.metric("צפי", "~" + str(weeks) + " שבועות")
        if commit == "קיצוני ⚡" and goal == "bulk":
            st.warning("קיצוני: 2100 קל' עודף יומי — מאוד אינטנסיבי!")

    st.markdown("---")
    bc, fc = st.columns(2)
    if bc.button("◀ חזור", use_container_width=True):
        _back()
    if fc.button("צור פרופיל!", use_container_width=True, type="primary"):
        if not d.get("weight_kg") or not d.get("height_cm"):
            st.error("חזור ומלא נתונים פיזיים")
            return
        try:
            tdee_v = _tdee(d["weight_kg"], d["height_cm"], d["age"], d["sex"], d["activity"])
            ci = COMMITMENT.get(commit, {}) if commit else {}
            uid = "web_" + uuid.uuid4().hex[:8]
            db.get_or_create_user(uid)
            db.update_user(
                uid, name=d["name"], sex=d["sex"], age=int(d["age"]),
                height_cm=int(d["height_cm"]), weight_kg=float(d["weight_kg"]),
                activity=int(d["activity"]), is_kosher=int(d["is_kosher"]),
                carb_pref=d["carb_pref"], spice_pref=d["spice_pref"],
                disliked_foods=d.get("disliked_foods", ""), goal=goal,
                goal_kg=float(gkg) if gkg else None, commitment_label=commit,
                daily_delta=int(ci.get("delta", 0)), tdee=int(tdee_v), state="COMPLETED",
            )
            db.log_weight(uid, float(d["weight_kg"]))
            st.session_state.uid = uid
            st.session_state.registering = False
            st.session_state.step = 1
            st.session_state.reg = {}
            st.rerun()
        except Exception as e:
            st.error("שגיאה בשמירה: " + str(e))


def show_registration():
    st.markdown('<h1 style="color:#E50914">יצירת פרופיל תזונה</h1>', unsafe_allow_html=True)
    st.progress(st.session_state.step / 4)
    s = st.session_state.step
    if s == 1:
        _reg_step1()
    elif s == 2:
        _reg_step2()
    elif s == 3:
        _reg_step3()
    elif s == 4:
        _reg_step4()


# ─── Landing page ──────────────────────────────────────────────────────────────
def show_landing():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            '<h1 style="color:#E50914;font-size:3rem;text-align:center">🍽️ תזונה חכמה</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align:center;color:#aaa;font-size:1.1rem">'
            'תפריט תזונה אישי · BMR מדויק · מעקב קלוריות · כשרות · מתכונים מהאינטרנט'
            '</p>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        try:
            users = db.get_all_users()
        except Exception:
            users = []

        if users:
            st.subheader("כניסה לפרופיל קיים")
            names = {u["phone"]: u["name"] for u in users}
            sel = st.selectbox("בחר פרופיל", list(names.keys()), format_func=lambda k: names[k], label_visibility="collapsed")
            if st.button("כניסה לדשבורד", use_container_width=True, type="primary"):
                st.session_state.uid = sel
                st.rerun()
            st.markdown("---")

        if st.button("+ צור פרופיל חדש", use_container_width=True, type="primary" if not users else "secondary"):
            st.session_state.registering = True
            st.session_state.step = 1
            st.session_state.reg = {}
            st.rerun()


# ─── Community tab ─────────────────────────────────────────────────────────────
def show_community():
    st.markdown('<h2>קהילת המתכונים</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#aaa">כל המתכונים הזמינים — לחץ על מתכון לפרטים מלאים</p>', unsafe_allow_html=True)

    cat_map = {"breakfast": "ארוחת בוקר", "lunch": "ארוחת צהריים", "dinner": "ארוחת ערב"}
    filter_cat = st.selectbox(
        "סנן לפי קטגוריה",
        ["הכל", "ארוחת בוקר", "ארוחת צהריים", "ארוחת ערב"],
        label_visibility="collapsed",
    )
    cat_rev = {v: k for k, v in cat_map.items()}

    all_recipes = list(RECIPES.values())
    if filter_cat != "הכל":
        all_recipes = [r for r in all_recipes if r.get("category") == cat_rev.get(filter_cat)]

    # Display in 3-column grid
    for i in range(0, len(all_recipes), 3):
        cols = st.columns(3)
        for j, r in enumerate(all_recipes[i: i + 3]):
            with cols[j]:
                cat_lbl = cat_map.get(r.get("category", ""), "")
                card_html = f"""
                <div class="community-card">
                    <div style="color:#E50914;font-size:.8rem;font-weight:700;margin-bottom:4px">{cat_lbl}</div>
                    <div class="recipe-title">{r.get('name','---')}</div>
                    <div class="cal-badge">{r.get('cal',0)} קל'</div>
                    <div class="recipe-meta" style="margin-top:6px">
                        <span>💪 {r.get('pro',0)}g</span>
                        <span>🌾 {r.get('carb',0)}g</span>
                        <span>🥑 {r.get('fat',0)}g</span>
                    </div>
                    <div style="margin-top:6px">
                        <span class="badge badge-prep">{_type_label(r.get('type',''))}</span>
                        <span class="badge badge-prep">⏱ {r.get('prep','---')}</span>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                with st.expander("פרטים"):
                    ings = r.get("ingredients") or []
                    if ings:
                        chips = "".join(f'<span class="ing-chip">{x}</span>' for x in ings)
                        st.markdown(
                            f'<b style="color:#E50914">מרכיבים:</b><br>{chips}',
                            unsafe_allow_html=True,
                        )
                    steps = r.get("steps") or []
                    if steps:
                        st.markdown('<b style="color:#E50914">הכנה:</b>', unsafe_allow_html=True)
                        for s in steps:
                            st.markdown(
                                f'<div style="color:#ccc;padding:2px 0">{s}</div>',
                                unsafe_allow_html=True,
                            )


# ─── Dashboard ─────────────────────────────────────────────────────────────────
def show_dashboard(uid, u):
    st.session_state["_user_obj_"] = u
    target_cal = int(_target(u))

    # Sidebar
    with st.sidebar:
        st.markdown(
            f'<div style="font-size:1.3rem;font-weight:900;color:#E50914;margin-bottom:4px">'
            f'{u.get("name","")}</div>',
            unsafe_allow_html=True,
        )
        goal_map = {"bulk": "הגדלת מסה", "cut": "ירידה", "maintain": "שמירה"}
        st.write("**מטרה:** " + goal_map.get(u.get("goal", "maintain"), ""))
        st.write("**יעד:** " + str(target_cal) + " קל'/יום")
        st.write("**TDEE:** " + str(u.get("tdee", "---")) + " קל'")
        if u.get("commitment_label"):
            st.write("**מחויבות:** " + str(u["commitment_label"]))
        st.write("**כשרות:** " + ("כשר" if u.get("is_kosher", 1) else "לא כשר"))
        pref = u.get("carb_pref")
        if pref == "carbs":
            st.write("**העדפה:** פחמימות")
        elif pref == "fats":
            st.write("**העדפה:** שומנים")
        st.markdown("---")

        water = u.get("water_cups") or 0
        if u.get("water_date") != date.today().isoformat():
            water = 0
        st.markdown(
            f'<div style="color:#aaa;margin-bottom:4px">מים: {water}/8</div>'
            f'<div style="font-size:1.3rem">{"🔵"*min(water,8)}{"⚪"*max(8-water,0)}</div>',
            unsafe_allow_html=True,
        )
        if st.button("+ כוס מים", use_container_width=True, type="primary"):
            db.add_water_cup(uid)
            st.rerun()
        st.markdown("---")
        if st.button("החלף משתמש", use_container_width=True):
            st.session_state.uid = None
            st.rerun()
        if st.button("פרופיל חדש", use_container_width=True):
            st.session_state.uid = None
            st.session_state.registering = True
            st.session_state.step = 1
            st.session_state.reg = {}
            st.rerun()

    tabs = st.tabs(["🍽️ תפריט יומי", "🛒 רשימת קניות", "📈 התקדמות", "👤 פרופיל", "🌐 קהילה"])
    tab_day, tab_shop, tab_prog, tab_prof, tab_community = tabs

    # ── Tab 1 — Daily menu ─────────────────────────────────────────────────────
    with tab_day:
        st.markdown(
            f'<h2>שלום, <span style="color:#E50914">{u.get("name","")}</span>!</h2>',
            unsafe_allow_html=True,
        )
        consumed = db.get_daily_calories(uid)
        pct = min(consumed / target_cal, 1.0) if target_cal else 0.0

        c1, c2, c3 = st.columns(3)
        c1.metric("נאכל היום", str(consumed) + " קל'")
        c2.metric("יעד יומי", str(target_cal) + " קל'")
        c3.metric("נותר", str(max(target_cal - consumed, 0)) + " קל'")

        st.progress(pct)
        if pct >= 1.0:
            st.success("הגעת ליעד היומי!")
        if u.get("commitment_label") == "קיצוני ⚡" and u.get("goal") == "bulk":
            st.warning("מצב קיצוני פעיל — 2100 קל' עודף יומי")

        st.markdown("---")

        for cat, lbl in [("breakfast", "ארוחת בוקר"), ("lunch", "ארוחת צהריים"), ("dinner", "ארוחת ערב")]:
            st.markdown(f'<h3>{lbl}</h3>', unsafe_allow_html=True)

            web_r = _safe_web(cat)
            keys = _sorted_keys(cat, u)
            idx = st.session_state["swap_" + cat] % len(keys)
            current = web_r if web_r else RECIPES.get(keys[idx])

            if not current:
                st.info("טוען מתכון...")
                continue

            _render_recipe_card(
                current,
                key_prefix=cat + "_",
                show_buttons=True,
                uid=uid,
                cat=cat,
                idx=idx,
                keys=keys,
                web_r=web_r,
            )

        logs = db.get_today_logs(uid)
        if logs:
            st.markdown('<h3>רשומות היום</h3>', unsafe_allow_html=True)
            df = pd.DataFrame(logs)[["meal_name", "calories", "logged_at"]].copy()
            df.columns = ["ארוחה", "קלוריות", "שעה"]
            df["שעה"] = pd.to_datetime(df["שעה"]).dt.strftime("%H:%M")
            st.table(df)

    # ── Tab 2 — Shopping list ──────────────────────────────────────────────────
    with tab_shop:
        st.markdown('<h2>רשימת קניות שבועית</h2>', unsafe_allow_html=True)
        meals = {}
        for cat in ("breakfast", "lunch", "dinner"):
            wr = _safe_web(cat)
            if wr:
                meals[cat] = wr
            else:
                k = _sorted_keys(cat, u)
                meals[cat] = RECIPES.get(k[0], {})

        seen, rows = set(), []
        for cat, meal in meals.items():
            for ing in meal.get("ingredients") or []:
                key = str(ing).split()[0].lower() if ing else ""
                if key and key not in seen:
                    seen.add(key)
                    rows.append({"מרכיב": str(ing), "ארוחה": meal.get("name", "")})

        st.caption("x5 לשבוע שלם")
        if rows:
            st.table(pd.DataFrame(rows))
        if u.get("disliked_foods"):
            st.warning("מוסר מהתפריט: " + str(u["disliked_foods"]))

    # ── Tab 3 — Progress ───────────────────────────────────────────────────────
    with tab_prog:
        st.markdown('<h2>התקדמות</h2>', unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            wh = db.get_weight_history(uid, days=30)
            if wh:
                dfw = pd.DataFrame(wh)
                dfw["day"] = pd.to_datetime(dfw["day"])
                st.markdown('<h3>משקל — 30 יום</h3>', unsafe_allow_html=True)
                st.line_chart(dfw.set_index("day")["weight_kg"])
            else:
                st.info("הוסף משקל ראשון מהטופס מימין.")

            ch = db.get_calorie_history(uid, days=7)
            if ch:
                dfc = pd.DataFrame(ch)
                dfc["day"] = pd.to_datetime(dfc["day"])
                dfc["יעד"] = target_cal
                st.markdown('<h3>קלוריות — 7 ימים</h3>', unsafe_allow_html=True)
                st.line_chart(dfc.set_index("day").rename(columns={"total": "בפועל"})[["בפועל", "יעד"]])

        with c2:
            st.markdown('<h3>עדכון משקל</h3>', unsafe_allow_html=True)
            with st.form("wf"):
                nw = st.number_input("משקל (ק\"ג)", 30.0, 300.0, float(u.get("weight_kg") or 70), 0.5, "%.1f")
                if st.form_submit_button("שמור", use_container_width=True, type="primary"):
                    db.log_weight(uid, nw)
                    st.success(str(nw) + " ק\"ג נשמר!")
                    st.rerun()

            goal_u = u.get("goal", "maintain")
            goal_kg = u.get("goal_kg") or 0
            if goal_u != "maintain" and goal_kg:
                wh2 = db.get_weight_history(uid, days=365)
                if wh2:
                    if goal_u == "cut":
                        done = max(wh2[0]["weight_kg"] - wh2[-1]["weight_kg"], 0)
                    else:
                        done = max(wh2[-1]["weight_kg"] - wh2[0]["weight_kg"], 0)
                    pg = min(done / float(goal_kg), 1.0)
                    st.markdown('<h3>התקדמות למטרה</h3>', unsafe_allow_html=True)
                    st.metric("נעשה", str(round(done, 1)) + " ק\"ג")
                    st.metric("יעד", str(float(goal_kg)) + " ק\"ג")
                    st.progress(pg)
                    if pg >= 1.0:
                        st.balloons()
                        st.success("הגעת ליעד!")

    # ── Tab 4 — Profile ────────────────────────────────────────────────────────
    with tab_prof:
        st.markdown('<h2>הפרופיל שלך</h2>', unsafe_allow_html=True)
        goal_lbl = {"bulk": "הגדלת מסה", "cut": "ירידה", "maintain": "שמירה"}
        rows_p = [
            ["שם", str(u.get("name", "---"))],
            ["גיל", str(u.get("age", "---")) + " שנים"],
            ["גובה", str(u.get("height_cm", "---")) + " ס\"מ"],
            ["משקל", str(u.get("weight_kg", "---")) + " ק\"ג"],
            ["TDEE", str(u.get("tdee", "---")) + " קל'"],
            ["יעד יומי", str(target_cal) + " קל'"],
            ["מטרה", goal_lbl.get(u.get("goal", "maintain"), "---")],
            ["מחויבות", str(u.get("commitment_label") or "---")],
            ["כשרות", "כשר" if u.get("is_kosher", 1) else "לא כשר"],
            ["העדפה", "פחמימות" if u.get("carb_pref") == "carbs" else "שומנים"],
            ["טעם", "חריף" if u.get("spice_pref") == "spicy" else "עדין"],
            ["מוסרים", str(u.get("disliked_foods") or "---")],
        ]
        st.table(pd.DataFrame(rows_p, columns=["שדה", "ערך"]))

        st.markdown('<h3>עדכון פרופיל</h3>', unsafe_allow_html=True)
        with st.form("ef"):
            nw2 = st.number_input("משקל נוכחי (ק\"ג)", 30.0, 300.0, float(u.get("weight_kg") or 70), 0.5, "%.1f")
            nd = st.text_input("מאכלים אסורים", value=str(u.get("disliked_foods") or ""))
            nk = st.toggle("כשרות", value=bool(u.get("is_kosher", 1)))
            nc = st.radio("העדפת מזון", ["פחמימות", "שומנים"], index=0 if u.get("carb_pref") == "carbs" else 1)
            if st.form_submit_button("שמור שינויים", use_container_width=True, type="primary"):
                new_tdee = _tdee(nw2, u["height_cm"], u["age"], u["sex"], u["activity"])
                db.update_user(uid, weight_kg=nw2, disliked_foods=nd.strip(),
                               is_kosher=1 if nk else 0,
                               carb_pref="carbs" if nc == "פחמימות" else "fats",
                               tdee=int(new_tdee))
                db.log_weight(uid, nw2)
                st.success("הפרופיל עודכן!")
                st.rerun()

    # ── Tab 5 — Community ──────────────────────────────────────────────────────
    with tab_community:
        show_community()


# ─── Main router ───────────────────────────────────────────────────────────────
def _main():
    uid = st.session_state.uid
    if uid:
        u = db.get_user(uid)
        if u and u.get("state") == "COMPLETED":
            show_dashboard(uid, u)
        else:
            st.session_state.uid = None
            st.rerun()
    elif st.session_state.registering:
        show_registration()
    else:
        show_landing()


try:
    _main()
except Exception as e:
    st.error("שגיאה: " + str(e))
    if st.button("רענן דף"):
        st.rerun()
