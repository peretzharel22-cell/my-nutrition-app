import re
import db
from datetime import datetime, timezone

# ─────────────────────────────────────────────────────────────────────────────
# RECIPES  —  all 100% kosher (no pork/shellfish, no meat+dairy per recipe)
# type: meat | dairy | pareve
# bulk_friendly: True = high-calorie density for mass gain
# ─────────────────────────────────────────────────────────────────────────────

RECIPES = {
    # ── BREAKFAST (regular) ───────────────────────────────────────────────────
    "b1": {
        "name": "אומלט חלבון עם ירקות", "category": "breakfast",
        "type": "pareve", "macro_focus": "fats", "bulk_friendly": False,
        "cal": 280, "pro": 36, "carb": 8,  "fat": 10, "prep": "10 דק׳",
        "ingredients": ["6 חלבוני ביצה", "½ פלפל אדום", "½ עגבנייה",
                        "חופן תרד", "ספריי שמן כשר", "מלח, פלפל, כמון"],
        "steps": ["1. טרוף חלבונים עם תבלינים.",
                  "2. טגן ירקות 2 דקות.", "3. שפוך חלבונים, בשל 3 דקות, קפל."],
    },
    "b2": {
        "name": "דייסת שיבולת שועל עם חלבון", "category": "breakfast",
        "type": "dairy", "macro_focus": "carbs", "bulk_friendly": False,
        "cal": 350, "pro": 30, "carb": 42, "fat": 7,  "prep": "8 דק׳",
        "ingredients": ["50 גרם שיבולת שועל", "1 כוס חלב 1% כשר",
                        "1 מנה אבקת חלבון וניל כשרה (25 גרם)", "½ בננה", "קינמון"],
        "steps": ["1. בשל שיבולת שועל בחלב 5 דקות.", "2. הוסף אבקת חלבון.",
                  "3. הגש עם בננה וקינמון."],
    },
    "b3": {
        "name": "סלט טונה על לחם שיפון", "category": "breakfast",
        "type": "pareve", "macro_focus": "carbs", "bulk_friendly": False,
        "cal": 310, "pro": 34, "carb": 22, "fat": 9,  "prep": "7 דק׳",
        "ingredients": ["1 קופסת טונה כשרה במים (185 גרם)", "1 ביצה קשה",
                        "1 כף מיונז כשר", "½ מלפפון", "2 פרוסות לחם שיפון",
                        "מיץ לימון, מלח, פלפל"],
        "steps": ["1. ערבב טונה + ביצה + מיונז + לימון + תבלינים.",
                  "2. הוסף מלפפון.", "3. הגש על לחם שיפון."],
    },
    # ── BREAKFAST (bulk) ──────────────────────────────────────────────────────
    "b_bulk": {
        "name": "שייק מסה ביתי 💪", "category": "breakfast",
        "type": "pareve", "macro_focus": "carbs", "bulk_friendly": True,
        "cal": 710, "pro": 42, "carb": 74, "fat": 22, "prep": "5 דק׳",
        "ingredients": ["2 מנות אבקת חלבון פרווה כשרה (60 גרם)",
                        "1 בננה גדולה קפואה",
                        "2 כפות חמאת בוטנים כשרה (30 גרם)",
                        "1 כוס חלב שיבולת שועל",
                        "2 כפות שיבולת שועל גולמי",
                        "1 כף דבש כשר"],
        "steps": ["1. שים הכל בבלנדר.",
                  "2. בלל 30 שניות עד לקרמיות.",
                  "3. שתה מיד — לא לאחסן."],
    },

    # ── LUNCH (regular) ───────────────────────────────────────────────────────
    "l1": {
        "name": "חזה עוף בגריל עם ירקות", "category": "lunch",
        "type": "meat", "macro_focus": "fats", "bulk_friendly": False,
        "cal": 460, "pro": 52, "carb": 18, "fat": 17, "prep": "25 דק׳",
        "ingredients": ["200 גרם חזה עוף כשר", "1 כף שמן זית",
                        "מיץ ½ לימון", "2 שיני שום",
                        "פפריקה מעושנת, תימין, מלח, פלפל",
                        "קישוא + פלפל לצלייה"],
        "steps": ["1. מרינדה: שמן + לימון + שום + תבלינים, 15 דקות.",
                  "2. גריל: 5-6 דקות כל צד.",
                  "3. צלה ירקות 4 דקות. הגש."],
    },
    "l2": {
        "name": "סלמון בגריל עם קינואה", "category": "lunch",
        "type": "pareve", "macro_focus": "balanced", "bulk_friendly": False,
        "cal": 500, "pro": 46, "carb": 36, "fat": 18, "prep": "30 דק׳",
        "ingredients": ["200 גרם פילה סלמון כשר (יש קשקשים וסנפירים)",
                        "½ כוס קינואה", "1 כוס ציר ירקות כשר",
                        "1 כף שמן זית", "מיץ לימון, שמיר, מלח, פלפל"],
        "steps": ["1. בשל קינואה בציר 15 דקות.",
                  "2. תבל סלמון, צלה 3-4 דקות כל צד.",
                  "3. הגש על קינואה."],
    },
    "l3": {
        "name": "קציצות הודו ברוטב עגבניות", "category": "lunch",
        "type": "meat", "macro_focus": "fats", "bulk_friendly": False,
        "cal": 480, "pro": 50, "carb": 24, "fat": 18, "prep": "35 דק׳",
        "ingredients": ["300 גרם הודו טחון כשר", "1 ביצה",
                        "2 כפות פירורי לחם כשר", "2 שיני שום",
                        "400 גרם עגבניות מרוסקות", "בזיליקום, אורגנו, מלח, פלפל"],
        "steps": ["1. ערבב הודו + ביצה + פירורי לחם + שום + תבלינים → כדורים.",
                  "2. הזהב מכל הצדדים.",
                  "3. הוסף עגבניות, בשל מכוסה 20 דקות."],
    },
    "l4": {
        "name": "מרק עדשים כתומות", "category": "lunch",
        "type": "pareve", "macro_focus": "carbs", "bulk_friendly": False,
        "cal": 370, "pro": 22, "carb": 52, "fat": 8,  "prep": "35 דק׳",
        "ingredients": ["1 כוס עדשים כתומות", "1 בצל", "2 גזרים", "4 שיני שום",
                        "כמון + כורכום", "1 ליטר ציר ירקות כשר", "מיץ ½ לימון"],
        "steps": ["1. טגן בצל + שום → גזרים + תבלינים.",
                  "2. הוסף עדשים + ציר, בשל 25 דקות.",
                  "3. בלל במוט, הוסף לימון."],
    },
    # ── LUNCH (bulk) ──────────────────────────────────────────────────────────
    "l_bulk": {
        "name": "פסטה עם חזה עוף ושמן זית 💪", "category": "lunch",
        "type": "meat", "macro_focus": "carbs", "bulk_friendly": True,
        "cal": 660, "pro": 50, "carb": 64, "fat": 18, "prep": "25 דק׳",
        "ingredients": ["200 גרם חזה עוף כשר, פרוס",
                        "100 גרם פסטה מחיטה מלאה כשרה",
                        "3 כפות שמן זית",
                        "4 שיני שום פרוסות",
                        "עגבניות שרי 10 יח'",
                        "בזיליקום טרי, מלח, פלפל"],
        "steps": ["1. בשל פסטה לפי הוראות האריזה.",
                  "2. צלה עוף במחבת עם שמן וסחוש 6 דקות כל צד.",
                  "3. הוצא עוף, טגן שום ועגבניות 3 דקות.",
                  "4. ערבב פסטה + עוף + רוטב + בזיליקום."],
    },

    # ── DINNER (regular) ──────────────────────────────────────────────────────
    "d1": {
        "name": "פרגית בתנור עם בטטה", "category": "dinner",
        "type": "meat", "macro_focus": "carbs", "bulk_friendly": False,
        "cal": 530, "pro": 50, "carb": 40, "fat": 18, "prep": "50 דק׳",
        "ingredients": ["2 פרגיות ללא עור כשרות (300 גרם)", "1 בטטה גדולה",
                        "1 כף שמן זית", "פפריקה מעושנת, תימין, רוזמרין, מלח, פלפל"],
        "steps": ["1. חמם תנור 200°C.",
                  "2. בטטה לפלחים + שמן + תבלינים → תבנית.",
                  "3. הוסף פרגיות מתובלות, אפה 45 דקות."],
    },
    "d2": {
        "name": "סלמון בתנור עם ברוקולי", "category": "dinner",
        "type": "pareve", "macro_focus": "fats", "bulk_friendly": False,
        "cal": 420, "pro": 44, "carb": 10, "fat": 22, "prep": "25 דק׳",
        "ingredients": ["200 גרם פילה סלמון כשר", "2 כוסות ברוקולי",
                        "2 כפות שמן זית", "2 שיני שום",
                        "קליפת לימון, שמיר, מלח, פלפל"],
        "steps": ["1. חמם תנור 200°C.",
                  "2. סלמון + ברוקולי על נייר אפייה.",
                  "3. מרח שמן + שום + לימון, אפה 20 דקות."],
    },
    "d3": {
        "name": "טופו מוקפץ עם ירקות", "category": "dinner",
        "type": "pareve", "macro_focus": "balanced", "bulk_friendly": False,
        "cal": 360, "pro": 28, "carb": 28, "fat": 14, "prep": "25 דק׳",
        "ingredients": ["300 גרם טופו קשה כשר", "ברוקולי + גזר + פלפל אדום",
                        "2 כפות רוטב סויה כשר", "1 כף שמן שומשום כשר",
                        "ג׳ינג׳ר מגורר + 2 שיני שום", "שומשום לקישוט"],
        "steps": ["1. טופו לקוביות, יבש, טגן עד פריך → הוצא.",
                  "2. הקפץ ירקות 3 דקות + שום + ג׳ינג׳ר.",
                  "3. החזר טופו + סויה, הקפץ 2 דקות."],
    },
    # ── DINNER (bulk) ────────────────────────────────────────────────────────
    "d_bulk": {
        "name": "פרגית עם פסטה וטחינה 💪", "category": "dinner",
        "type": "meat", "macro_focus": "carbs", "bulk_friendly": True,
        "cal": 780, "pro": 55, "carb": 68, "fat": 26, "prep": "40 דק׳",
        "ingredients": ["300 גרם פרגית כשרה ללא עור",
                        "150 גרם פסטה כשרה",
                        "3 כפות טחינה גולמית כשרה",
                        "2 כפות שמן זית",
                        "2 שיני שום, מיץ לימון",
                        "מלח, פלפל, פפריקה"],
        "steps": ["1. בשל פסטה לפי הוראות האריזה.",
                  "2. תבל פרגית, צלה בתנור 200°C 30 דקות.",
                  "3. ערבב טחינה + שום + לימון + מעט מים לרוטב.",
                  "4. הגש פרגית על פסטה, זלף טחינה מעל."],
    },
}

