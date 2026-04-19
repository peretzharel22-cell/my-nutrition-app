# -*- coding: utf-8 -*-
"""app_web.py - Streamlit nutrition dashboard — Organic Modern Theme"""
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

st.set_page_config(page_title="תזונה חכמה", layout="wide", page_icon="🍽️")

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;900&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #F4F1EA !important;
    color: #355E3B !important;
    font-family: 'Heebo', sans-serif !important;
    direction: rtl;
    text-align: right;
}
[data-testid="block-container"] { background-color: #F4F1EA !important; }
section[data-testid="stMain"] { background-color: #F4F1EA !important; }

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-left: 3px solid #3EB489;
}
[data-testid="stSidebar"] * { color: #355E3B !important; }
[data-testid="stSidebar"] button {
    background: #3EB489 !important;
    border: none !important;
    color: #fff !important;
    border-radius: 8px !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 700 !important;
    transition: background .2s, transform .15s !important;
}
[data-testid="stSidebar"] button:hover {
    background: #2e9a72 !important;
    transform: scale(1.03) !important;
}

h1, h2, h3, h4 {
    font-family: 'Heebo', sans-serif !important;
    color: #355E3B !important;
    font-weight: 900 !important;
}
h1 { font-size: 2.4rem !important; }
h2 { font-size: 1.8rem !important; }
h3 { font-size: 1.35rem !important; }

.stProgress > div > div { background: #3EB489 !important; border-radius: 4px; }
.stProgress > div { background: #E8E2D9 !important; border-radius: 4px; }

button[kind="primary"] {
    background: #3EB489 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    transition: background .2s, transform .15s !important;
}
button[kind="primary"]:hover {
    background: #2e9a72 !important;
    transform: scale(1.03) !important;
}
button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #355E3B !important;
    border: 1.5px solid #3EB489 !important;
    border-radius: 8px !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
    transition: all .2s !important;
}
button[kind="secondary"]:hover {
    background: #3EB489 !important;
    color: #fff !important;
    transform: scale(1.03) !important;
}

[data-testid="stTabs"] button {
    background: transparent !important;
    color: #7a9b7d !important;
    border-bottom: 2px solid transparent !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 8px 16px !important;
    transition: color .2s !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #3EB489 !important;
    border-bottom: 2px solid #3EB489 !important;
}
[data-testid="stTabs"] button:hover { color: #355E3B !important; }

input, textarea, [data-baseweb="input"] input, [data-baseweb="select"] div {
    background: #FFFFFF !important;
    color: #355E3B !important;
    border: 1.5px solid #D5CFC4 !important;
    border-radius: 8px !important;
    font-family: 'Heebo', sans-serif !important;
}
input:focus, textarea:focus { border-color: #3EB489 !important; outline: none !important; }
label { color: #5a7a5e !important; font-family: 'Heebo', sans-serif !important; }

[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1.5px solid #E8E2D9 !important;
    border-radius: 12px !important;
    padding: 14px !important;
    box-shadow: 0 2px 8px rgba(53,94,59,.08) !important;
}
[data-testid="stMetricValue"] { color: #3EB489 !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #7a9b7d !important; }

hr { border-color: #E8E2D9 !important; }

[data-testid="stAlert"] {
    background: #FFFFFF !important;
    border-left: 4px solid #F88379 !important;
    border-radius: 8px !important;
    color: #355E3B !important;
}
.stSuccess { border-left-color: #3EB489 !important; }
.stInfo { border-left-color: #3EB489 !important; }
.stWarning { border-left-color: #F88379 !important; }

table { background: #FFFFFF !important; color: #355E3B !important; width: 100% !important; border-radius: 8px !important; overflow: hidden !important; }
th { background: #3EB489 !important; color: #fff !important; padding: 10px 14px !important; font-family: 'Heebo', sans-serif !important; font-weight: 700 !important; }
td { padding: 9px 14px !important; border-bottom: 1px solid #F4F1EA !important; }

[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1.5px solid #E8E2D9 !important;
    border-radius: 10px !important;
    margin-bottom: 4px !important;
}
[data-testid="stExpander"] summary {
    color: #355E3B !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
}

.rc {
    background: #FFFFFF;
    border: 1.5px solid #E8E2D9;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: transform .22s, box-shadow .22s, border-color .22s;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(53,94,59,.07);
}
.rc:hover {
    transform: scale(1.025);
    box-shadow: 0 8px 28px rgba(62,180,137,.22);
    border-color: #3EB489;
}
.rc-bar {
    position: absolute;
    top: 0; right: 0;
    width: 5px;
    height: 100%;
    background: #3EB489;
    border-radius: 0 12px 12px 0;
}
.rc-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #355E3B;
    margin-bottom: 6px;
    font-family: 'Heebo', sans-serif;
}
.rc-meta {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    font-size: .88rem;
    color: #7a9b7d;
    margin-bottom: 8px;
}
.pill {
    display: inline-block;
    font-size: .78rem;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 20px;
    margin: 2px 1px;
}
.pill-green { background: #3EB489; color: #fff; }
.pill-coral { background: #F88379; color: #fff; }
.pill-grey  { background: #F4F1EA; border: 1px solid #D5CFC4; color: #5a7a5e; }
.chip {
    display: inline-block;
    background: #F4F1EA;
    border: 1px solid #D5CFC4;
    color: #5a7a5e;
    font-size: .8rem;
    padding: 2px 10px;
    border-radius: 20px;
    margin: 2px;
    font-family: 'Heebo', sans-serif;
}
.cc {
    background: #FFFFFF;
    border: 1.5px solid #E8E2D9;
    border-radius: 12px;
    padding: 16px;
    transition: transform .22s, border-color .22s, box-shadow .22s;
    box-shadow: 0 2px 8px rgba(53,94,59,.06);
}
.cc:hover {
    transform: scale(1.03);
    border-color: #3EB489;
    box-shadow: 0 6px 22px rgba(62,180,137,.2);
}
.cc-cat { color: #3EB489; font-size: .8rem; font-weight: 700; margin-bottom: 4px; }
.cc-title { font-size: 1rem; font-weight: 800; color: #355E3B; margin-bottom: 4px; }
.cc-cal { font-size: 1.3rem; font-weight: 900; color: #F88379; }
"""

st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)

db.init_db()

for _k, _v in [("uid", None), ("step", 1), ("reg", {}), ("registering", False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

for _cat in ("breakfast", "lunch", "dinner"):
    if ("swap_" + _cat) not in st.session_state:
        st.session_state["swap_" + _cat] = 0
    if ("web_" + _cat) not in st.session_state:
        st.session_state["web_" + _cat] = None


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


def _recipe_card(r):
    src_pill = '<span class="pill pill-coral">רשת</span>' if r.get("source") in ("web", "fallback") else ""
    type_pill = f'<span class="pill pill-grey">{_type_label(r.get("type",""))}</span>'
    prep_pill = f'<span class="pill pill-grey">&#x23F1; {r.get("prep","---")}</span>'
    html = (
        '<div class="rc">'
        '<div class="rc-bar"></div>'
        f'<div class="rc-title">{src_pill}{r.get("name","---")}</div>'
        '<div class="rc-meta">'
        f'<span>&#x1F525; <b style="color:#F88379">{r.get("cal",0)}</b> קל\'</span>'
        f'<span>&#x1F4AA; {r.get("pro",0)}g חלבון</span>'
        f'<span>&#x1F33E; {r.get("carb",0)}g פחמימות</span>'
        f'<span>&#x1F951; {r.get("fat",0)}g שומן</span>'
        '</div>'
        f'<div>{type_pill}{prep_pill}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _meal_section(uid, cat, lbl, u):
    st.markdown(f"<h3>{lbl}</h3>", unsafe_allow_html=True)
    web_r = _safe_web(cat)
    keys = _sorted_keys(cat, u)
    idx = st.session_state["swap_" + cat] % len(keys)
    current = web_r if web_r else RECIPES.get(keys[idx])
    if not current:
        st.info("טוען מתכון...")
        return

    _recipe_card(current)

    with st.expander("פרטים מלאים — מרכיבים ושלבי הכנה"):
        ings = current.get("ingredients") or []
        if ings:
            chips = "".join(f'<span class="chip">{i}</span>' for i in ings)
            st.markdown(
                f'<div style="margin-bottom:10px"><b style="color:#3EB489">מרכיבים:</b><br>{chips}</div>',
                unsafe_allow_html=True,
            )
        for step in (current.get("steps") or []):
            st.markdown(
                f'<div style="padding:4px 0;border-bottom:1px solid #F4F1EA;color:#5a7a5e">{step}</div>',
                unsafe_allow_html=True,
            )

    b1, b2, b3, b4 = st.columns(4)
    if b1.button("✔ אכלתי", key="ate_" + cat, use_container_width=True, type="primary"):
        cal = int(current.get("cal", 0))
        db.add_daily_calories(uid, cal)
        db.log_meal(uid, keys[idx] if not web_r else "web",
                    str(current.get("name", "")), str(current.get("type", "pareve")), cat, cal)
        if current.get("type") == "meat":
            db.update_user(uid, last_meat_ts=datetime.utcnow().isoformat())
        st.toast(str(current.get("name", "")) + " — " + str(cal) + " קל'")
        st.rerun()
    if b2.button("החלף", key="swap_" + cat, use_container_width=True):
        st.session_state["web_" + cat] = None
        st.session_state["swap_" + cat] = (idx + 1) % len(keys)
        st.rerun()
    if b3.button("מהרשת", key="web_" + cat, use_container_width=True):
        off = st.session_state.get("web_off_" + cat, 0)
        with st.spinner("מחפש..."):
            wr = fetch_web_recipe(cat, u, off)
        if wr and isinstance(wr, dict):
            st.session_state["web_" + cat] = wr
            st.session_state["web_off_" + cat] = off + 1
        else:
            st.warning("לא נמצא מתכון.")
        st.rerun()
    if web_r and b4.button("מקומי", key="local_" + cat, use_container_width=True):
        st.session_state["web_" + cat] = None
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)


def _reg_step1():
    st.subheader("שלב 1/4 — פרטים אישיים")
    with st.form("s1"):
        name = st.text_input("שם מלא", placeholder="הזן שם...")
        sex = st.radio("מין ביולוגי", ["זכר", "נקבה"], horizontal=True)
        if st.form_submit_button("הבא", use_container_width=True, type="primary"):
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
        height = c2.number_input('גובה (ס"מ)', 140, 220, int(d.get("height_cm", 170)), step=1)
        weight = c1.number_input('משקל (ק"ג)', 35.0, 200.0, float(d.get("weight_kg", 70)), step=0.5, format="%.1f")
        act = c2.selectbox("פעילות גופנית", [1, 2, 3, 4, 5],
                           index=int(d.get("activity", 2)) - 1,
                           format_func=lambda x: {1:"1 — יושבני",2:"2 — קל",3:"3 — מתון",4:"4 — פעיל",5:"5 — אינטנסיבי"}[x])
        bc, nc = st.columns(2)
        if bc.form_submit_button("חזור", use_container_width=True):
            _back()
        if nc.form_submit_button("הבא", use_container_width=True, type="primary"):
            _next({"age": int(age), "height_cm": int(height), "weight_kg": float(weight), "activity": int(act)})


def _reg_step3():
    st.subheader("שלב 3/4 — כשרות וטעם")
    d = st.session_state.reg
    with st.form("s3"):
        kosher = st.toggle("שמירת כשרות (הפרדת בשר/חלב 6 שעות)", value=bool(d.get("is_kosher", 1)))
        st.markdown("<hr>", unsafe_allow_html=True)
        pref = st.radio("העדפת מזון",
                        ["פחמימות (פסטה, אורז, לחם)", "שומנים בריאים (אבוקדו, דגים, אגוזים)"],
                        index=0 if d.get("carb_pref", "carbs") == "carbs" else 1)
        spice = st.radio("טעם מועדף", ["חריף", "עדין"],
                         index=0 if d.get("spice_pref") == "spicy" else 1, horizontal=True)
        dis = st.text_input("מאכלים שאינך אוהב", value=d.get("disliked_foods", ""), placeholder="עגבנייה, גבינה...")
        bc, nc = st.columns(2)
        if bc.form_submit_button("חזור", use_container_width=True):
            _back()
        if nc.form_submit_button("הבא", use_container_width=True, type="primary"):
            _next({"is_kosher": 1 if kosher else 0,
                   "carb_pref": "carbs" if "פחמימות" in pref else "fats",
                   "spice_pref": "spicy" if "חריף" in spice else "mild",
                   "disliked_foods": dis.strip()})


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
        gkg = st.number_input('כמה ק"ג תרצה ' + verb + "?", 1.0, 60.0,
                              float(d.get("goal_kg") or 10), 0.5, format="%.1f")
        ckeys = list(COMMITMENT.keys())
        commit = st.radio("רמת מחויבות", ckeys, index=1,
                          captions=['0.25 ק"ג/שבוע', '0.5 ק"ג/שבוע (מומלץ)', '0.8 ק"ג/שבוע', '1 ק"ג/שבוע'],
                          label_visibility="collapsed")
    if d.get("weight_kg") and d.get("height_cm"):
        tdee_v = _tdee(d["weight_kg"], d["height_cm"], d["age"], d["sex"], d["activity"])
        ci = COMMITMENT.get(commit, {}) if commit else {}
        delta = ci.get("delta", 0)
        bonus = ci.get("bulk_bonus", 0) if goal == "bulk" else 0
        tgt = tdee_v if goal == "maintain" else (tdee_v - delta if goal == "cut" else tdee_v + delta + bonus)
        c1, c2, c3 = st.columns(3)
        c1.metric("TDEE", str(tdee_v) + " קל'")
        c2.metric("יעד יומי", str(tgt) + " קל'")
        if goal != "maintain" and commit:
            weeks = round((gkg or 10) / COMMITMENT[commit]["kg_week"])
            c3.metric("צפי", "~" + str(weeks) + " שבועות")
        if commit == "קיצוני ⚡" and goal == "bulk":
            st.warning("קיצוני: 2100 קל' עודף יומי — מאוד אינטנסיבי!")
    st.markdown("<hr>", unsafe_allow_html=True)
    bc, fc = st.columns(2)
    if bc.button("חזור", use_container_width=True):
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
            db.update_user(uid, name=d["name"], sex=d["sex"], age=int(d["age"]),
                           height_cm=int(d["height_cm"]), weight_kg=float(d["weight_kg"]),
                           activity=int(d["activity"]), is_kosher=int(d["is_kosher"]),
                           carb_pref=d["carb_pref"], spice_pref=d["spice_pref"],
                           disliked_foods=d.get("disliked_foods", ""), goal=goal,
                           goal_kg=float(gkg) if gkg else None, commitment_label=commit,
                           daily_delta=int(ci.get("delta", 0)), tdee=int(tdee_v), state="COMPLETED")
            db.log_weight(uid, float(d["weight_kg"]))
            st.session_state.uid = uid
            st.session_state.registering = False
            st.session_state.step = 1
            st.session_state.reg = {}
            st.rerun()
        except Exception as e:
            st.error("שגיאה בשמירה: " + str(e))


def show_registration():
    st.markdown('<h1 style="color:#3EB489">יצירת פרופיל תזונה</h1>', unsafe_allow_html=True)
    st.progress(st.session_state.step / 4)
    s = st.session_state.step
    if s == 1:   _reg_step1()
    elif s == 2: _reg_step2()
    elif s == 3: _reg_step3()
    elif s == 4: _reg_step4()


def show_landing():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            '<h1 style="color:#3EB489;text-align:center">🍽️ תזונה חכמה</h1>'
            '<p style="text-align:center;color:#7a9b7d;font-size:1.05rem">'
            'תפריט אישי · BMR מדויק · מעקב קלוריות · כשרות · מתכונים מהרשת'
            '</p>',
            unsafe_allow_html=True,
        )
        st.markdown("<hr>", unsafe_allow_html=True)
        try:
            users = db.get_all_users()
        except Exception:
            users = []
        if users:
            st.subheader("כניסה לפרופיל קיים")
            names = {u["phone"]: u["name"] for u in users}
            sel = st.selectbox("בחר פרופיל", list(names.keys()),
                               format_func=lambda k: names[k], label_visibility="collapsed")
            if st.button("כניסה לדשבורד", use_container_width=True, type="primary"):
                st.session_state.uid = sel
                st.rerun()
            st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("+ צור פרופיל חדש", use_container_width=True,
                     type="primary" if not users else "secondary"):
            st.session_state.registering = True
            st.session_state.step = 1
            st.session_state.reg = {}
            st.rerun()


def show_community():
    st.markdown('<h2>קהילת המתכונים</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7a9b7d">כל המתכונים הזמינים — לחץ על כרטיס לפרטים מלאים</p>',
                unsafe_allow_html=True)
    cat_map = {"breakfast": "ארוחת בוקר", "lunch": "ארוחת צהריים", "dinner": "ארוחת ערב"}
    filter_cat = st.selectbox("סנן", ["הכל", "ארוחת בוקר", "ארוחת צהריים", "ארוחת ערב"],
                              label_visibility="collapsed")
    cat_rev = {v: k for k, v in cat_map.items()}
    all_r = list(RECIPES.values())
    if filter_cat != "הכל":
        all_r = [r for r in all_r if r.get("category") == cat_rev.get(filter_cat)]
    for i in range(0, len(all_r), 3):
        cols = st.columns(3)
        for j, r in enumerate(all_r[i: i + 3]):
            with cols[j]:
                cat_lbl = cat_map.get(r.get("category", ""), "")
                type_pill = f'<span class="pill pill-grey">{_type_label(r.get("type",""))}</span>'
                prep_pill = f'<span class="pill pill-grey">&#x23F1; {r.get("prep","---")}</span>'
                st.markdown(
                    f'<div class="cc">'
                    f'<div class="cc-cat">{cat_lbl}</div>'
                    f'<div class="cc-title">{r.get("name","---")}</div>'
                    f'<div class="cc-cal">{r.get("cal",0)} קל\'</div>'
                    f'<div class="rc-meta" style="margin-top:5px">'
                    f'<span>&#x1F4AA; {r.get("pro",0)}g</span>'
                    f'<span>&#x1F33E; {r.get("carb",0)}g</span>'
                    f'<span>&#x1F951; {r.get("fat",0)}g</span>'
                    f'</div>'
                    f'<div style="margin-top:6px">{type_pill}{prep_pill}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                with st.expander("פרטים"):
                    ings = r.get("ingredients") or []
                    if ings:
                        chips = "".join(f'<span class="chip">{x}</span>' for x in ings)
                        st.markdown(
                            f'<b style="color:#3EB489">מרכיבים:</b><br>{chips}',
                            unsafe_allow_html=True,
                        )
                    for step in (r.get("steps") or []):
                        st.markdown(
                            f'<div style="padding:2px 0;color:#5a7a5e;border-bottom:1px solid #F4F1EA">{step}</div>',
                            unsafe_allow_html=True,
                        )


def show_dashboard(uid, u):
    target_cal = int(_target(u))

    with st.sidebar:
        st.markdown(
            f'<div style="font-size:1.25rem;font-weight:900;color:#3EB489;margin-bottom:4px">{u.get("name","")}</div>',
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
        st.write("**העדפה:** " + ("פחמימות" if pref == "carbs" else "שומנים"))
        st.markdown("<hr>", unsafe_allow_html=True)
        water = u.get("water_cups") or 0
        if u.get("water_date") != date.today().isoformat():
            water = 0
        st.markdown(
            f'<div style="color:#7a9b7d;margin-bottom:4px">מים: {water}/8</div>'
            f'<div style="font-size:1.25rem">{"🔵"*min(water,8)}{"⚪"*max(8-water,0)}</div>',
            unsafe_allow_html=True,
        )
        if st.button("+ כוס מים", use_container_width=True, type="primary"):
            db.add_water_cup(uid)
            st.rerun()
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("החלף משתמש", use_container_width=True):
            st.session_state.uid = None
            st.rerun()
        if st.button("פרופיל חדש", use_container_width=True):
            st.session_state.uid = None
            st.session_state.registering = True
            st.session_state.step = 1
            st.session_state.reg = {}
            st.rerun()

    tabs = st.tabs(["🍽️ תפריט יומי", "🛒 קניות", "📈 התקדמות", "👤 פרופיל", "🌿 קהילה"])
    tab_day, tab_shop, tab_prog, tab_prof, tab_community = tabs

    with tab_day:
        st.markdown(
            f'<h2>שלום, <span style="color:#3EB489">{u.get("name","")}</span>!</h2>',
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
        st.markdown("<hr>", unsafe_allow_html=True)
        for cat, lbl in [("breakfast","ארוחת בוקר"),("lunch","ארוחת צהריים"),("dinner","ארוחת ערב")]:
            _meal_section(uid, cat, lbl, u)
        logs = db.get_today_logs(uid)
        if logs:
            st.markdown('<h3>רשומות היום</h3>', unsafe_allow_html=True)
            df = pd.DataFrame(logs)[["meal_name","calories","logged_at"]].copy()
            df.columns = ["ארוחה","קלוריות","שעה"]
            df["שעה"] = pd.to_datetime(df["שעה"]).dt.strftime("%H:%M")
            st.table(df)

    with tab_shop:
        st.markdown('<h2>רשימת קניות שבועית</h2>', unsafe_allow_html=True)
        meals = {}
        for cat in ("breakfast","lunch","dinner"):
            wr = _safe_web(cat)
            meals[cat] = wr if wr else RECIPES.get(_sorted_keys(cat, u)[0], {})
        seen, rows = set(), []
        for cat, meal in meals.items():
            for ing in (meal.get("ingredients") or []):
                key = str(ing).split()[0].lower() if ing else ""
                if key and key not in seen:
                    seen.add(key)
                    rows.append({"מרכיב": str(ing), "ארוחה": meal.get("name","")})
        st.caption("x5 לשבוע שלם")
        if rows:
            st.table(pd.DataFrame(rows))
        if u.get("disliked_foods"):
            st.warning("מוסר מהתפריט: " + str(u["disliked_foods"]))

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
                st.info("הוסף משקל ראשון מהטופס.")
            ch = db.get_calorie_history(uid, days=7)
            if ch:
                dfc = pd.DataFrame(ch)
                dfc["day"] = pd.to_datetime(dfc["day"])
                dfc["יעד"] = target_cal
                st.markdown('<h3>קלוריות — 7 ימים</h3>', unsafe_allow_html=True)
                st.line_chart(dfc.set_index("day").rename(columns={"total":"בפועל"})[["בפועל","יעד"]])
        with c2:
            st.markdown('<h3>עדכון משקל</h3>', unsafe_allow_html=True)
            with st.form("wf"):
                nw = st.number_input('משקל (ק"ג)', 30.0, 300.0, float(u.get("weight_kg") or 70), 0.5, "%.1f")
                if st.form_submit_button("שמור", use_container_width=True, type="primary"):
                    db.log_weight(uid, nw)
                    st.success(str(nw) + ' ק"ג נשמר!')
                    st.rerun()
            goal_u = u.get("goal","maintain")
            goal_kg = u.get("goal_kg") or 0
            if goal_u != "maintain" and goal_kg:
                wh2 = db.get_weight_history(uid, days=365)
                if wh2:
                    done = max((wh2[0]["weight_kg"]-wh2[-1]["weight_kg"] if goal_u=="cut"
                                else wh2[-1]["weight_kg"]-wh2[0]["weight_kg"]), 0)
                    pg = min(done / float(goal_kg), 1.0)
                    st.markdown('<h3>התקדמות למטרה</h3>', unsafe_allow_html=True)
                    st.metric("נעשה", str(round(done,1)) + ' ק"ג')
                    st.metric("יעד", str(float(goal_kg)) + ' ק"ג')
                    st.progress(pg)
                    if pg >= 1.0:
                        st.balloons()
                        st.success("הגעת ליעד!")

    with tab_prof:
        st.markdown('<h2>הפרופיל שלך</h2>', unsafe_allow_html=True)
        goal_lbl = {"bulk":"הגדלת מסה","cut":"ירידה","maintain":"שמירה"}
        rows_p = [
            ["שם",       str(u.get("name","---"))],
            ["גיל",      str(u.get("age","---")) + " שנים"],
            ["גובה",     str(u.get("height_cm","---")) + ' ס"מ'],
            ["משקל",     str(u.get("weight_kg","---")) + ' ק"ג'],
            ["TDEE",     str(u.get("tdee","---")) + " קל'"],
            ["יעד יומי", str(target_cal) + " קל'"],
            ["מטרה",     goal_lbl.get(u.get("goal","maintain"),"---")],
            ["מחויבות",  str(u.get("commitment_label") or "---")],
            ["כשרות",    "כשר" if u.get("is_kosher",1) else "לא כשר"],
            ["העדפה",    "פחמימות" if u.get("carb_pref")=="carbs" else "שומנים"],
            ["טעם",      "חריף" if u.get("spice_pref")=="spicy" else "עדין"],
            ["מוסרים",   str(u.get("disliked_foods") or "---")],
        ]
        st.table(pd.DataFrame(rows_p, columns=["שדה","ערך"]))
        st.markdown('<h3>עדכון פרופיל</h3>', unsafe_allow_html=True)
        with st.form("ef"):
            nw2 = st.number_input('משקל נוכחי (ק"ג)', 30.0, 300.0,
                                   float(u.get("weight_kg") or 70), 0.5, "%.1f")
            nd = st.text_input("מאכלים אסורים", value=str(u.get("disliked_foods") or ""))
            nk = st.toggle("כשרות", value=bool(u.get("is_kosher", 1)))
            nc = st.radio("העדפת מזון", ["פחמימות","שומנים"],
                          index=0 if u.get("carb_pref")=="carbs" else 1)
            if st.form_submit_button("שמור שינויים", use_container_width=True, type="primary"):
                new_tdee = _tdee(nw2, u["height_cm"], u["age"], u["sex"], u["activity"])
                db.update_user(uid, weight_kg=nw2, disliked_foods=nd.strip(),
                               is_kosher=1 if nk else 0,
                               carb_pref="carbs" if nc=="פחמימות" else "fats",
                               tdee=int(new_tdee))
                db.log_weight(uid, nw2)
                st.success("הפרופיל עודכן!")
                st.rerun()

    with tab_community:
        show_community()


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
