# -*- coding: utf-8 -*-
"""app.py - Social Nutrition Network — Professional Premium (main entry point)"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime

import db
import handler
from handler import (
    RECIPES, COMMITMENT, _sorted_keys, _target, _tdee,
    fetch_web_recipe, estimate_nutrition,
)

st.set_page_config(page_title="תזונה חכמה", page_icon="🥗", layout="wide")


def inject_css() -> None:
    css = """
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
section[data-testid="stMain"],
[data-testid="block-container"] {
    background-color: #F8F9FA !important;
    color: #212529 !important;
    font-family: 'Heebo', sans-serif !important;
    line-height: 1.6 !important;
    direction: rtl;
    text-align: right;
}

.main .block-container {
    direction: rtl !important;
    text-align: right !important;
    padding-top: 1.5rem;
    max-width: 1080px;
}

[data-testid="stMarkdownContainer"],
[data-testid="stText"],
label, p, span {
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Heebo', sans-serif !important;
    line-height: 1.6 !important;
    color: #212529 !important;
}

h1, h2, h3, h4, h5 {
    font-family: 'Heebo', sans-serif !important;
    font-weight: 700 !important;
    color: #212529 !important;
    line-height: 1.3 !important;
    direction: rtl !important;
    text-align: right !important;
}

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-left: 1px solid #DEE2E6 !important;
}
[data-testid="stSidebar"] * {
    color: #212529 !important;
    font-family: 'Heebo', sans-serif !important;
}
[data-testid="stSidebar"] button {
    background: #1B4332 !important;
    border: none !important;
    border-radius: 8px !important;
    margin-bottom: 5px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: #fff !important;
    width: 100% !important;
    transition: opacity 0.18s ease !important;
}
[data-testid="stSidebar"] button:hover { opacity: 0.80 !important; }

.stProgress > div > div { background: #1B4332 !important; border-radius: 4px !important; }
.stProgress > div        { background: #DEE2E6 !important; border-radius: 4px !important; }

div[data-testid="stForm"] {
    background: #FFFFFF !important;
    border: 1px solid #DEE2E6 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}

input, textarea, select,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    direction: rtl !important;
    text-align: right !important;
    background: #FFFFFF !important;
    color: #212529 !important;
    border: 1px solid #DEE2E6 !important;
    border-radius: 8px !important;
    font-family: 'Heebo', sans-serif !important;
    line-height: 1.6 !important;
    transition: border-color 0.15s ease !important;
}
input:focus, textarea:focus {
    border-color: #1B4332 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(27,67,50,0.10) !important;
}

.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button {
    background: #1B4332 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: 'Heebo', sans-serif !important;
    color: #fff !important;
    letter-spacing: 0.3px !important;
    transition: opacity 0.18s ease !important;
}
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    opacity: 0.82 !important;
    box-shadow: 0 4px 14px rgba(27,67,50,0.20) !important;
}

.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1.5px solid #DEE2E6 !important;
    border-radius: 8px !important;
    color: #212529 !important;
    font-weight: 600 !important;
    font-family: 'Heebo', sans-serif !important;
    transition: opacity 0.18s ease !important;
}
.stButton > button[kind="secondary"]:hover { opacity: 0.70 !important; }

.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid #DEE2E6;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 18px !important;
    font-weight: 600 !important;
    font-family: 'Heebo', sans-serif !important;
    color: #6c757d !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #1B4332 !important;
    border-bottom: 2px solid #1B4332 !important;
    background: transparent !important;
}

.feed-card {
    background: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 14px;
    overflow: hidden;
    word-wrap: break-word;
    direction: rtl;
    text-align: right;
}

.recipe-card {
    background: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    overflow: hidden;
    word-wrap: break-word;
    direction: rtl;
    text-align: right;
    transition: box-shadow 0.2s ease;
}
.recipe-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.10); }
.recipe-card b { font-weight: 700; }

.community-card {
    background: #FFFFFF;
    border: 1px solid #DEE2E6;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 8px 0;
    overflow: hidden;
    word-wrap: break-word;
    direction: rtl;
    text-align: right;
    transition: box-shadow 0.18s ease;
}
.community-card:hover { box-shadow: 0 4px 12px rgba(27,67,50,0.10); }