BY_CATEGORY = {
    "breakfast": ["b1", "b2", "b3", "b_bulk"],
    "lunch":     ["l1", "l2", "l3", "l4", "l_bulk"],
    "dinner":    ["d1", "d2", "d3", "d_bulk"],
}
CAT_LABEL = {
    "breakfast": "🌅 ארוחת בוקר",
    "lunch":     "☀️ ארוחת צהריים",
    "dinner":    "🌙 ארוחת ערב",
}

# ── Commitment levels (0.5kg/week = 550 cal/day base) ─────────────────────────

COMMITMENT = {
    "רגוע 🐢":       {"kg_week": 0.25, "delta": 275,  "bulk_bonus": 0},
    "מאוזן ⚖️":     {"kg_week": 0.50, "delta": 550,  "bulk_bonus": 0},
    "אינטנסיבי 🔥":  {"kg_week": 0.80, "delta": 880,  "bulk_bonus": 500},
    "קיצוני ⚡":     {"kg_week": 1.00, "delta": 1100, "bulk_bonus": 1000},  # 2100 cal/day surplus total
}

ACTIVITY_MULT = {1: 1.20, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.90}

def _bmr(w, h, age, sex):
    base = 10 * w + 6.25 * h - 5 * age
    return round(base + 5 if sex.upper() == "M" else base - 161)

def _tdee(w, h, age, sex, act):
    return round(_bmr(w, h, age, sex) * ACTIVITY_MULT.get(act, 1.375))

def _target(u):
    tdee   = u.get("tdee") or 0
    goal   = u.get("goal", "maintain")
    delta  = u.get("daily_delta") or 550
    label  = u.get("commitment_label") or ""
    if goal == "maintain":
        return tdee
    if goal == "cut":
        return tdee - delta
    # bulk — add aggressive bonus for intense/extreme
    bonus = COMMITMENT.get(label, {}).get("bulk_bonus", 0)
    return tdee + delta + bonus

def _is_aggressive_bulk(u):
    return (u.get("goal") == "bulk" and
            u.get("commitment_label") in ["אינטנסיבי 🔥", "קיצוני ⚡"])

# ── Kosher guard ──────────────────────────────────────────────────────────────

def _meat_wait_hours(last_meat_ts):
    if not last_meat_ts: return 999
    try:
        eaten = datetime.fromisoformat(last_meat_ts).replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - eaten).total_seconds() / 3600
    except Exception:
        return 999

def _kosher_ok(rtype, u):
    """Returns (ok: bool, reason: str)"""
    if not u.get("is_kosher", 1):
        return True, ""   # user not kosher — no restrictions
    if rtype == "dairy":
        hrs = _meat_wait_hours(u.get("last_meat_ts"))
        if hrs < 6:
            left = 6 - hrs
            return False, f"המתן עוד {int(left)}ש׳ {int((left%1)*60)}ד׳ (הפרדת בשר/חלב)"
    return True, ""

# ── Recipe selection & filtering ──────────────────────────────────────────────

def _sorted_keys(category, u):
    cpref    = u.get("carb_pref")
    disliked = u.get("disliked_foods") or ""
    dw       = [w.strip().lower() for w in disliked.split(",") if w.strip()]
    agg_bulk = _is_aggressive_bulk(u)
    kosher   = u.get("is_kosher", 1)
    last_mt  = u.get("last_meat_ts")

    def score(k):
        r   = RECIPES[k]
        # Hard filter: skip non-kosher for kosher users
        if kosher and r["type"] == "dairy":
            hrs = _meat_wait_hours(last_mt)
            if hrs < 6:
                return 999     # push to end, won't appear in top-3
        # Penalise disliked ingredients
        txt = (" ".join(r["ingredients"]) + " " + r["name"]).lower()
        pen = sum(10 for w in dw if w in txt)
        # Bulk priority
        if agg_bulk:
            if r.get("bulk_friendly"):  pen -= 8
            pen -= r["cal"] // 120      # higher-cal = lower score
        # Cut: prefer lower calorie
        elif u.get("goal") == "cut":
            pen += r["cal"] // 250
        # Macro preference
        foc = r.get("macro_focus", "balanced")
        if (cpref == "carbs" and foc == "carbs") or \
           (cpref == "fats"  and foc == "fats"):
            pen -= 1
        return pen

    return sorted(BY_CATEGORY[category], key=score)[:3]


