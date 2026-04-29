import os
import json
import re
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="DrankDrunk", page_icon="🍸", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #F2F2F7;
    color: #1C1C1E;
}
.stApp { background-color: #F2F2F7; }

.brand-header { text-align: center; padding: 1.5rem 0 0.8rem; }
.brand-title  { font-size: 1.9rem; font-weight: 700; color: #1C1C1E; letter-spacing: -0.02em; margin-bottom: 0.15rem; }
.brand-sub    { font-size: 0.72rem; color: #8E8E93; letter-spacing: 0.07em; text-transform: uppercase; }

.section-label {
    font-size: 0.7rem; font-weight: 600; color: #8E8E93;
    letter-spacing: 0.08em; text-transform: uppercase; margin: 1.1rem 0 0.45rem;
}

.ios-card { background: #FFFFFF; border-radius: 16px; padding: 0.1rem 1.1rem; margin-bottom: 0.75rem; }

.stat-row  { display: flex; gap: 10px; margin-bottom: 0.75rem; }
.stat-card { flex: 1; background: #FFFFFF; border-radius: 14px; padding: 0.8rem 0.5rem; text-align: center; }
.stat-label { font-size: 0.62rem; color: #8E8E93; font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 0.2rem; }
.stat-value { font-size: 1.35rem; font-weight: 700; color: #1C1C1E; }

.decision-continue { background:#E8F7EF; border-radius:14px; padding:0.9rem 1.1rem; color:#1A7A48; font-size:0.88rem; font-weight:500; margin-bottom:0.75rem; border-left:4px solid #34C759; }
.decision-caution  { background:#FFF8E6; border-radius:14px; padding:0.9rem 1.1rem; color:#92650A; font-size:0.88rem; font-weight:500; margin-bottom:0.75rem; border-left:4px solid #FF9500; }
.decision-stop     { background:#FEECEC; border-radius:14px; padding:0.9rem 1.1rem; color:#A52A2A; font-size:0.88rem; font-weight:500; margin-bottom:0.75rem; border-left:4px solid #FF3B30; }

.drink-item { display:flex; align-items:center; padding:0.7rem 0; border-bottom:0.5px solid #E5E5EA; }
.drink-item:last-child { border-bottom:none; }
.drink-icon { width:42px; height:42px; border-radius:10px; background:#F2F2F7; display:flex; align-items:center; justify-content:center; font-size:1.25rem; margin-right:0.7rem; flex-shrink:0; }
.drink-info { flex:1; }
.drink-name { font-weight:600; font-size:0.9rem; color:#1C1C1E; margin-bottom:0.1rem; }
.drink-meta { font-size:0.75rem; color:#8E8E93; }
.drink-right { text-align:right; }
.drink-units { font-weight:600; font-size:0.9rem; color:#1C1C1E; }
.drink-dec   { font-size:0.72rem; font-weight:600; margin-top:0.1rem; }

.summary-bar { background:#FFFFFF; border-radius:14px; padding:0.75rem 1rem; display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem; font-size:0.82rem; color:#8E8E93; }
.summary-total { font-weight:700; color:#1C1C1E; }

[data-testid="stTextInput"] input {
    background:#FFFFFF !important; border:0.5px solid #E5E5EA !important;
    border-radius:12px !important; color:#1C1C1E !important;
    font-family:'Inter',sans-serif !important; padding:0.6rem 1rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color:#007AFF !important;
    box-shadow:0 0 0 3px rgba(0,122,255,0.12) !important;
}
[data-testid="stTextInput"] input::placeholder { color:#C7C7CC !important; }

.stButton > button {
    background:#007AFF !important; color:#FFFFFF !important; border:none !important;
    border-radius:12px !important; font-family:'Inter',sans-serif !important;
    font-weight:600 !important; font-size:0.88rem !important;
    padding:0.55rem 1.4rem !important; transition:opacity 0.15s !important;
}
.stButton > button:hover  { opacity:0.88 !important; }
.stButton > button:active { opacity:0.72 !important; }

div[data-testid="stTabs"] button { font-family:'Inter',sans-serif !important; font-weight:500 !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#007AFF !important; border-bottom-color:#007AFF !important; }

.stDataFrame  { border-radius:12px !important; overflow:hidden !important; }
.stWarning    { background:#FFF8E6 !important; border-color:#FF9500 !important; color:#92650A !important; border-radius:12px !important; }
.stInfo       { background:#EAF3FF !important; border-color:#007AFF !important; color:#004EB3 !important; border-radius:12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="brand-header">
  <div class="brand-title">🍸 DrankDrunk</div>
  <div class="brand-sub">Drink Tracker · Smart Decisions</div>
</div>
""", unsafe_allow_html=True)

st.warning("⚠️ Educational estimates only — not medical, legal, or driving-safety advice.")

if "history" not in st.session_state:
    st.session_state.history = []

# ── Constants ──
CATEGORY_EMOJI = {
    "beer": "🍺", "wine": "🍷", "spirit": "🥃",
    "cocktail": "🍹", "mixed": "🍸", "ambiguous": "🥤"
}
LABEL_MAP = {"continue": "Continue", "caution": "Caution", "stop": "Stop"}
ICON_MAP  = {"continue": "✅", "caution": "⚠️", "stop": "🛑"}
DEC_COLOR = {"Continue": "#34C759", "Caution": "#FF9500", "Stop": "#FF3B30"}

# ── Helpers ──
def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found.")
    return json.loads(match.group(0))

def safe_number(value, default):
    try:
        return default if (value is None or value == "") else float(value)
    except Exception:
        return default

def fallback_parse_drink(user_input):
    text = user_input.lower()
    drinks = []
    def qty(t):
        if "4" in t or "four" in t: return 4
        if "3" in t or "three" in t or "several" in t: return 3
        if "2" in t or "two" in t or "couple" in t: return 2
        return 1
    q = qty(text)
    if "beer" in text or "pint" in text or "lager" in text:
        vol = 473 if "pint" in text else (500 if "500" in text else 330)
        drinks.append({"category": "beer", "drink_summary": "beer", "abv_pct": 5, "volume_ml": vol, "quantity": q})
    if "wine" in text or "champagne" in text or "prosecco" in text:
        drinks.append({"category": "wine", "drink_summary": "wine", "abv_pct": 12, "volume_ml": 250 if "250" in text else 150, "quantity": q})
    if any(w in text for w in ["whiskey", "whisky", "vodka", "rum", "gin", "tequila", "shot"]):
        drinks.append({"category": "spirit", "drink_summary": "spirit shot", "abv_pct": 40, "volume_ml": 30, "quantity": q})
    if any(w in text for w in ["mojito", "margarita", "cocktail", "sour", "colada", "negroni", "daiquiri"]):
        drinks.append({"category": "cocktail", "drink_summary": "cocktail", "abv_pct": 12, "volume_ml": 150, "quantity": q})
    if not drinks:
        drinks.append({"category": "ambiguous", "drink_summary": user_input, "abv_pct": 12, "volume_ml": 150, "quantity": q})
    cat = "mixed" if len(drinks) > 1 else drinks[0]["category"]
    return {"category": cat, "drink_summary": user_input, "drinks": drinks,
            "confidence": "medium" if cat != "ambiguous" else "low"}

FEW_SHOT_EXAMPLES = """
Examples (input → JSON):
Input: "whiskey shot"
Output: {"category":"spirit","drink_summary":"whiskey shot","drinks":[{"category":"spirit","drink_summary":"whiskey shot","abv_pct":40,"volume_ml":30,"quantity":1}],"confidence":"high"}
Input: "mojito"
Output: {"category":"cocktail","drink_summary":"mojito","drinks":[{"category":"cocktail","drink_summary":"mojito","abv_pct":12,"volume_ml":150,"quantity":1}],"confidence":"high"}
Input: "2 beers and 1 whiskey"
Output: {"category":"mixed","drink_summary":"2 beers and 1 whiskey","drinks":[{"category":"beer","drink_summary":"beer","abv_pct":5,"volume_ml":330,"quantity":2},{"category":"spirit","drink_summary":"whiskey","abv_pct":40,"volume_ml":30,"quantity":1}],"confidence":"high"}
Input: "a couple drinks"
Output: {"category":"ambiguous","drink_summary":"a couple drinks","drinks":[{"category":"ambiguous","drink_summary":"drink","abv_pct":12,"volume_ml":150,"quantity":2}],"confidence":"low"}
Input: "red wine 250ml"
Output: {"category":"wine","drink_summary":"red wine 250ml","drinks":[{"category":"wine","drink_summary":"red wine","abv_pct":13,"volume_ml":250,"quantity":1}],"confidence":"high"}
"""

def parse_drink_with_ai(user_input):
    prompt = f"""You are an alcohol intake parsing assistant. Convert natural-language drink input into valid JSON only.
Rules: Return JSON only. No markdown. category="mixed" for multiple types. No null values. "couple"=2, "several"=3.
Defaults: beer 330ml 5%, pint 473ml 5%, wine 150ml 12%, spirit 30ml 40%, cocktail 150ml 12%, ambiguous 150ml 12%.
{FEW_SHOT_EXAMPLES}
Return: {{"category":"...","drink_summary":"...","drinks":[{{"category":"...","drink_summary":"...","abv_pct":0,"volume_ml":0,"quantity":0}}],"confidence":"..."}}
User input: {user_input}"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a strict JSON generator. Return only valid JSON with no markdown."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return extract_json(response.choices[0].message.content)

def calculate_total_units(drinks):
    defaults = {"beer": (5, 330), "wine": (12, 150), "spirit": (40, 30), "cocktail": (12, 150), "ambiguous": (12, 150)}
    total = 0
    for d in drinks:
        cat = str(d.get("category", "ambiguous")).lower()
        da, dv = defaults.get(cat, (12, 150))
        total += safe_number(d.get("volume_ml"), dv) * (safe_number(d.get("abv_pct"), da) / 100) * safe_number(d.get("quantity"), 1) / 17.7
    return round(total, 2)

def make_decision(current_units, prior=0.0):
    total = round(current_units + prior, 2)
    if total <= 1.5:
        return "continue", total, f"Your cumulative intake is low ({total} units). Stay hydrated and drink at a comfortable pace."
    elif total <= 3.0:
        return "caution", total, f"Your cumulative intake is moderate ({total} units). Consider slowing down and drinking some water."
    else:
        return "stop", total, f"Your cumulative intake is high ({total} units). It is safer to stop drinking alcohol for now."

# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
tab_drink, tab_log = st.tabs(["🍸 Drink Analyzer", "📓 Log"])

# ───────────────────────────────────────
# Tab 1: Drink Analyzer
# ───────────────────────────────────────
with tab_drink:
    st.markdown('<p class="section-label">Drink Details</p>', unsafe_allow_html=True)

    drink_name = st.text_input(
        "Drink Name", placeholder="e.g. Cheese Milk Cap, Whisky, Red Wine…"
    )

    col_vol, col_abv = st.columns(2)
    with col_vol:
        volume_ml = st.number_input("Volume (ml)", min_value=1, max_value=2000, value=330, step=10)
    with col_abv:
        abv_pct = st.number_input("Alcohol Content (%ABV)", min_value=0.0, max_value=100.0, value=5.0, step=0.5, format="%.1f")

    if st.button("Analyze Drink", use_container_width=True):
        if not drink_name.strip():
            st.error("Please enter a drink name.")
        else:
            with st.spinner("Analyzing…"):
                fb = False
                try:
                    parsed = parse_drink_with_ai(drink_name)
                except Exception:
                    parsed = fallback_parse_drink(drink_name); fb = True

                drinks = [{
                    "category":      parsed.get("drinks", [{}])[0].get("category", "ambiguous") if parsed.get("drinks") else "ambiguous",
                    "drink_summary": drink_name,
                    "abv_pct":       abv_pct,
                    "volume_ml":     volume_ml,
                    "quantity":      1
                }]
                cur = calculate_total_units(drinks)
                prior = sum(e["units"] for e in st.session_state.history)
                decision, cumulative, reason = make_decision(cur, prior)

            cat    = drinks[0]["category"]
            emoji  = CATEGORY_EMOJI.get(cat, "🥤")
            dec_en = LABEL_MAP[decision]

            st.markdown('<p class="section-label">Result</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="stat-row">
              <div class="stat-card"><div class="stat-label">Type</div><div class="stat-value">{emoji}</div></div>
              <div class="stat-card"><div class="stat-label">This Drink</div><div class="stat-value">{cur} u</div></div>
              <div class="stat-card"><div class="stat-label">Session Total</div><div class="stat-value">{cumulative} u</div></div>
              <div class="stat-card"><div class="stat-label">ABV</div><div class="stat-value" style="font-size:1.1rem">{abv_pct}%</div></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(
                f'<div class="decision-{decision}"><strong>{ICON_MAP[decision]} {dec_en}</strong> — {reason}</div>',
                unsafe_allow_html=True
            )

            if fb:
                st.info("AI classification unavailable — rule-based fallback parser used.")

            st.session_state.history.append({
                "drink":    drink_name,
                "type":     cat,
                "ml":       volume_ml,
                "abv":      f"{abv_pct}%",
                "units":    cur,
                "decision": dec_en,
            })

# ───────────────────────────────────────
# Tab 2: Log
# ───────────────────────────────────────
with tab_log:
    if st.session_state.history:
        total_u = round(sum(e["units"] for e in st.session_state.history), 2)
        count   = len(st.session_state.history)

        st.markdown(f"""
        <div class="summary-bar">
          <span>{count} drink{"s" if count != 1 else ""} logged</span>
          <span class="summary-total">Total: {total_u} units</span>
        </div>
        """, unsafe_allow_html=True)

        items_html = ""
        for i, entry in enumerate(reversed(st.session_state.history)):
            em  = CATEGORY_EMOJI.get(entry["type"], "🥤")
            dc  = DEC_COLOR.get(entry["decision"], "#8E8E93")
            sep = "" if i == len(st.session_state.history) - 1 else "border-bottom:0.5px solid #E5E5EA;"
            items_html += f"""
            <div class="drink-item" style="{sep}">
              <div class="drink-icon">{em}</div>
              <div class="drink-info">
                <div class="drink-name">{entry['drink']}</div>
                <div class="drink-meta">{entry['type']} · {entry['ml']}ml · {entry['abv']}</div>
              </div>
              <div class="drink-right">
                <div class="drink-units">{entry['units']} u</div>
                <div class="drink-dec" style="color:{dc}">{entry['decision']}</div>
              </div>
            </div>"""

        st.markdown(f'<div class="ios-card">{items_html}</div>', unsafe_allow_html=True)

        if st.button("Clear Log"):
            st.session_state.history = []
            st.rerun()
    else:
        st.markdown("""
        <div class="ios-card" style="text-align:center;padding:2rem 1rem;color:#8E8E93;font-size:0.88rem;">
          No drinks logged yet. Head to Drink Analyzer to get started.
        </div>""", unsafe_allow_html=True)

    st.markdown('<p style="font-size:0.72rem;color:#8E8E93;text-align:center;margin-top:1rem;">Baseline: manual spreadsheet tracking. This app replaces multi-field forms with structured input and real-time safety decisions.</p>', unsafe_allow_html=True)