.badge {
    display: inline-block;
    background: #1B4332;
    color: #fff !important;
    border-radius: 20px;
    padding: 1px 10px;
    font-size: 0.72rem;
    font-weight: 700;
    margin-right: 4px;
    vertical-align: middle;
    white-space: nowrap;
}
.badge-comm { background: #D90429 !important; }
.badge-gold { background: #F9A825 !important; }
.stars { color: #F9A825; font-size: 1rem; letter-spacing: 1px; }

[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #DEE2E6 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
    color: #212529 !important;
    padding: 10px 14px !important;
}

[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #DEE2E6 !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
    box-shadow: none !important;
}
[data-testid="stMetricValue"] {
    color: #1B4332 !important;
    font-weight: 700 !important;
    font-family: 'Heebo', sans-serif !important;
}
[data-testid="stMetricLabel"] {
    color: #6c757d !important;
    font-family: 'Heebo', sans-serif !important;
}

table {
    background: #FFFFFF !important;
    color: #212529 !important;
    width: 100% !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    border-collapse: collapse !important;
}
th {
    background: #F8F9FA !important;
    color: #212529 !important;
    padding: 10px 16px !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
    border-bottom: 2px solid #DEE2E6 !important;
}
td {
    padding: 9px 16px !important;
    border-bottom: 1px solid #F8F9FA !important;
    vertical-align: top !important;
}

hr {
    border: none !important;
    border-top: 1px solid #DEE2E6 !important;
    margin: 14px 0 !important;
}

[data-testid="stAlert"] {
    background: #FFFFFF !important;
    border-radius: 10px !important;
    border: none !important;
    border-right: 3px solid #1B4332 !important;
    color: #212529 !important;
    padding: 12px 16px !important;
}

[data-testid="stCaptionContainer"],
.stCaption { color: #6c757d !important; font-size: 0.83rem !important; }

.auth-container {
    max-width: 420px;
    margin: 0 auto;
    padding: 2rem 0;
}

.auth-logo {
    text-align: center;
    padding: 1.5rem 0 1rem;
}

.auth-logo h1 {
    font-size: 2rem !important;
    color: #1B4332 !important;
    margin-bottom: 4px;
}

.auth-logo p {
    color: #6c757d !important;
    font-size: 1rem !important;
}
"""
    st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)


inject_css()

db.init_db()

_DEFAULTS = [
    ("uid",      None),
    ("username", None),
    ("page",     "auth"),
    ("step",     1),
    ("reg",      {}),
]
for _k, _v in _DEFAULTS:
    if _k not in st.session_state:
        st.session_state[_k] = _v

for _cat in ("breakfast", "lunch", "dinner"):
    for _pre, _def in (("swap_", 0), ("web_", None), ("web_off_", 0)):
        _key = f"{_pre}{_cat}"
        if _key not in st.session_state:
            st.session_state[_key] = _def


def _stars(likes: int) -> str:
    if likes >= 50:   n = 5
    elif likes >= 20: n = 4
    elif likes >= 10: n = 3
    elif likes >= 3:  n = 2
    elif likes >= 1:  n = 1
    else:             n = 0
    return "★" * n + "☆" * (5 - n)


def _donut(value: int, total: int, label: str, color: str, unit: str = "") -> go.Figure:
    pct = min(value / total, 1.0) if total > 0 else 0.0
    remaining = max(total - value, 0)
    fig = go.Figure(go.Pie(
        values=[max(value, 1), max(remaining, 0)],
        hole=0.72,
        marker=dict(colors=[color, "#E9ECEF"], line=dict(width=0)),
        textinfo="none",
        hoverinfo="skip",
        direction="clockwise",
        sort=False,
    ))
    fig.add_annotation(
        text=f"<b>{value}</b><br><sub>{unit}</sub>",
        x=0.5, y=0.5,
        font=dict(size=15, color="#212529", family="Heebo"),
        showarrow=False,
    )
    fig.update_layout(
        title=dict(text=label, x=0.5, font=dict(size=13, color="#6c757d", family="Heebo")),
        showlegend=False,
        margin=dict(t=30, b=5, l=5, r=5),
        height=140,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _safe_web(cat):
    r = st.session_state.get(f"web_{cat}")
    if not isinstance(r, dict):
        return None
    if not {"name", "cal", "pro", "carb", "fat"}.issubset(r):
        return None
    return r


def _advance(data=None):
    if data:
        st.session_state.reg.update(data)
    st.session_state.step += 1
    st.rerun()


def _go_back():
    st.session_state.step = max(1, st.session_state.step - 1)
    st.rerun()


def _logout():
    try:
        if "token" in st.query_params:
            token = st.query_params["token"]
            db.delete_remember_token(token)
            st.query_params.clear()
    except Exception:
        pass
    for k in ("uid", "username"):
        st.session_state[k] = None
    st.session_state.page = "auth"
    st.session_state.step = 1
    st.session_state.reg = {}
    st.rerun()


def _render_sidebar(uid, u):
    username = st.session_state.get("username") or db.get_username_by_phone(uid)
    with st.sidebar:
        st.markdown(
            f"<div style='font-size:1.05rem;font-weight:700;color:#1B4332;margin-bottom:2px;padding:4px 0'>"
            f"שלום, {username}</div>",
            unsafe_allow_html=True,
        )
        goal_map = {"bulk": "הגדלת מסה", "cut": "ירידה", "maintain": "שמירה"}
        st.write(f"**מטרה:** {goal_map.get(u.get('goal', 'maintain'), '---')}")
        st.write(f"**יעד:** {int(_target(u))} קל'/יום")
        st.write(f"**TDEE:** {u.get('tdee', '---')} קל'")
        st.write(f"**כשרות:** {'כשר' if u.get('is_kosher', 1) else 'לא כשר'}")

        st.markdown("---")

        today_str = date.today().isoformat()
        water = u.get("water_cups") or 0
        if u.get("water_date") != today_str:
            water = 0
        st.write(f"**מים:** {water}/8 כוסות")
        st.write("●" * min(water, 8) + "○" * max(8 - water, 0))
        if st.button("+ כוס מים", use_container_width=True, key="sidebar_water"):
            db.add_water_cup(uid)
            st.rerun()

        st.markdown("---")
        st.write("**ניווט**")
        if st.button("תפריט יומי", use_container_width=True, key="nav_menu"):
            st.session_state.page = "main"
            st.rerun()
        if st.button("קהילה", use_container_width=True, key="nav_community"):
            st.session_state.page = "community"
            st.rerun()
        if st.button("הפרופיל שלי", use_container_width=True, key="nav_profile"):
            st.session_state.page = "my_profile"
            st.rerun()

        st.markdown("---")
        if st.button("התנתק", use_container_width=True, key="nav_logout"):
            _logout()


def show_auth():
    try:
        token = st.query_params.get("token")
        if token:
            phone = db.verify_remember_token(token)
            if phone:
                username = db.get_username_by_phone(phone)
                st.session_state.uid = phone
                st.session_state.username = username
                st.session_state.page = "main"
                st.rerun()
    except Exception:
        pass

    _, center, _ = st.columns([1, 2, 1])
    with center:
        with st.container():
            st.markdown(
                "<div class='auth-logo'>"
                "<h1>תזונה חכמה</h1>"
                "<p>רשת חברתית לתזונה בריאה</p>"
                "</div>",
                unsafe_allow_html=True,
            )
            st.markdown("---")

        tab_login, tab_signup = st.tabs(["כניסה לחשבון", "הרשמה חדשה"])

        with tab_login:
            with st.container():
                with st.form("form_login"):
                    st.markdown(
                        "<div style='padding-bottom:4px;font-weight:600'>שם משתמש</div>",
                        unsafe_allow_html=True,
                    )
                    uname = st.text_input("שם משתמש", label_visibility="collapsed")
                    st.markdown(
                        "<div style='padding-bottom:4px;font-weight:600'>סיסמה</div>",
                        unsafe_allow_html=True,
                    )
                    passwd = st.text_input("סיסמה", type="password", label_visibility="collapsed")
                    remember = st.checkbox("זכור אותי (30 יום)")
                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("כניסה", use_container_width=True, type="primary")
                    if submitted:
                        if not uname.strip() or not passwd:
                            st.error("נא למלא שם משתמש וסיסמה")
                        else:
                            ok, result = db.authenticate(uname.strip(), passwd)
                            if ok:
                                st.session_state.uid = result
                                st.session_state.username = uname.strip().lower()
                                st.session_state.page = "main"
                                if remember:
                                    try:
                                        token = db.create_remember_token(result)
                                        st.query_params["token"] = token
                                    except Exception:
                                        pass
                                st.rerun()
                            else:
                                st.error(result)

        with tab_signup:
            with st.container():
                with st.form("form_signup"):
                    st.markdown(
                        "<div style='padding-bottom:4px;font-weight:600'>שם משתמש (לפחות 3 תווים)</div>",
                        unsafe_allow_html=True,
                    )
                    new_uname = st.text_input("שם משתמש", label_visibility="collapsed")
                    st.markdown(
                        "<div style='padding-bottom:4px;font-weight:600'>סיסמה (לפחות 6 תווים)</div>",
                        unsafe_allow_html=True,
                    )
                    new_pass = st.text_input("סיסמה", type="password", label_visibility="collapsed")
                    st.markdown(
                        "<div style='padding-bottom:4px;font-weight:600'>אימות סיסמה</div>",
                        unsafe_allow_html=True,
                    )
                    new_pass2 = st.text_input("אימות סיסמה", type="password", label_visibility="collapsed")
                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    submitted2 = st.form_submit_button("הרשמה", use_container_width=True, type="primary")
                    if submitted2:
                        if len(new_uname.strip()) < 3:
                            st.error("שם משתמש חייב להכיל לפחות 3 תווים")
                        elif len(new_pass) < 6:
                            st.error("סיסמה חייבת להכיל לפחות 6 תווים")
                        elif new_pass != new_pass2:
                            st.error("הסיסמאות אינן תואמות")
                        else:
                            ok, result = db.create_account(new_uname.strip(), new_pass)
                            if ok:
                                st.session_state.uid = result
                                st.session_state.username = new_uname.strip().lower()
                                st.session_state.page = "profile_setup"
                                st.session_state.step = 1
                                st.session_state.reg = {}
                                st.rerun()
                            else:
                                st.error(result)


def _pstep1():
    st.subheader("שלב 1 מתוך 4 - פרטים אישיים")
    with st.form("ps1"):
        name = st.text_input("שם מלא", placeholder="הזן שם מלא...")
        sex = st.radio("מין ביולוגי", ["זכר", "נקבה"], horizontal=True)
        if st.form_submit_button("הבא", use_container_width=True, type="primary"):
            if not name.strip():
                st.error("נא להזין שם")
            else:
                _advance({"name": name.strip(), "sex": "M" if sex == "זכר" else "F"})


def _pstep2():
    st.subheader("שלב 2 מתוך 4 - נתונים פיזיים")
    d = st.session_state.reg
    with st.form("ps2"):
        c1, c2 = st.columns(2)
        age    = c1.number_input("גיל (שנים)", 16, 80, int(d.get("age", 25)), step=1)
        height = c2.number_input("גובה (סנטימטר)", 140, 220, int(d.get("height_cm", 170)), step=1)
        weight = c1.number_input("משקל (קילוגרם)", 35.0, 200.0,
                                   float(d.get("weight_kg", 70)), step=0.5, format="%.1f")
        act_opts = {1:"1 - יושבני", 2:"2 - קל", 3:"3 - מתון", 4:"4 - פעיל", 5:"5 - אינטנסיבי"}
        act = c2.selectbox("פעילות גופנית", list(act_opts.keys()),
                            index=int(d.get("activity", 2)) - 1,
                            format_func=lambda x: act_opts[x])
        b1, b2 = st.columns(2)
        if b1.form_submit_button("חזור", use_container_width=True):
            _go_back()
        if b2.form_submit_button("הבא", use_container_width=True, type="primary"):
            _advance({"age": int(age), "height_cm": int(height),
                      "weight_kg": float(weight), "activity": int(act)})


def _pstep3():
    st.subheader("שלב 3 מתוך 4 - כשרות וטעם")
    d = st.session_state.reg
    with st.form("ps3"):
        kosher = st.toggle("שמירת כשרות - הפרדת בשר וחלב 6 שעות",
                            value=bool(d.get("is_kosher", 1)))
        st.markdown("---")
        pref = st.radio("העדפת מזון",
                        ["פחמימות - פסטה, אורז, לחם", "שומנים בריאים - אבוקדו, דגים, אגוזים"],
                        index=0 if d.get("carb_pref", "carbs") == "carbs" else 1)
        spice = st.radio("טעם מועדף", ["חריף", "עדין"],
                         index=0 if d.get("spice_pref") == "spicy" else 1, horizontal=True)
        dis = st.text_input("מאכלים שאינך אוהב (מופרדים בפסיק)",
                             value=d.get("disliked_foods", ""),
                             placeholder="עגבנייה, גבינה, פטריות...")
        b1, b2 = st.columns(2)
        if b1.form_submit_button("חזור", use_container_width=True):
            _go_back()
        if b2.form_submit_button("הבא", use_container_width=True, type="primary"):
            _advance({"is_kosher": 1 if kosher else 0,
                      "carb_pref": "carbs" if "פחמימות" in pref else "fats",
                      "spice_pref": "spicy" if "חריף" in spice else "mild",
                      "disliked_foods": dis.strip()})


def _pstep4(uid):
    st.subheader("שלב 4 מתוך 4 - מטרה ומחויבות")
    d = st.session_state.reg
    with st.form("ps4"):
        goal_opts = {
            "הגדלת מסה שרירית": "bulk",
            "ירידה במשקל":       "cut",
            "שמירה על המשקל":    "maintain",
        }
        goal_label = st.radio("מה המטרה שלך?", list(goal_opts.keys()))
        goal = goal_opts[goal_label]

        gkg = None
        commit = None
        if goal != "maintain":
            verb = "לעלות" if goal == "bulk" else "לרדת"
            gkg = st.number_input(f"כמה קילוגרם תרצה {verb}?",
                                   1.0, 60.0, float(d.get("goal_kg") or 10), 0.5, format="%.1f")
            commit = st.radio("רמת מחויבות", list(COMMITMENT.keys()), index=1,
                              captions=["0.25 ק\"ג/שבוע", "0.5 ק\"ג/שבוע (מומלץ)",
                                        "0.8 ק\"ג/שבוע", "1 ק\"ג/שבוע"])

        if d.get("weight_kg") and d.get("height_cm") and d.get("age") and d.get("sex"):
            tdee_v = _tdee(float(d["weight_kg"]), float(d["height_cm"]),
                           int(d["age"]), str(d["sex"]), int(d.get("activity", 2)))
            ci = COMMITMENT.get(commit, {}) if commit else {}
            delta = ci.get("delta", 0)
            bonus = ci.get("bulk_bonus", 0) if goal == "bulk" else 0
            tgt = tdee_v if goal == "maintain" else (
                tdee_v - delta if goal == "cut" else tdee_v + delta + bonus
            )
            c1, c2, c3 = st.columns(3)
            c1.metric("TDEE", f"{tdee_v} קל'")
            c2.metric("יעד יומי", f"{tgt} קל'")
            if goal != "maintain" and commit and gkg:
                weeks = round(float(gkg) / COMMITMENT[commit]["kg_week"])
                c3.metric("צפי", f"~{weeks} שבועות")
            if goal == "bulk" and commit == "קיצוני ⚡":
                st.warning("מצב קיצוני: עודף 2100 קל' ביום - מאוד אינטנסיבי!")

        st.markdown("---")
        b1, b2 = st.columns(2)
        go_back = b1.form_submit_button("חזור", use_container_width=True)
        go_next = b2.form_submit_button("צור פרופיל", use_container_width=True, type="primary")

    if go_back:
        _go_back()
    if go_next:
        if not d.get("weight_kg") or not d.get("height_cm"):
            st.error("חזור ומלא נתונים פיזיים")
            return
        try:
            tdee_v = _tdee(float(d["weight_kg"]), float(d["height_cm"]),
                           int(d["age"]), str(d["sex"]), int(d.get("activity", 2)))
            ci = COMMITMENT.get(commit, {}) if commit else {}
            db.update_user(
                uid,
                name=str(d["name"]), sex=str(d["sex"]), age=int(d["age"]),
                height_cm=int(d["height_cm"]), weight_kg=float(d["weight_kg"]),
                activity=int(d["activity"]), is_kosher=int(d.get("is_kosher", 1)),
                carb_pref=str(d.get("carb_pref", "carbs")),
                spice_pref=str(d.get("spice_pref", "mild")),
                disliked_foods=str(d.get("disliked_foods", "")),
                goal=goal,
                goal_kg=float(gkg) if gkg else None,
                commitment_label=commit,
                daily_delta=int(ci.get("delta", 0)),
                tdee=int(tdee_v),
                state="COMPLETED",
            )
            db.log_weight(uid, float(d["weight_kg"]))
            st.session_state.page = "main"
            st.session_state.step = 1
            st.session_state.reg = {}
            st.rerun()
        except Exception as exc:
            st.error(f"שגיאה בשמירת הפרופיל: {exc}")


def show_profile_setup(uid):
    st.markdown(
        "<h1 style='color:#1B4332'>הגדרת פרופיל תזונה</h1>",
        unsafe_allow_html=True,
    )
    st.progress(st.session_state.step / 4, text=f"שלב {st.session_state.step} מתוך 4")
    s = st.session_state.step
    if s == 1:   _pstep1()
    elif s == 2: _pstep2()
    elif s == 3: _pstep3()
    elif s == 4: _pstep4(uid)


def show_dashboard(uid, u):
    target_cal = int(_target(u))
    tab_menu, tab_shop, tab_progress, tab_profile_edit = st.tabs([
        "תפריט יומי", "רשימת קניות", "התקדמות", "עריכת פרופיל"
    ])

    with tab_menu:
        name_disp = u.get("name", "").split()[0] if u.get("name") else ""
        st.markdown(
            f"<h2 style='color:#1B4332;margin-bottom:4px;'>שלום, {name_disp}</h2>",
            unsafe_allow_html=True,
        )

        consumed = db.get_daily_calories(uid)
        pct = min(consumed / target_cal, 1.0) if target_cal else 0.0
        remaining = max(target_cal - consumed, 0)

        today_logs = db.get_today_logs(uid)

        goal_pro  = max(int(target_cal * 0.30 / 4), 1)
        goal_carb = max(int(target_cal * 0.45 / 4), 1)
        goal_fat  = max(int(target_cal * 0.25 / 9), 1)
        est_pro = est_carb = est_fat = 0
        if today_logs:
            for row in today_logs:
                mid = row.get("meal_id", "")
                r = RECIPES.get(mid, {})
                est_pro  += r.get("pro",  0)
                est_carb += r.get("carb", 0)
                est_fat  += r.get("fat",  0)

        dc1, dc2, dc3, dc4 = st.columns([1, 1, 1, 1])
        dc1.plotly_chart(
            _donut(consumed,  target_cal, "קלוריות",  "#1B4332", f"/{target_cal}"),
            use_container_width=True, config={"displayModeBar": False},
        )
        dc2.plotly_chart(
            _donut(est_pro,   goal_pro,   "חלבון",    "#D90429", "g"),
            use_container_width=True, config={"displayModeBar": False},
        )
        dc3.plotly_chart(
            _donut(est_carb,  goal_carb,  "פחמימות",  "#F9A825", "g"),
            use_container_width=True, config={"displayModeBar": False},
        )
        dc4.plotly_chart(
            _donut(est_fat,   goal_fat,   "שומן",     "#6c757d", "g"),
            use_container_width=True, config={"displayModeBar": False},
        )

        st.progress(pct)
        if pct >= 1.0:
            st.success("הגעת ליעד היומי!")
        else:
            st.info(f"נותר: {remaining} קל' ליעד")

        if u.get("goal") == "bulk" and u.get("commitment_label") == "קיצוני ⚡":
            st.warning("מצב קיצוני פעיל - עודף של 2100 קל' ביום")

        st.markdown("---")

        for cat, lbl in [("breakfast", "ארוחת בוקר"),
                          ("lunch",    "ארוחת צהריים"),
                          ("dinner",   "ארוחת ערב")]:
            with st.container():
                st.markdown(f"### {lbl}")

                web_r = _safe_web(cat)
                keys  = _sorted_keys(cat, u)
                idx   = int(st.session_state[f"swap_{cat}"]) % len(keys)
                current = web_r if web_r else RECIPES.get(keys[idx])

                if not current:
                    st.info("טוען מתכון...")
                    st.markdown("---")
                    continue

                st.markdown(
                    f'<div class="recipe-card">'
                    f'<b style="font-size:1.05rem">{current.get("name","---")}</b><br>'
                    f'<span style="color:#D90429;font-weight:700">{current.get("cal",0)} קל\'</span>'
                    f'&nbsp;&nbsp;'
                    f'חלבון {current.get("pro",0)}g'
                    f'&nbsp;·&nbsp;'
                    f'פחמימות {current.get("carb",0)}g'
                    f'&nbsp;·&nbsp;'
                    f'שומן {current.get("fat",0)}g'
                    f'&nbsp;·&nbsp;'
                    f'{current.get("prep","---")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                ings = current.get("ingredients") or []
                if ings:
                    st.caption("מרכיבים: " + " · ".join(str(i) for i in ings[:5]))

                b1, b2, b3, b4 = st.columns(4)

                if b1.button("אכלתי", key=f"ate_{cat}"):
                    cal = int(current.get("cal", 0))
                    db.add_daily_calories(uid, cal)
                    db.log_meal(uid, keys[idx] if not web_r else "web",
                                str(current.get("name", "")),
                                str(current.get("type", "pareve")), cat, cal)
                    if current.get("type") == "meat":
                        db.update_user(uid, last_meat_ts=datetime.utcnow().isoformat())
                    st.toast(f"{current.get('name','')} - {cal} קל'")
                    st.rerun()

                if b2.button("החלף", key=f"swap_{cat}_btn"):
                    st.session_state[f"web_{cat}"] = None
                    st.session_state[f"swap_{cat}"] = (idx + 1) % len(keys)
                    st.rerun()

                if b3.button("מהרשת", key=f"web_{cat}_btn"):
                    off = int(st.session_state.get(f"web_off_{cat}", 0))
                    with st.spinner("מחפש מתכון..."):
                        fetched = fetch_web_recipe(cat, u, off)
                    if fetched and isinstance(fetched, dict):
                        st.session_state[f"web_{cat}"] = fetched
                        st.session_state[f"web_off_{cat}"] = off + 1
                    else:
                        st.warning("לא נמצא מתכון, נסה שוב.")
                    st.rerun()

                if web_r and b4.button("מקומי", key=f"local_{cat}"):
                    st.session_state[f"web_{cat}"] = None
                    st.rerun()

                with st.expander("פרטים מלאים — מרכיבים והוראות", expanded=False):
                    ings_full = current.get("ingredients") or []
                    if ings_full:
                        st.markdown("**מרכיבים:**")
                        for ing in ings_full:
                            st.write(f"- {ing}")
                    steps_full = current.get("steps") or []
                    if steps_full:
                        st.markdown("**הוראות הכנה:**")
                        for step in steps_full:
                            st.write(step)
                    if not ings_full and not steps_full:
                        st.info("אין פרטים נוספים למתכון זה")

                top_recs = db.get_top_community_recipes(category=cat, limit=3)
                if top_recs:
                    with st.expander(f"המלצות קהילה עבור {lbl}", expanded=False):
                        st.caption("ממוינות לפי דירוג גבוה ביותר")
                        for i, rec in enumerate(top_recs):
                            likes  = rec.get("likes_count", 0)
                            stars  = _stars(likes)
                            medal  = ["🥇", "🥈", "🥉"][i] if i < 3 else ""
                            st.markdown(
                                f'<div class="community-card">'
                                f'{medal} <b>{rec["name"]}</b>'
                                f'&nbsp;<span class="badge badge-comm">קהילה</span><br>'
                                f'<span class="stars">{stars}</span>'
                                f'&nbsp;{likes} לייקים'
                                f'&nbsp;·&nbsp;{rec.get("calories",0)} קל\''
                                f'&nbsp;·&nbsp;{rec.get("protein",0)}g חלבון'
                                f'&nbsp;·&nbsp;{rec.get("username","")}'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                            if rec.get("difficulty") or rec.get("prep_time"):
                                parts = []
                                if rec.get("difficulty"): parts.append(f"קושי: {rec['difficulty']}")
                                if rec.get("prep_time"):  parts.append(f"זמן: {rec['prep_time']}")
                                st.caption(" · ".join(parts))
                            comm_c1, comm_c2 = st.columns([1, 5])
                            if comm_c1.button("אכלתי", key=f"comm_ate_{cat}_{rec['id']}"):
                                db.add_daily_calories(uid, int(rec.get("calories", 0)))
                                db.log_meal(uid, f"comm_{rec['id']}",
                                            str(rec["name"]), "pareve", cat,
                                            int(rec.get("calories", 0)))
                                st.toast(f"{rec['name']} - {rec.get('calories',0)} קל'")
                                st.rerun()

                st.markdown("---")

        logs = db.get_today_logs(uid)
        if logs:
            st.write("### רשומות היום")
            df = pd.DataFrame(logs)[["meal_name", "calories", "logged_at"]].copy()
            df.columns = ["ארוחה", "קלוריות", "שעה"]
            df["שעה"] = pd.to_datetime(df["שעה"]).dt.strftime("%H:%M")
            st.table(df)

    with tab_shop:
        st.markdown("<h2>רשימת קניות שבועית</h2>", unsafe_allow_html=True)
        st.caption("x5 לשבוע שלם")
        meals = {}
        for cat in ("breakfast", "lunch", "dinner"):
            wr = _safe_web(cat)
            meals[cat] = wr if wr else RECIPES.get(_sorted_keys(cat, u)[0], {})
        seen, rows = set(), []
        for cat, meal in meals.items():
            for ing in meal.get("ingredients") or []:
                key = str(ing).split()[0].lower() if ing else ""
                if key and key not in seen:
                    seen.add(key)
                    rows.append({"מרכיב": str(ing), "ארוחה": str(meal.get("name", ""))})
        if rows:
            st.table(pd.DataFrame(rows))
        if u.get("disliked_foods"):
            st.warning(f"מוסר מהתפריט: {u['disliked_foods']}")

    with tab_progress:
        st.markdown("<h2>התקדמות</h2>", unsafe_allow_html=True)
        c_chart, c_form = st.columns([2, 1])
        with c_chart:
            wh = db.get_weight_history(uid, days=30)
            if wh:
                wdf = pd.DataFrame(wh)
                wdf["day"] = pd.to_datetime(wdf["day"])
                st.write("### משקל - 30 ימים")
                st.line_chart(wdf.set_index("day")["weight_kg"])
            else:
                st.info("הוסף משקל ראשון בטופס.")
            ch = db.get_calorie_history(uid, days=7)
            if ch:
                cdf = pd.DataFrame(ch)
                cdf["day"] = pd.to_datetime(cdf["day"])
                cdf["יעד"] = target_cal
                st.write("### קלוריות - 7 ימים")
                st.line_chart(
                    cdf.set_index("day").rename(columns={"total": "בפועל"})[["בפועל", "יעד"]]
                )
        with c_form:
            st.write("### עדכון משקל")
            with st.form("wf"):
                nw = st.number_input("משקל (ק\"ג)", 30.0, 300.0,
                                      float(u.get("weight_kg") or 70), 0.5, "%.1f")
                if st.form_submit_button("שמור", use_container_width=True, type="primary"):
                    db.log_weight(uid, nw)
                    st.success(f"{nw} ק\"ג נשמר!")
                    st.rerun()
            goal_t  = u.get("goal", "maintain")
            goal_kg = u.get("goal_kg") or 0
            if goal_t != "maintain" and goal_kg:
                hist = db.get_weight_history(uid, days=365)
                if hist:
                    done = max(
                        hist[0]["weight_kg"] - hist[-1]["weight_kg"]
                        if goal_t == "cut"
                        else hist[-1]["weight_kg"] - hist[0]["weight_kg"],
                        0,
                    )
                    pg = min(done / float(goal_kg), 1.0)
                    st.write("### התקדמות למטרה")
                    st.metric("הושג", f"{round(done, 1)} ק\"ג")
                    st.metric("יעד", f"{float(goal_kg):.1f} ק\"ג")
                    st.progress(pg)
                    if pg >= 1.0:
                        st.balloons()
                        st.success("הגעת ליעד!")

    with tab_profile_edit:
        st.markdown("<h2>עריכת פרופיל</h2>", unsafe_allow_html=True)
        goal_disp = {"bulk": "הגדלת מסה", "cut": "ירידה", "maintain": "שמירה"}
        rows_p = [
            ["שם",       str(u.get("name", "---"))],
            ["גיל",      f"{u.get('age','---')} שנים"],
            ["גובה",     f"{u.get('height_cm','---')} ס\"מ"],
            ["משקל",     f"{u.get('weight_kg','---')} ק\"ג"],
            ["TDEE",     f"{u.get('tdee','---')} קל'"],
            ["יעד יומי", f"{target_cal} קל'"],
            ["מטרה",     goal_disp.get(u.get("goal","maintain"), "---")],
            ["מחויבות",  str(u.get("commitment_label") or "---")],
            ["כשרות",    "כשר" if u.get("is_kosher", 1) else "לא כשר"],
            ["העדפה",    "פחמימות" if u.get("carb_pref") == "carbs" else "שומנים"],
            ["טעם",      "חריף" if u.get("spice_pref") == "spicy" else "עדין"],
            ["מוסרים",   str(u.get("disliked_foods") or "---")],
        ]
        st.table(pd.DataFrame(rows_p, columns=["שדה", "ערך"]))
        st.write("### עדכון מהיר")
        with st.form("ef"):
            upd_w = st.number_input("משקל (ק\"ג)", 30.0, 300.0,
                                     float(u.get("weight_kg") or 70), 0.5, "%.1f")
            upd_d = st.text_input("מאכלים אסורים", value=str(u.get("disliked_foods") or ""))
            upd_k = st.toggle("כשרות", value=bool(u.get("is_kosher", 1)))
            upd_p = st.radio("העדפת מזון", ["פחמימות", "שומנים בריאים"],
                              index=0 if u.get("carb_pref") == "carbs" else 1)
            if st.form_submit_button("שמור שינויים", use_container_width=True, type="primary"):
                new_tdee = _tdee(upd_w, float(u.get("height_cm", 170)),
                                 int(u.get("age", 25)), str(u.get("sex", "M")),
                                 int(u.get("activity", 2)))
                db.update_user(uid, weight_kg=upd_w,
                               disliked_foods=upd_d.strip(),
                               is_kosher=1 if upd_k else 0,
                               carb_pref="carbs" if "פחמימות" in upd_p else "fats",
                               tdee=int(new_tdee))
                db.log_weight(uid, upd_w)
                st.success("הפרופיל עודכן!")
                st.rerun()


def show_community(uid, u):
    username = st.session_state.get("username") or db.get_username_by_phone(uid)
    tab_feed, tab_recipes = st.tabs(["פיד קהילתי", "מתכוני קהילה"])

    with tab_feed:
        st.markdown("<h2>פיד קהילתי</h2>", unsafe_allow_html=True)
        with st.form("new_post_form"):
            content = st.text_area("שתף עדכון עם הקהילה...", max_chars=500,
                                    placeholder="היום אכלתי ארוחת בוקר מצוינת! הגעתי ל-2000 קל'...")
            if st.form_submit_button("פרסם", use_container_width=True, type="primary"):
                if content.strip():
                    db.add_feed_post(uid, username, content.strip())
                    st.rerun()
                else:
                    st.warning("נא לכתוב משהו לפני הפרסום")
        st.markdown("---")
        posts = db.get_feed_posts(40)
        if not posts:
            st.info("הפיד ריק - היה הראשון לפרסם!")
        for post in posts:
            posted_date = str(post.get("posted_at", ""))[:16].replace("T", " ")
            with st.container():
                st.markdown(
                    f'<div class="feed-card">'
                    f'<div style="font-weight:700;font-size:.95rem">{post["username"]}'
                    f'<span style="color:#6c757d;font-weight:400;font-size:.82rem;margin-right:8px">· {posted_date}</span>'
                    f'</div>'
                    f'<div style="margin-top:6px;line-height:1.6">{post["content"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if post["phone"] == uid:
                    if st.button("מחק", key=f"del_post_{post['id']}", help="מחק פוסט"):
                        db.delete_feed_post(post["id"], uid)
                        st.rerun()

    with tab_recipes:
        st.markdown("<h2>מתכוני קהילה</h2>", unsafe_allow_html=True)

        with st.expander("שתף מתכון חדש", expanded=False):
            st.write("#### חישוב תזונה אוטומטי")
            auto_ings = st.text_area(
                "הזן מרכיבים לחישוב אוטומטי",
                placeholder="200 גרם עוף, 1 אבוקדו, 1 כוס אורז",
                key="auto_ings_input",
                height=80,
            )
            if st.button("חשב תזונה אוטומטית", key="btn_auto_calc"):
                if auto_ings.strip():
                    est = estimate_nutrition(auto_ings.strip())
                    st.session_state["est_cal"]  = est[0]
                    st.session_state["est_pro"]  = est[1]
                    st.session_state["est_carb"] = est[2]
                    st.session_state["est_fat"]  = est[3]
                else:
                    st.warning("הזן מרכיבים לפני החישוב")

            if "est_cal" in st.session_state:
                em1, em2, em3, em4 = st.columns(4)
                em1.metric("קלוריות (מוערך)", st.session_state["est_cal"])
                em2.metric("חלבון (מוערך)",   f"{st.session_state['est_pro']}g")
                em3.metric("פחמימות (מוערך)", f"{st.session_state['est_carb']}g")
                em4.metric("שומן (מוערך)",    f"{st.session_state['est_fat']}g")
                st.caption("הערכים הועברו לטופס שיתוף המתכון למטה")

            st.markdown("---")
            with st.form("share_recipe_form"):
                r_name = st.text_input("שם המתכון")
                r_desc = st.text_area("תיאור קצר (אופציונלי)", max_chars=200)
                r_cat  = st.selectbox("קטגוריה",
                                       ["breakfast", "lunch", "dinner", "snack"],
                                       format_func=lambda x: {
                                           "breakfast": "ארוחת בוקר",
                                           "lunch":     "ארוחת צהריים",
                                           "dinner":    "ארוחת ערב",
                                           "snack":     "חטיף",
                                       }[x])
                r_ings  = st.text_area("מרכיבים (שורה לכל מרכיב)",
                                        value=auto_ings if auto_ings.strip() else "",
                                        placeholder="200 גרם עוף\n1 כוס אורז\nשמן זית")
                r_inst  = st.text_area("הוראות הכנה",
                                        placeholder="1. בשל את האורז...\n2. צלה את העוף...")
                fd1, fd2, fd3 = st.columns(3)
                r_media = fd1.text_input("קישור תמונה / סרטון (אופציונלי)", placeholder="https://...")
                r_prep  = fd2.text_input("זמן הכנה", placeholder="30 דקות")
                r_diff  = fd3.selectbox("רמת קושי", ["", "קל", "בינוני", "קשה"])
                ci1, ci2, ci3, ci4 = st.columns(4)
                r_cal  = ci1.number_input("קלוריות",    0, 4000, st.session_state.get("est_cal",  400), step=10)
                r_pro  = ci2.number_input("חלבון (g)",  0, 200,  st.session_state.get("est_pro",   30), step=1)
                r_carb = ci3.number_input("פחמימות (g)",0, 400,  st.session_state.get("est_carb",  40), step=1)
                r_fat  = ci4.number_input("שומן (g)",   0, 200,  st.session_state.get("est_fat",   15), step=1)
                if st.form_submit_button("שתף מתכון", use_container_width=True, type="primary"):
                    if not r_name.strip():
                        st.error("נא להזין שם מתכון")
                    elif not r_ings.strip():
                        st.error("נא להזין מרכיבים")
                    else:
                        db.share_recipe(uid, username, r_name.strip(), r_desc.strip(),
                                        r_ings.strip(), r_inst.strip(), r_cat,
                                        r_cal, r_pro, r_carb, r_fat,
                                        media_url=r_media.strip(),
                                        prep_time=r_prep.strip(),
                                        difficulty=r_diff)
                        for k in ("est_cal","est_pro","est_carb","est_fat"):
                            st.session_state.pop(k, None)
                        st.success("המתכון שותף בהצלחה!")
                        st.rerun()

        st.markdown("---")
        liked_ids = db.get_liked_recipe_ids(uid)
        saved_ids = db.get_saved_recipe_ids(uid)
        recipes   = db.get_community_recipes(50)

        if not recipes:
            st.info("אין עדיין מתכונים קהילתיים - היה הראשון לשתף!")

        for rec in recipes:
            cat_heb = {"breakfast":"בוקר","lunch":"צהריים","dinner":"ערב","snack":"חטיף"}.get(
                rec.get("category",""), "")
            st.markdown(
                f'<div class="recipe-card">'
                f'<b style="font-size:1.05rem">{rec["name"]}</b>'
                f'&nbsp;<span class="badge badge-comm">קהילה · {cat_heb}</span><br>'
                f'<span style="color:#D90429;font-weight:700">{rec.get("calories",0)} קל\'</span>'
                f'&nbsp;·&nbsp;חלבון {rec.get("protein",0)}g'
                f'&nbsp;·&nbsp;פחמימות {rec.get("carbs",0)}g'
                f'&nbsp;·&nbsp;שומן {rec.get("fat",0)}g'
                f'</div>',
                unsafe_allow_html=True,
            )

            media_url = (rec.get("media_url") or "").strip()
            if media_url:
                lower_url = media_url.lower()
                if any(lower_url.endswith(ext) for ext in (".mp4",".mov",".webm",".ogg")):
                    st.video(media_url)
                else:
                    try:
                        st.image(media_url, use_container_width=True)
                    except Exception:
                        st.link_button("פתח מדיה", media_url)

            if rec.get("description"):
                st.write(rec["description"])

            if rec.get("ingredients"):
                with st.expander("מרכיבים"):
                    for line in rec["ingredients"].split("\n"):
                        if line.strip():
                            st.write(f"- {line.strip()}")

            has_details = any([rec.get("instructions"), rec.get("prep_time"), rec.get("difficulty")])
            if has_details:
                with st.expander("פרטים נוספים"):
                    if rec.get("difficulty") or rec.get("prep_time"):
                        dc1, dc2 = st.columns(2)
                        if rec.get("difficulty"): dc1.metric("רמת קושי", rec["difficulty"])
                        if rec.get("prep_time"):  dc2.metric("זמן הכנה", rec["prep_time"])
                    if rec.get("instructions"):
                        st.write("**הוראות הכנה:**")
                        for line in rec["instructions"].split("\n"):
                            if line.strip():
                                st.write(line.strip())

            shared_date = str(rec.get("shared_at",""))[:10]
            st.caption(f"שותף על ידי {rec['username']} | {shared_date} | "
                       f"{rec['likes_count']} לייקים · {rec['saves_count']} שמירות")

            btn_c1, btn_c2, _ = st.columns([1, 1, 4])
            rid = rec["id"]
            like_label = f"❤️ {rec['likes_count']}" if rid in liked_ids else f"♡ {rec['likes_count']}"
            save_label = "שמור" if rid not in saved_ids else "נשמר"
            if btn_c1.button(like_label, key=f"like_{rid}"):
                db.toggle_like(rid, uid)
                st.rerun()
            if btn_c2.button(save_label, key=f"save_{rid}"):
                db.toggle_save(rid, uid)
                st.rerun()

            st.markdown("---")


def show_profile_page(uid, u):
    username   = st.session_state.get("username") or db.get_username_by_phone(uid)
    target_cal = int(_target(u))

    st.markdown(f"<h2>הפרופיל של {username}</h2>", unsafe_allow_html=True)
    st.markdown("---")

    col_stat, col_goal = st.columns(2)
    with col_stat:
        st.write("### נתונים")
        st.metric("TDEE",         f"{u.get('tdee',0)} קל'")
        st.metric("יעד יומי",     f"{target_cal} קל'")
        st.metric("משקל נוכחי",  f"{u.get('weight_kg','---')} ק\"ג")
    with col_goal:
        st.write("### מטרה")
        goal_disp = {"bulk":"הגדלת מסה","cut":"ירידה במשקל","maintain":"שמירה"}
        st.write(f"**{goal_disp.get(u.get('goal','maintain'),'---')}**")
        if u.get("commitment_label"):
            st.write(f"מחויבות: {u['commitment_label']}")
        if u.get("goal_kg"):
            st.write(f"יעד: {u['goal_kg']} ק\"ג")
        st.write(f"כשרות: {'כשר' if u.get('is_kosher',1) else 'לא כשר'}")

    st.markdown("---")

    my_posts = db.get_posts_by_user(uid)
    st.write(f"### הפוסטים שלי ({len(my_posts)})")
    if my_posts:
        for post in my_posts:
            c1, c2 = st.columns([10, 1])
            with c1:
                posted_date = str(post.get("posted_at",""))[:16].replace("T"," ")
                st.write(f"{posted_date}")
                st.write(post["content"])
            with c2:
                if st.button("מחק", key=f"profile_del_{post['id']}", help="מחק"):
                    db.delete_feed_post(post["id"], uid)
                    st.rerun()
            st.markdown("---")
    else:
        st.info("טרם פרסמת פוסטים")

    my_recipes = db.get_recipes_by_user(uid)
    st.write(f"### המתכונים שלי ({len(my_recipes)})")
    if my_recipes:
        for rec in my_recipes:
            cat_heb = {"breakfast":"בוקר","lunch":"צהריים","dinner":"ערב","snack":"חטיף"}.get(
                rec.get("category",""),"")
            st.write(f"**{rec['name']}** · {cat_heb}")
            st.write(f"קלוריות: {rec.get('calories',0)} | חלבון: {rec.get('protein',0)}g | "
                     f"פחמימות: {rec.get('carbs',0)}g | שומן: {rec.get('fat',0)}g")
            st.caption(f"{rec['likes_count']} לייקים · {str(rec.get('shared_at',''))[:10]}")
            st.markdown("---")
    else:
        st.info("טרם שיתפת מתכונים")

    saved = db.get_saved_recipes(uid)
    st.write(f"### מתכונים שמורים ({len(saved)})")
    if saved:
        for rec in saved:
            st.write(f"**{rec['name']}** · {rec.get('username','')}")
            st.write(f"קלוריות: {rec.get('calories',0)} | חלבון: {rec.get('protein',0)}g | "
                     f"פחמימות: {rec.get('carbs',0)}g | שומן: {rec.get('fat',0)}g")
            st.markdown("---")
    else:
        st.info("אין מתכונים שמורים")


def _main():
    uid  = st.session_state.get("uid")
    page = st.session_state.get("page", "auth")

    if not uid:
        show_auth()
        return

    user = db.get_user(uid)
    if not user:
        st.session_state.uid  = None
        st.session_state.page = "auth"
        st.rerun()
        return

    if user.get("state") != "COMPLETED":
        show_profile_setup(uid)
        return

    _render_sidebar(uid, user)

    if page == "community":
        show_community(uid, user)
    elif page == "my_profile":
        show_profile_page(uid, user)
    else:
        show_dashboard(uid, user)


try:
    _main()
except Exception as err:
    st.error(f"שגיאה: {err}")
    if st.button("רענן דף"):
        st.rerun()