def _fmt_list(category, u):
    keys     = _sorted_keys(category, u)
    cpref    = u.get("carb_pref")
    note     = " (מותאם: 🍝)" if cpref == "carbs" else (" (מותאם: 🥑)" if cpref == "fats" else "")
    target   = _target(u)
    per_meal = target // 3 if target else 0
    agg      = _is_aggressive_bulk(u)

    header = f"*{CAT_LABEL[category]}*{note}\n"
    if agg:
        header += "_⚡ כדי לעמוד בקצב שבחרת, הוספתי מנות עתירות קלוריות ובריאות_\n"
    header += "\n"

    lines = []
    for i, k in enumerate(keys, 1):
        r   = RECIPES[k]
        fit = " ✓" if per_meal and abs(r["cal"] - per_meal) / per_meal <= 0.35 else ""
        bul = " 💪" if r.get("bulk_friendly") and agg else ""
        lines.append(f"*{i}.{bul} {r['name']}*{fit}\n"
                     f"🔥 {r['cal']} קל׳ | 💪 {r['pro']}g חלבון | ⏱ {r['prep']}")
    return header + "\n\n".join(lines)


def _fmt_recipe(r, u):
    ings     = "\n".join(f"  • {i}" for i in r["ingredients"])
    steps    = "\n".join(r["steps"])
    t_icon   = {"meat": "🥩 בשרי", "dairy": "🧀 חלבי", "pareve": "🐟 פרווה"}[r["type"]]
    kosher_l = " | ✡️ כשר" if u.get("is_kosher", 1) else ""
    bulk_msg = ""
    if r.get("bulk_friendly") and _is_aggressive_bulk(u):
        bulk_msg = "\n⚡ _מנה עתירת קלוריות — תומכת בקצב המסה שבחרת_\n"
    return (f"*{r['name']}*\n"
            f"{t_icon}{kosher_l} | 🔥 {r['cal']} קל׳ | 💪 {r['pro']}g | "
            f"🍞 {r['carb']}g | 🥑 {r['fat']}g | ⏱ {r['prep']}\n"
            f"{bulk_msg}\n"
            f"*🛒 מרכיבים:*\n{ings}\n\n*👨‍🍳 הכנה:*\n{steps}\n\n"
            f"בתיאבון! 😋  לחץ *✅ אכלתי* לתיעוד.")


def _cal_bar(consumed, target):
    if not target: return ""
    pct = min(consumed / target, 1.0)
    return "🟩" * round(pct * 10) + "⬜" * (10 - round(pct * 10)) + f"  {round(pct*100)}%"


def _timeline(u):
    goal    = u.get("goal", "maintain")
    goal_kg = u.get("goal_kg") or 0
    label   = u.get("commitment_label") or ""
    if goal == "maintain" or not goal_kg or not label:
        return ""
    info    = COMMITMENT.get(label, {})
    weeks   = round(goal_kg / info.get("kg_week", 0.5))
    months  = round(weeks / 4.3, 1)
    delta   = info.get("delta", 550)
    bonus   = info.get("bulk_bonus", 0) if goal == "bulk" else 0
    verb    = "לרדת" if goal == "cut" else "לעלות"
    total_d = delta + bonus
    return (f"📅 {goal_kg}ק״ג {verb} | {label}\n"
            f"⏳ {weeks} שבועות (~{months} חודשים)\n"
            f"🔻 {total_d} קל׳/יום {'חסר' if goal=='cut' else 'עודף'}")


def _shopping_list(uid):
    u     = db.get_user(uid)
    cpref = u.get("carb_pref")
    dis   = u.get("disliked_foods") or ""
    b = RECIPES[_sorted_keys("breakfast", u)[0]]
    l = RECIPES[_sorted_keys("lunch",     u)[0]]
    d = RECIPES[_sorted_keys("dinner",    u)[0]]
    seen, ings = set(), []
    for meal in (b, l, d):
        for ing in meal["ingredients"]:
            key = ing.split()[0]
            if key not in seen:
                seen.add(key); ings.append(ing)
    lines = [f"🛒 *רשימת קניות שבועית* (×5)\n",
             f"_{b['name']} · {l['name']} · {d['name']}_\n"]
    lines += [f"  • {i}" for i in ings]
    if dis: lines.append(f"\n⚠️ _מוסר: {dis}_")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def process(uid, body):
    text  = body.strip()
    user  = db.get_or_create_user(uid)
    state = user.get("state") or "NEW"

    # ── Reset ──
    if text.lower() in ["איפוס", "reset", "/start", "התחלה"]:
        db.set_state(uid, "ASK_NAME")
        db.reset_daily_calories(uid)
        return "שלום! 👋 אני הבוט התזונתי שלך.\nנבנה תפריט מותאם אישית.\n\nאיך קוראים לך?"

    # ── Registration ──────────────────────────────────────────────────────────

    if state == "NEW":
        db.set_state(uid, "ASK_NAME")
        return "שלום! 👋\nאיך קוראים לך?"

    if state == "ASK_NAME":
        db.update_user(uid, name=text)
        db.set_state(uid, "ASK_SEX")
        return f"נעים מאוד, {text}! 😊\nמה המין שלך?"

    if state == "ASK_SEX":
        sex = "M" if "זכר" in text or text.upper() == "M" else "F"
        db.update_user(uid, sex=sex)
        db.set_state(uid, "ASK_KOSHER")
        return ("האם אתה שומר כשרות? ✡️\n\n"
                "כשר ✓ — הפרדת בשר/חלב (6 שעות), מרכיבים כשרים בלבד\n"
                "לא כשר — ללא הגבלות כשרות")

    if state == "ASK_KOSHER":
        is_k = 1 if text in ["כשר ✓", "כשר", "1", "כן", "yes"] else 0
        db.update_user(uid, is_kosher=is_k)
        db.set_state(uid, "ASK_AGE")
        note = "✡️ תפריט כשר פעיל — כל המרכיבים כשרים והפרדה מלאה." if is_k else "ללא הגבלות כשרות."
        return f"{note}\n\nמה הגיל שלך? (שנים)"

    if state == "ASK_AGE":
        try:
            age = int(text); assert 10 <= age <= 100
        except Exception:
            return "שלח גיל תקין (לדוגמה: 28)"
        db.update_user(uid, age=age); db.set_state(uid, "ASK_HEIGHT")
        return "מה הגובה שלך? (ס״מ)"

    if state == "ASK_HEIGHT":
        try:
            h = float(text); assert 130 <= h <= 220
        except Exception:
            return "שלח גובה תקין (לדוגמה: 175)"
        db.update_user(uid, height_cm=h); db.set_state(uid, "ASK_WEIGHT")
        return "מה המשקל שלך? (ק״ג)"

    if state == "ASK_WEIGHT":
        try:
            w = float(text.replace(",", ".")); assert 30 <= w <= 250
        except Exception:
            return "שלח משקל תקין (לדוגמה: 80)"
        db.update_user(uid, weight_kg=w); db.set_state(uid, "ASK_ACTIVITY")
        return ("מה רמת הפעילות?\n\n"
                "1 — יושבני\n2 — קל (1-3/שבוע)\n3 — מתון (3-5/שבוע)\n"
                "4 — פעיל (6-7/שבוע)\n5 — אינטנסיבי מאוד")

    if state == "ASK_ACTIVITY":
        if text not in ["1","2","3","4","5"]: return "שלח מספר 1-5."
        db.update_user(uid, activity=int(text)); db.set_state(uid, "ASK_GOAL")
        return "מה המטרה?\n\n1 — 🏋️ הגדלת מסה\n2 — 🔥 ירידה במשקל\n3 — ⚖️ שמירה"

    if state == "ASK_GOAL":
        gmap = {"1":"bulk","2":"cut","3":"maintain"}
        if text not in gmap: return "שלח 1, 2 או 3."
        goal = gmap[text]
        db.update_user(uid, goal=goal)
        if goal == "maintain":
            db.set_state(uid, "ASK_TASTE_1"); return _taste1_msg()
        verb = "לרדת" if goal == "cut" else "לעלות"
        db.set_state(uid, "ASK_KG")
        return f"כמה ק״ג תרצה {verb}? (לדוגמה: 10)"

    if state == "ASK_KG":
        try:
            kg = float(text.replace(",",".")); assert 0.5 <= kg <= 80
        except Exception:
            return "שלח מספר ק״ג (לדוגמה: 10)"
        db.update_user(uid, goal_kg=kg); db.set_state(uid, "ASK_COMMITMENT")
        return ("באיזו רמת מחויבות?\n\n"
                "🐢 *רגוע* — 0.25ק״ג/שבוע\n"
                "⚖️ *מאוזן* — 0.5ק״ג/שבוע (מומלץ)\n"
                "🔥 *אינטנסיבי* — 0.8ק״ג/שבוע\n"
                "⚡ *קיצוני* — 1ק״ג/שבוע")

    if state == "ASK_COMMITMENT":
        c = COMMITMENT.get(text)
        if not c: return "לחץ על אחד הכפתורים."
        db.update_user(uid, commitment_label=text, daily_delta=c["delta"])
        db.set_state(uid, "ASK_TASTE_1")
        u    = db.get_user(uid)
        kg   = u.get("goal_kg", 0)
        weeks = round(kg / c["kg_week"])
        bonus = c["bulk_bonus"]
        bulk_note = (f"\n⚡ *מסה אגרסיבית:* +{bonus} קל׳ יומי נוסף!" if
                     u.get("goal") == "bulk" and bonus > 0 else "")
        return (f"✓ {text} — {c['delta'] + (bonus if u.get('goal')=='bulk' else 0)} קל׳/יום"
                f"{bulk_note}\nצפי: {weeks} שבועות\n\n" + _taste1_msg())

    if state == "ASK_TASTE_1":
        if text not in ["1","2"]: return "שלח 1 או 2."
        db.update_user(uid, carb_pref="carbs" if text=="1" else "fats")
        db.set_state(uid, "ASK_TASTE_2")
        return "2/3 🌶️ טעם מועדף:\n\n1 — חריף\n2 — עדין"

    if state == "ASK_TASTE_2":
        if text not in ["1","2"]: return "שלח 1 או 2."
        db.update_user(uid, spice_pref="spicy" if text=="1" else "mild")
        db.set_state(uid, "ASK_TASTE_3")
        return "3/3 🚫 מאכלים שאתה לא אוהב?\nכתוב מופרד בפסיק — או שלח *דלג*"

    if state == "ASK_TASTE_3":
        dis = "" if text.lower() in ["דלג","skip","אין"] else text
        db.update_user(uid, disliked_foods=dis)
        u      = db.get_user(uid)
        tdee   = _tdee(u["weight_kg"], u["height_cm"], u["age"], u["sex"], u["activity"])
        db.update_user(uid, tdee=tdee, state="COMPLETED")
        u      = db.get_user(uid)
        target = _target(u)
        glab   = {"bulk":"הגדלת מסה 🏋️","cut":"ירידה במשקל 🔥","maintain":"שמירה ⚖️"}[u["goal"]]
        plab   = "🍝 פחמימות" if u.get("carb_pref")=="carbs" else "🥑 שומנים"
        kosher_line = "✡️ תפריט כשר פעיל\n" if u.get("is_kosher",1) else ""
        bulk_banner = ""
        if _is_aggressive_bulk(u):
            bulk_banner = ("\n⚡ *כדי לעמוד בקצב שבחרת, הוספתי מנות עתירות "
                           "קלוריות ובריאות* (אגוזים, פסטה, טחינה, שייקים)\n")
        return (f"✅ *הפרופיל מוכן!*\n\n"
                f"{kosher_line}"
                f"🔥 TDEE: {tdee} קל׳/יום\n"
                f"🎯 יעד: *{target} קל׳/יום* ({glab})\n"
                f"🍽️ {plab}"
                f"{bulk_banner}\n"
                f"{_timeline(u)}\n\n"
                f"לחץ *בוקר*, *צהריים* או *ערב* להתחיל!")

    # ── Active user ───────────────────────────────────────────────────────────

    u = db.get_user(uid)

    if text == "בוקר":   db.set_state(uid, "SELECT_B"); return _fmt_list("breakfast", u)
    if text == "צהריים": db.set_state(uid, "SELECT_L"); return _fmt_list("lunch", u)
    if text == "ערב":    db.set_state(uid, "SELECT_D"); return _fmt_list("dinner", u)

    if text == "תפריט" or state == "SHOW_MENU":
        db.set_state(uid, "SHOW_MENU")
        return "📋 *בחר ארוחה:*\n\n• *בוקר*\n• *צהריים*\n• *ערב*"

    # ── Recipe selection ──────────────────────────────────────────────────────
    cat_map = {"SELECT_B":"breakfast","SELECT_L":"lunch","SELECT_D":"dinner"}
    if state in cat_map and text in ["1","2","3"]:
        category = cat_map[state]
        keys     = _sorted_keys(category, u)
        key      = keys[int(text)-1]
        recipe   = RECIPES[key]

        # Smart kosher validation
        ok, reason = _kosher_ok(recipe["type"], u)
        if not ok:
            # Try next available kosher recipe
            fallback = next((k for k in keys[1:] if _kosher_ok(RECIPES[k]["type"], u)[0]), None)
            if fallback:
                recipe = RECIPES[fallback]
                key    = fallback
            else:
                return f"⚠️ *כשרות:* {reason}\nנסה ארוחה אחרת."

        if recipe["type"] == "meat":
            db.update_user(uid, last_meat_ts=datetime.utcnow().isoformat())

        db.set_last_recipe(uid, key, recipe["cal"])
        db.set_state(uid, "COMPLETED")
        return _fmt_recipe(recipe, u)

    # ── I ate this ──
    if text in ["אכלתי ✅","אכלתי","✅ אכלתי","✅אכלתי"]:
        key = u.get("last_recipe_key")
        if not key or key not in RECIPES:
            return "בחר ארוחה קודם — לחץ *בוקר*, *צהריים* או *ערב*."
        recipe = RECIPES[key]
        cal    = recipe["cal"]
        total  = db.add_daily_calories(uid, cal)
        db.log_meal(uid, key, recipe["name"], recipe["type"], recipe["category"], cal)
        u2     = db.get_user(uid)
        target = _target(u2)
        bar    = _cal_bar(total, target)
        remain = max(target - total, 0)
        return (f"✅ *{recipe['name']}* תועדה!\n➕ {cal} קל׳\n\n"
                f"📊 *היום:* {total} / {target} קל׳\n{bar}\n"
                f"{'🎯 הגעת ליעד!' if remain==0 else f'נותר: {remain} קל׳'}")

    # ── Daily summary ──
    if text in ["סיכום יומי","📊 סיכום יומי","סיכום"]:
        if not u or not u.get("tdee"): return "שלח *איפוס* לבניית פרופיל."
        target   = _target(u)
        consumed = db.get_daily_calories(uid)
        bar      = _cal_bar(consumed, target)
        water    = u.get("water_cups") or 0
        w_bar    = "🔵"*min(water,8) + "⚪"*max(8-water,0)
        kosher_l = " | ✡️ כשר" if u.get("is_kosher",1) else ""
        return (f"📊 *סיכום יומי*{kosher_l}\n{'─'*18}\n"
                f"🍽️ צריכה: *{consumed}* קל׳\n🎯 יעד: *{target}* קל׳\n{bar}\n"
                f"{'✅ הגעת ליעד!' if consumed>=target else f'נותר: {max(target-consumed,0)} קל׳'}\n\n"
                f"💧 {w_bar} {water}/8\n\n{_timeline(u)}")

    # ── Shopping list ──
    if text in ["רשימת קניות","🛒 קניות","קניות"]:
        if not u or not u.get("carb_pref"): return "שלח *איפוס* לבניית פרופיל."
        return _shopping_list(uid)

    # ── Profile ──
    if text == "פרופיל":
        if not u or not u.get("tdee"): return "שלח *איפוס*."
        target = _target(u)
        glab   = {"bulk":"הגדלת מסה 🏋️","cut":"ירידה במשקל 🔥","maintain":"שמירה ⚖️"}
        plab   = "🍝 פחמימות" if u.get("carb_pref")=="carbs" else ("🥑 שומנים" if u.get("carb_pref") else "—")
        return (f"📋 *הפרופיל שלך*\n\n"
                f"👤 {u.get('name')} | {u.get('age')} שנים\n"
                f"📏 {u.get('height_cm')} ס״מ | ⚖️ {u.get('weight_kg')} ק״ג\n"
                f"{'✡️ כשר | ' if u.get('is_kosher',1) else ''}{plab}\n\n"
                f"🔥 TDEE: {u['tdee']} קל׳/יום\n"
                f"🎯 יעד: *{target} קל׳/יום* ({glab.get(u.get('goal','maintain'))})\n"
                f"{_timeline(u)}")

    # ── Water ──
    if text in ["מים 💧","מים","💧"]:
        cups = db.add_water_cup(uid)
        bar  = "🔵"*min(cups,8) + "⚪"*max(8-cups,0)
        return f"💧 כוס נוספה!\n{bar}  {cups}/8"

    return "לחץ על כפתור, שלח *תפריט*, או *איפוס*."


def _taste1_msg():
    return "1/3 🍽️ מה עדיף לך?\n\n1 — 🍝 פחמימות (פסטה, אורז, לחם)\n2 — 🥑 שומנים בריאים (אבוקדו, אגוזים, דגים)"


# ─────────────────────────────────────────────────────────────────────────────
# WEB RECIPE ENGINE  (DuckDuckGo Search)
# ─────────────────────────────────────────────────────────────────────────────

_NON_KOSHER_KW = ["pork", "bacon", "ham", "chorizo", "prawn", "shrimp",
                   "lobster", "crab", "shellfish", "clam", "oyster", "lard",
                   "חזיר", "שרימפס", "בשר חזיר", "סרטן"]

# Hebrew DDG queries: [goal_type][meal_category]
_DDG_QUERIES_HE = {
    "bulk": {
        "breakfast": "מתכון כשר עתיר קלוריות ארוחת בוקר חלבון",
        "lunch":     "מתכון כשר עתיר קלוריות ארוחת צהריים עוף בשר",
        "dinner":    "מתכון כשר עתיר קלוריות ארוחת ערב פחמימות חלבון",
    },
    "cut": {
        "breakfast": "מתכון כשר דל קלוריות עתיר חלבון ארוחת בוקר",
        "lunch":     "מתכון כשר לירידה במשקל ארוחת צהריים",
        "dinner":    "מתכון כשר לירידה במשקל ארוחת ערב קל",
    },
    "maintain": {
        "breakfast": "מתכון כשר בריא ארוחת בוקר מאוזן",
        "lunch":     "מתכון כשר בריא ארוחת צהריים",
        "dinner":    "מתכון כשר בריא ארוחת ערב",
    },
}

# 10 hardcoded kosher fallback recipes (used when DDGS fails)
_FALLBACK_RECIPES = [
    {
        "name": "שקשוקה קלאסית", "category": "breakfast",
        "type": "pareve", "macro_focus": "balanced", "bulk_friendly": False,
        "cal": 320, "pro": 22, "carb": 18, "fat": 14, "prep": "20 דק׳",
        "ingredients": ["4 ביצים כשרות", "2 עגבניות", "1 פלפל אדום",
                        "1 בצל", "2 שיני שום", "כמון, פפריקה, מלח, פלפל",
                        "1 כף שמן זית", "פטרוזיליה לקישוט"],
        "steps": ["1. טגן בצל ופלפל עד ריכוך.",
                  "2. הוסף שום + עגבניות + תבלינים, בשל 8 דקות.",
                  "3. שבור ביצים לתוך הרוטב, בשל מכוסה 5 דקות."],
        "source": "fallback",
    },
    {
        "name": "טוסט אבוקדו עם ביצה", "category": "breakfast",
        "type": "pareve", "macro_focus": "fats", "bulk_friendly": False,
        "cal": 380, "pro": 18, "carb": 28, "fat": 20, "prep": "10 דק׳",
        "ingredients": ["2 פרוסות לחם מחיטה מלאה כשר", "1 אבוקדו בשל",
                        "2 ביצים", "מיץ לימון, מלח, פלפל",
                        "שמן זית, פלפל אדום"],
        "steps": ["1. צלה לחם.", "2. מעך אבוקדо + לימון + מלח.",
                  "3. מרח על לחם, הוסף ביצה עלומה."],
        "source": "fallback",
    },
    {
        "name": "שייק בוקר עתיר חלבון 💪", "category": "breakfast",
        "type": "pareve", "macro_focus": "carbs", "bulk_friendly": True,
        "cal": 620, "pro": 40, "carb": 68, "fat": 18, "prep": "5 דק׳",
        "ingredients": ["2 מנות אבקת חלבון פרווה כשרה",
                        "1 בננה קפואה", "2 כפות חמאת בוטנים כשרה",
                        "1 כוס חלב שיבולת שועל", "1 כף דבש",
                        "קרח"],
        "steps": ["1. שים הכל בבלנדר.", "2. בלל 30 שניות.", "3. שתה מיד."],
        "source": "fallback",
    },
    {
        "name": "עוף בגריל עם אורז בסמטי", "category": "lunch",
        "type": "meat", "macro_focus": "carbs", "bulk_friendly": False,
        "cal": 520, "pro": 48, "carb": 52, "fat": 14, "prep": "30 דק׳",
        "ingredients": ["200 גרם חזה עוף כשר", "¾ כוס אורז בסמטי",
                        "1 כף שמן זית", "מיץ לימון",
                        "כמון, פפריקה, שום, מלח, פלפל"],
        "steps": ["1. בשל אורז לפי הוראות.",
                  "2. תבל עוף, צלה בגריל 6 דקות כל צד.",
                  "3. הגש על אורז עם לימון."],
        "source": "fallback",
    },
    {
        "name": "מרק עוף ירקות כשר", "category": "lunch",
        "type": "meat", "macro_focus": "balanced", "bulk_friendly": False,
        "cal": 340, "pro": 32, "carb": 22, "fat": 10, "prep": "40 דק׳",
        "ingredients": ["300 גרם חזה עוף כשר", "2 גזרים", "2 עמודי סלרי",
                        "1 בצל", "2 שיני שום",
                        "כורכום, כמון, מלח, פלפל", "1.5 ליטר מים"],
        "steps": ["1. בשל עוף עם ירקות ותבלינים 35 דקות.",
                  "2. הוצא עוף ופרק לסיבים.",
                  "3. החזר לסיר, הגש חם."],
        "source": "fallback",
    },
    {
        "name": "פסטה עם סלמון ושמיר 💪", "category": "lunch",
        "type": "pareve", "macro_focus": "carbs", "bulk_friendly": True,
        "cal": 640, "pro": 44, "carb": 68, "fat": 20, "prep": "25 דק׳",
        "ingredients": ["150 גרם פסטה כשרה", "200 גרם פילה סלמון כשר",
                        "2 כפות שמן זית", "3 שיני שום",
                        "שמיר טרי, מיץ לימון", "מלח, פלפל"],
        "steps": ["1. בשל פסטה.", "2. צלה סלמון 4 דקות כל צד.",
                  "3. טגן שום בשמן, ערבב עם פסטה ופירור סלמון."],
        "source": "fallback",
    },
    {
        "name": "סלט ניסואז כשר", "category": "lunch",
        "type": "pareve", "macro_focus": "fats", "bulk_friendly": False,
        "cal": 420, "pro": 38, "carb": 24, "fat": 18, "prep": "20 דק׳",
        "ingredients": ["2 קופסאות טונה כשרה", "4 ביצים קשות",
                        "עגבניות שרי", "שעועית ירוקה מבושלת",
                        "זיתים שחורים כשרים", "2 כפות שמן זית + חומץ"],
        "steps": ["1. בשל ביצים ושעועית.", "2. סדר על צלחת גדולה.",
                  "3. זלף שמן + חומץ."],
        "source": "fallback",
    },
    {
        "name": "פרגית בתנור עם בטטה ורוזמרין", "category": "dinner",
        "type": "meat", "macro_focus": "carbs", "bulk_friendly": False,
        "cal": 540, "pro": 48, "carb": 42, "fat": 18, "prep": "50 דק׳",
        "ingredients": ["2 פרגיות כשרות ללא עור", "2 בטטות בינוניות",
                        "2 כפות שמן זית", "רוזמרין, תימין",
                        "פפריקה מעושנת, מלח, פלפל"],
        "steps": ["1. חמם תנור 200°C.",
                  "2. חתוך בטטות לפלחים, תבל.",
                  "3. הוסף פרגיות מתובלות, אפה 45 דקות."],
        "source": "fallback",
    },
    {
        "name": "קציצות עדשים ירוקות", "category": "dinner",
        "type": "pareve", "macro_focus": "carbs", "bulk_friendly": False,
        "cal": 360, "pro": 22, "carb": 44, "fat": 10, "prep": "40 דק׳",
        "ingredients": ["1 כוס עדשים ירוקות מבושלות", "1 ביצה",
                        "½ בצל מגורר", "2 שיני שום",
                        "3 כפות קמח מחיטה מלאה כשר",
                        "כמון, כוסברה, מלח, פלפל"],
        "steps": ["1. ערבב עדשים + ביצה + בצל + שום + קמח + תבלינים.",
                  "2. צור כדורים שטוחים.",
                  "3. טגן בשמן 4 דקות כל צד."],
        "source": "fallback",
    },
    {
        "name": "סטייק הודו עם ירקות צלויים 💪", "category": "dinner",
        "type": "meat", "macro_focus": "balanced", "bulk_friendly": True,
        "cal": 580, "pro": 58, "carb": 30, "fat": 22, "prep": "35 דק׳",
        "ingredients": ["300 גרם שניצל הודו כשר", "קישוא + פלפלים + חצילים",
                        "3 כפות שמן זית", "2 שיני שום",
                        "טימין, אורגנו, מלח, פלפל"],
        "steps": ["1. חמם תנור 200°C.",
                  "2. חתוך ירקות + תבל + שמן → תבנית, אפה 20 דקות.",
                  "3. הוסף הודו מתובל, אפה 15 דקות נוספות."],
        "source": "fallback",
    },
]


def _pick_fallback(category: str, u: dict, offset: int = 0) -> dict:
    """Return a hardcoded fallback recipe matching category."""
    pool = [r for r in _FALLBACK_RECIPES if r["category"] == category]
    if not pool:
        pool = _FALLBACK_RECIPES
    idx = offset % len(pool)
    return dict(pool[idx])


def _web_estimate_macros(ingredients: list[str]) -> tuple[int, int, int, int]:
    """Return (cal, pro_g, carb_g, fat_g) for a recipe ingredient list."""
    text = " ".join(ingredients).lower()

    pro = 18
    if any(k in text for k in ["chicken", "turkey", "tuna", "salmon", "cod", "sea bass", "tilapia",
                                "עוף", "הודו", "טונה", "סלמון"]):
        pro += 38
    elif any(k in text for k in ["beef", "lamb", "steak", "mince", "ground", "בקר", "כבש"]):
        pro += 32
    elif any(k in text for k in ["egg", "tofu", "lentil", "chickpea", "bean",
                                  "ביצ", "טופו", "עדשים", "חומוס"]):
        pro += 22
    elif any(k in text for k in ["cheese", "yogurt", "cottage", "גבינה", "יוגורט"]):
        pro += 14

    carb = 12
    if any(k in text for k in ["pasta", "spaghetti", "noodle", "פסטה", "ספגטי"]):
        carb += 55
    elif any(k in text for k in ["rice", "quinoa", "אורז", "קינואה"]):
        carb += 46
    elif any(k in text for k in ["potato", "sweet potato", "bread", "flour", "בטטה", "תפוח אדמה", "לחם", "קמח"]):
        carb += 40
    elif any(k in text for k in ["oat", "oatmeal", "שיבולת שועל"]):
        carb += 36
    else:
        carb += 8

    fat = 7
    if any(k in text for k in ["olive oil", "שמן זית", "sunflower oil"]):
        fat += 10
    if any(k in text for k in ["butter", "cream", "cheese", "חמאה", "גבינה", "שמנת"]):
        fat += 13
    if any(k in text for k in ["nut", "almond", "walnut", "tahini", "peanut butter",
                                "אגוז", "שקד", "טחינה", "חמאת בוטנים"]):
        fat += 15
    if any(k in text for k in ["avocado", "coconut", "אבוקדו", "קוקוס"]):
        fat += 12

    cal = pro * 4 + carb * 4 + fat * 9
    return cal, pro, carb, fat


def _extract_ingredients(text: str) -> list[str]:
    """Pull ingredient-like phrases from raw recipe text."""
    FOOD_KW = {
        "cup","tbsp","tsp","oz","gram","g ","ml","lb","tablespoon","teaspoon",
        "chicken","beef","fish","salmon","tuna","egg","rice","pasta","potato",
        "oil","butter","flour","sugar","milk","cheese","onion","garlic","tomato",
        "salt","pepper","herb","spice","lemon","olive","broth","stock","bean",
        "lentil","oat","cream","yogurt","avocado","nut","almond","quinoa",
        "עוף","בשר","דג","סלמון","טונה","ביצ","אורז","פסטה","תפוח","שמן",
        "חמאה","קמח","סוכר","חלב","גבינה","בצל","שום","עגבנ","מלח","פלפל",
        "כמון","טחינה","אבוקדו","אגוז","שקד","עדשים","חומוס","ק׳ג","גרם",
    }
    candidates = []
    for part in text.replace(" • ", "\n").replace(" · ", "\n").split("\n"):
        part = part.strip()
        if 4 < len(part) < 90 and any(fw in part.lower() for fw in FOOD_KW):
            candidates.append(part)
    return candidates[:12]


def fetch_web_recipe(category: str, u: dict, offset: int = 0) -> dict | None:
    """
    Fetch a real-time recipe via DuckDuckGo (Hebrew queries).
    Falls back to hardcoded kosher recipes if search fails.
    Returns a recipe dict compatible with RECIPES format.
    """
    is_k       = bool(u.get("is_kosher", 1))
    goal       = str(u.get("goal") or "maintain")
    is_extreme = (u.get("commitment_label") == "קיצוני ⚡" and goal == "bulk")
    target_cal = int(_target(u))
    per_meal   = max(target_cal // 3, 300) if target_cal else 600

    # Build Hebrew query
    goal_key = goal if goal in _DDG_QUERIES_HE else "maintain"
    query = _DDG_QUERIES_HE[goal_key].get(category,
            _DDG_QUERIES_HE["maintain"].get(category, "מתכון כשר בריא"))

    # Try DuckDuckGo
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=8))
    except Exception:
        results = []

    for result in results:
        if not isinstance(result, dict):
            continue

        title = str(result.get("title") or "").split(" - ")[0].split(" | ")[0].strip()
        body  = str(result.get("body") or "")
        if not title or len(title) < 4:
            continue

        combined = (title + " " + body).lower()

        # Kosher filter
        if is_k and any(kw in combined for kw in _NON_KOSHER_KW):
            continue

        # Extract ingredients from body
        ingredients = _extract_ingredients(body)
        macro_src   = ingredients if ingredients else [body[:300]]
        cal, pro, carb, fat = _web_estimate_macros(macro_src)

        # Extreme bulk boost
        if is_extreme and cal < 650:
            cal  = int(cal * 1.6); pro  = int(pro * 1.4)
            carb = int(carb * 1.6); fat  = int(fat * 1.4)

        # Calorie fit check (±70% of per-meal target)
        if per_meal and abs(cal - per_meal) / max(per_meal, 1) > 0.70:
            continue

        # Detect meal type
        if any(k in combined for k in ["beef","chicken","turkey","lamb","duck","meat","veal",
                                        "עוף","בשר","הודו","כבש"]):
            mtype = "meat"
        elif any(k in combined for k in ["milk","cheese","butter","cream","dairy","yogurt",
                                          "חלב","גבינה","חמאה","שמנת","יוגורט"]):
            mtype = "dairy"
        else:
            mtype = "pareve"

        focus = "carbs" if carb > pro + 20 else "fats" if fat > pro + 5 else "balanced"
        steps = [s.strip() for s in body.replace(". ", ".\n").split("\n")
                 if 15 < len(s.strip()) < 200][:4]

        return {
            "name":          title[:60],
            "category":      str(category),
            "type":          mtype,
            "macro_focus":   focus,
            "bulk_friendly": bool(cal > 500),
            "cal":  max(int(cal), 100),
            "pro":  max(int(pro), 5),
            "carb": max(int(carb), 5),
            "fat":  max(int(fat), 3),
            "prep": "30 דק׳",
            "ingredients": [str(i)[:80] for i in (ingredients or [body[:60]])[:10]],
            "steps":        [str(s)[:150] for s in steps],
            "image":        "",
            "source":       "web",
        }

    # ── Fallback to hardcoded kosher recipes ──────────────────────────────────
    return _pick_fallback(category, u, offset)


# =============================================================================
# AUTO-NUTRITION ESTIMATOR
# Parses free-text ingredient lists (English + Hebrew) and returns
# (calories, protein_g, carb_g, fat_g) estimates.
# =============================================================================

# Nutrition per 100 g: (cal, pro, carb, fat)
_FOOD_PER_100G = {
    "chicken":       (165, 31,  0,   3.6),
    "turkey":        (189, 29,  0,   7.0),
    "beef":          (250, 26,  0,  17.0),
    "lamb":          (294, 25,  0,  21.0),
    "salmon":        (208, 20,  0,  13.0),
    "tuna":          (130, 28,  0,   1.0),
    "cod":           ( 82, 18,  0,   0.7),
    "shrimp":        ( 85, 18,  1,   1.0),
    "tofu":          ( 76,  8,  2,   4.8),
    "lentils":       (116,  9, 20,   0.4),
    "chickpeas":     (164,  9, 27,   2.6),
    "beans":         (127,  9, 23,   0.5),
    "edamame":       (121, 11,  9,   5.2),
    "cheese":        (350, 25,  1,  28.0),
    "milk":          ( 42,  3,  5,   1.0),
    "yogurt":        ( 59,  4,  5,   0.4),
    "cottage":       ( 98, 11,  3,   4.3),
    "butter":        (717,  1,  0,  81.0),
    "cream":         (340,  2,  3,  36.0),
    "rice":          (130,  3, 28,   0.3),
    "pasta":         (371, 13, 75,   1.5),
    "oats":          (389, 17, 66,   7.0),
    "bread":         (265,  9, 49,   3.2),
    "flour":         (364, 10, 76,   1.0),
    "quinoa":        (120,  4, 21,   1.9),
    "potato":        ( 77,  2, 17,   0.1),
    "sweet potato":  ( 86,  2, 20,   0.1),
    "broccoli":      ( 34,  3,  7,   0.4),
    "spinach":       ( 23,  3,  4,   0.4),
    "tomato":        ( 18,  1,  4,   0.2),
    "onion":         ( 40,  1,  9,   0.1),
    "garlic":        (149,  6, 33,   0.5),
    "carrot":        ( 41,  1, 10,   0.2),
    "zucchini":      ( 17,  1,  3,   0.3),
    "mushroom":      ( 22,  3,  3,   0.3),
    "olive oil":     (884,  0,  0, 100.0),
    "sunflower oil": (884,  0,  0, 100.0),
    "coconut oil":   (862,  0,  0, 100.0),
    "almond":        (579, 21, 22,  50.0),
    "walnut":        (654, 15, 14,  65.0),
    "cashew":        (553, 18, 30,  44.0),
    "tahini":        (595, 17, 21,  53.0),
    "peanut butter": (588, 25, 20,  50.0),
    "avocado":       (160,  2,  9,  15.0),
    "coconut":       (354,  3, 15,  33.0),
    "banana":        ( 89,  1, 23,   0.3),
    "apple":         ( 52,  0, 14,   0.2),
    "orange":        ( 47,  1, 12,   0.1),
    "mango":         ( 60,  1, 15,   0.4),
    "strawberry":    ( 32,  1,  8,   0.3),
    "honey":         (304,  0, 82,   0.0),
    "sugar":         (387,  0,100,   0.0),
    "chocolate":     (546,  5, 60,  31.0),
    "oat milk":      ( 39,  1,  7,   1.5),
    "almond milk":   ( 13,  0,  1,   1.1),
}

# Hebrew food names -> English key in _FOOD_PER_100G
_HE_TO_EN = {
    "עוף":            "chicken",
    "חזה עוף":        "chicken",
    "הודו":           "turkey",
    "בשר":            "beef",
    "בקר":            "beef",
    "כבש":            "lamb",
    "סלמון":          "salmon",
    "טונה":           "tuna",
    "בקלה":           "cod",
    "שרימפס":         "shrimp",
    "טופו":           "tofu",
    "עדשים":          "lentils",
    "חומוס":          "chickpeas",
    "שעועית":         "beans",
    "גבינה":          "cheese",
    "חלב":            "milk",
    "יוגורט":         "yogurt",
    "קוטג":           "cottage",
    "חמאה":           "butter",
    "שמנת":           "cream",
    "אורז":           "rice",
    "פסטה":           "pasta",
    "ספגטי":          "pasta",
    "שיבולת שועל":    "oats",
    "לחם":            "bread",
    "קמח":            "flour",
    "קינואה":         "quinoa",
    "תפוח אדמה":      "potato",
    "בטטה":           "sweet potato",
    "ברוקולי":        "broccoli",
    "תרד":            "spinach",
    "עגבנייה":        "tomato",
    "עגבניות":        "tomato",
    "בצל":            "onion",
    "שום":            "garlic",
    "גזר":            "carrot",
    "קישוא":          "zucchini",
    "פטריות":         "mushroom",
    "שמן זית":        "olive oil",
    "שמן חמניות":     "sunflower oil",
    "שמן קוקוס":      "coconut oil",
    "שקד":            "almond",
    "שקדים":          "almond",
    "אגוז":           "walnut",
    "אגוזים":         "walnut",
    "קשיו":           "cashew",
    "טחינה":          "tahini",
    "חמאת בוטנים":    "peanut butter",
    "אבוקדו":         "avocado",
    "קוקוס":          "coconut",
    "בננה":           "banana",
    "תפוח":           "apple",
    "תפוז":           "orange",
    "מנגו":           "mango",
    "תות":            "strawberry",
    "דבש":            "honey",
    "סוכר":           "sugar",
    "שוקולד":         "chocolate",
    "חלב שיבולת שועל":"oat milk",
    "חלב שקדים":      "almond milk",
}

# Per-unit items — values are per 1 piece: (cal, pro, carb, fat)
_PER_UNIT = {
    "egg":      (78,  6, 0.6, 5.0),
    "ביצה":     (78,  6, 0.6, 5.0),
    "ביצים":    (78,  6, 0.6, 5.0),
    "avocado":  (240, 3, 13,  22.0),
    "אבוקדו":   (240, 3, 13,  22.0),
    "banana":   (105, 1, 27,   0.4),
    "בננה":     (105, 1, 27,   0.4),
    "apple":    (95,  0, 25,   0.3),
    "תפוח":     (95,  0, 25,   0.3),
    "orange":   (62,  1, 15,   0.2),
    "תפוז":     (62,  1, 15,   0.2),
    "potato":   (160, 4, 37,   0.2),
    "תפוח אדמה":(160, 4, 37,   0.2),
}

# Unit string -> grams conversion
_UNIT_GRAMS = {
    "grams": 1, "gram": 1, "g": 1,
    "גרם": 1, "ג": 1,
    "kg": 1000, "kilogram": 1000,
    "קג": 1000,
    "oz": 28.35, "ounce": 28.35,
    "cup": 240, "cups": 240,
    "כוס": 240, "כוסות": 240,
    "tablespoon": 15, "tbsp": 15,
    "כף": 15, "כפות": 15,
    "teaspoon": 5, "tsp": 5,
    "כפית": 5, "כפיות": 5,
    "ml": 1, "מל": 1,
    "liter": 1000, "l": 1000,
    "ליטר": 1000,
}


def estimate_nutrition(ingredients_text: str) -> tuple[int, int, int, int]:
    """
    Parse a free-text ingredient list (English or Hebrew) and return
    estimated (calories, protein_g, carb_g, fat_g).

    Handles formats like:
        100g chicken
        2 eggs
        1 avocado
        3 כפות שמן זית
        200 גרם סלמון
    """
    totals = [0.0, 0.0, 0.0, 0.0]   # cal, pro, carb, fat

    # Split by commas or newlines into individual ingredient lines
    lines = [
        ln.strip()
        for ln in re.split(r"[,\n;]", ingredients_text)
        if ln.strip()
    ]

    for line in lines:
        line_lo = line.lower().strip()

        # 1. Extract leading number (quantity)
        num_m = re.match(r"^([\d.,/]+)\s*", line_lo)
        quantity = 1.0
        if num_m:
            raw = num_m.group(1)
            try:
                if "/" in raw:
                    parts = raw.split("/")
                    quantity = float(parts[0]) / float(parts[1])
                else:
                    quantity = float(raw.replace(",", "."))
            except ValueError:
                quantity = 1.0

        # 2. Identify unit and convert to grams
        amount_g = None
        for unit, grams_per_unit in sorted(
            _UNIT_GRAMS.items(), key=lambda kv: -len(kv[0])
        ):
            pattern = r"(?<!\w)" + re.escape(unit) + r"(?!\w)"
            if re.search(pattern, line_lo):
                amount_g = quantity * grams_per_unit
                break

        # No unit found → assume quantity is # of whole items (100 g each)
        if amount_g is None:
            amount_g = quantity * 100.0

        # 3. Check per-unit items first (eggs, avocados, etc.)
        matched_unit = False
        for key, (c, p, cb, f) in _PER_UNIT.items():
            if key in line_lo:
                count = quantity  # e.g. "2 eggs"
                totals[0] += c * count
                totals[1] += p * count
                totals[2] += cb * count
                totals[3] += f * count
                matched_unit = True
                break
        if matched_unit:
            continue

        # 4. Translate Hebrew to English for lookup
        food_line = line_lo
        # Sort by length descending to match longer phrases first
        for he_word, en_word in sorted(_HE_TO_EN.items(), key=lambda kv: -len(kv[0])):
            if he_word in food_line:
                food_line = food_line.replace(he_word, en_word)

        # 5. Look up food in nutrition database
        factor = amount_g / 100.0
        for food_name, (cal, pro, carb, fat) in sorted(
            _FOOD_PER_100G.items(), key=lambda kv: -len(kv[0])
        ):
            if food_name in food_line:
                totals[0] += cal  * factor
                totals[1] += pro  * factor
                totals[2] += carb * factor
                totals[3] += fat  * factor
                break

    return (
        max(int(round(totals[0])), 0),
        max(int(round(totals[1])), 0),
        max(int(round(totals[2])), 0),
        max(int(round(totals[3])), 0),
    )
