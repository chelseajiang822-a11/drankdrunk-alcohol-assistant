import os
import json
import re
import calendar
import datetime
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from collections import defaultdict

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="DrankDrunk", page_icon="🍸", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #F2F2F7; color: #1C1C1E;
}
.stApp { background-color: #F2F2F7; }

.brand-header { text-align:center; padding:1.5rem 0 0.8rem; }
.brand-title  { font-size:1.9rem; font-weight:700; color:#1C1C1E; letter-spacing:-0.02em; margin-bottom:0.15rem; }
.brand-sub    { font-size:0.72rem; color:#8E8E93; letter-spacing:0.07em; text-transform:uppercase; }

.section-label { font-size:0.7rem; font-weight:600; color:#8E8E93; letter-spacing:0.08em; text-transform:uppercase; margin:1.1rem 0 0.45rem; }

.ios-card { background:#FFFFFF; border-radius:16px; padding:0.1rem 1.1rem; margin-bottom:0.75rem; }

.stat-row  { display:flex; gap:10px; margin-bottom:0.75rem; }
.stat-card { flex:1; background:#FFFFFF; border-radius:14px; padding:0.8rem 0.5rem; text-align:center; }
.stat-label { font-size:0.62rem; color:#8E8E93; font-weight:500; letter-spacing:0.04em; text-transform:uppercase; margin-bottom:0.2rem; }
.stat-value { font-size:1.35rem; font-weight:700; color:#1C1C1E; }

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

/* ── Stats: podium ── */
.podium-row { display:flex; justify-content:center; gap:1.5rem; margin:1rem 0 1.5rem; }
.podium-item { display:flex; flex-direction:column; align-items:center; gap:0.4rem; }
.podium-circle { width:64px; height:64px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.6rem; }
.podium-gold   { background:#FFF3CD; }
.podium-silver { background:#EFEFEF; }
.podium-bronze { background:#FFE8D6; }
.podium-name  { font-size:0.82rem; font-weight:600; color:#1C1C1E; text-align:center; max-width:72px; }
.podium-count { font-size:0.72rem; color:#8E8E93; }

/* ── Stats: ranking list ── */
.rank-item { display:flex; align-items:center; padding:0.65rem 0; border-bottom:0.5px solid #E5E5EA; }
.rank-item:last-child { border-bottom:none; }
.rank-num  { width:28px; font-weight:700; font-size:1rem; color:#C7C7CC; flex-shrink:0; }
.rank-num.gold   { color:#FF9500; }
.rank-num.silver { color:#8E8E93; }
.rank-num.bronze { color:#CD7C54; }
.rank-info { flex:1; margin-left:0.5rem; }
.rank-drink-name { font-weight:600; font-size:0.88rem; color:#1C1C1E; }
.rank-drink-meta { font-size:0.72rem; color:#8E8E93; margin-top:0.1rem; }
.rank-right { text-align:right; }
.rank-units { font-weight:700; font-size:0.9rem; color:#34C759; }

/* ── Segment control ── */
.seg-row { display:flex; background:#E5E5EA; border-radius:10px; padding:3px; margin-bottom:1rem; }
.seg-btn { flex:1; text-align:center; padding:0.35rem 0; border-radius:8px; font-size:0.78rem; font-weight:500; color:#3C3C43; cursor:pointer; transition:all 0.15s; }
.seg-btn.active { background:#FFFFFF; color:#1C1C1E; font-weight:600; box-shadow:0 1px 3px rgba(0,0,0,0.12); }

/* ── Calendar ── */
.cal-wrap { background:#FFFFFF; border-radius:16px; padding:1rem; margin-bottom:0.75rem; }
.cal-title { font-size:1rem; font-weight:600; color:#1C1C1E; text-align:center; margin-bottom:0.8rem; }
.cal-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; }
.cal-dow  { font-size:0.6rem; font-weight:600; color:#8E8E93; text-align:center; padding-bottom:4px; letter-spacing:0.05em; }
.cal-day  { aspect-ratio:1; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:0.72rem; font-weight:500; color:#1C1C1E; position:relative; }
.cal-day.empty { background:transparent; }
.cal-day.today { outline:2px solid #007AFF; outline-offset:-2px; }
.cal-day.has-drink { color:#FFFFFF; font-weight:700; }
.cal-day.level-1 { background:#B7EBCA; color:#1A7A48; }
.cal-day.level-2 { background:#5AC87E; color:#FFFFFF; }
.cal-day.level-3 { background:#34C759; color:#FFFFFF; }
.cal-day.level-4 { background:#1A7A48; color:#FFFFFF; }
.cal-legend { display:flex; align-items:center; gap:6px; justify-content:flex-end; margin-top:8px; font-size:0.65rem; color:#8E8E93; }
.leg-box { width:12px; height:12px; border-radius:3px; }

[data-testid="stTextInput"] input {
    background:#FFFFFF !important; border:0.5px solid #E5E5EA !important;
    border-radius:12px !important; color:#1C1C1E !important;
    font-family:'Inter',sans-serif !important; padding:0.6rem 1rem !important;
}
[data-testid="stTextInput"] input:focus { border-color:#007AFF !important; box-shadow:0 0 0 3px rgba(0,122,255,0.12) !important; }
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

.stDataFrame { border-radius:12px !important; overflow:hidden !important; }
.stWarning   { background:#FFF8E6 !important; border-color:#FF9500 !important; color:#92650A !important; border-radius:12px !important; }
.stInfo      { background:#EAF3FF !important; border-color:#007AFF !important; color:#004EB3 !important; border-radius:12px !important; }
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
if "unit_limit" not in st.session_state:
    st.session_state.unit_limit = 4.0
if "profile" not in st.session_state:
    st.session_state.profile = {"username": "", "bio": "", "avatar_emoji": "🙂", "logged_in": False}


# ── Constants ──
CATEGORY_EMOJI = {"beer":"🍺","wine":"🍷","spirit":"🥃","cocktail":"🍹","mixed":"🍸","ambiguous":"🥤"}
LABEL_MAP = {"continue":"Continue","caution":"Caution","stop":"Stop"}
ICON_MAP  = {"continue":"✅","caution":"⚠️","stop":"🛑"}
DEC_COLOR = {"Continue":"#34C759","Caution":"#FF9500","Stop":"#FF3B30"}

# ── Core helpers ──
def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match: raise ValueError("No JSON object found.")
    return json.loads(match.group(0))

def safe_number(value, default):
    try: return default if (value is None or value == "") else float(value)
    except: return default

def fallback_parse_drink(user_input):
    text = user_input.lower(); drinks = []
    def qty(t):
        if "4" in t or "four" in t: return 4
        if "3" in t or "three" in t or "several" in t: return 3
        if "2" in t or "two" in t or "couple" in t: return 2
        return 1
    q = qty(text)
    if "beer" in text or "pint" in text or "lager" in text:
        drinks.append({"category":"beer","drink_summary":"beer","abv_pct":5,"volume_ml":473 if "pint" in text else (500 if "500" in text else 330),"quantity":q})
    if "wine" in text or "champagne" in text or "prosecco" in text:
        drinks.append({"category":"wine","drink_summary":"wine","abv_pct":12,"volume_ml":250 if "250" in text else 150,"quantity":q})
    if any(w in text for w in ["whiskey","whisky","vodka","rum","gin","tequila","shot"]):
        drinks.append({"category":"spirit","drink_summary":"spirit shot","abv_pct":40,"volume_ml":30,"quantity":q})
    if any(w in text for w in ["mojito","margarita","cocktail","sour","colada","negroni","daiquiri"]):
        drinks.append({"category":"cocktail","drink_summary":"cocktail","abv_pct":12,"volume_ml":150,"quantity":q})
    if not drinks:
        drinks.append({"category":"ambiguous","drink_summary":user_input,"abv_pct":12,"volume_ml":150,"quantity":q})
    cat = "mixed" if len(drinks) > 1 else drinks[0]["category"]
    return {"category":cat,"drink_summary":user_input,"drinks":drinks,"confidence":"medium" if cat != "ambiguous" else "low"}

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
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"system","content":"You are a strict JSON generator. Return only valid JSON with no markdown."},
                  {"role":"user","content":prompt}],
        temperature=0
    )
    return extract_json(resp.choices[0].message.content)

def calculate_total_units(drinks):
    defaults = {"beer":(5,330),"wine":(12,150),"spirit":(40,30),"cocktail":(12,150),"ambiguous":(12,150)}
    total = 0
    for d in drinks:
        cat = str(d.get("category","ambiguous")).lower()
        da,dv = defaults.get(cat,(12,150))
        total += safe_number(d.get("volume_ml"),dv)*(safe_number(d.get("abv_pct"),da)/100)*safe_number(d.get("quantity"),1)/17.7
    return round(total,2)

def make_decision(current_units, prior=0.0, limit=4.0):
    total = round(current_units + prior, 2)
    pct   = total / max(limit, 0.1)
    if pct < 0.5:
        return "continue", total, f"You're at {total} u — well within your {limit} u limit. Stay hydrated."
    elif pct < 0.85:
        return "caution", total, f"You're at {total} u — approaching your {limit} u limit. Consider slowing down."
    else:
        return "stop", total, f"You've reached {total} u — at or over your {limit} u limit. Time to stop."

# ── Stats helpers ──
def filter_history(history, period):
    today = datetime.date.today()
    if period == "All":
        return history
    filtered = []
    for e in history:
        d = e.get("date", str(today))
        try:
            ed = datetime.date.fromisoformat(d)
        except:
            ed = today
        if period == "This Week":
            start = today - datetime.timedelta(days=today.weekday())
            if ed >= start: filtered.append(e)
        elif period == "This Month":
            if ed.year == today.year and ed.month == today.month: filtered.append(e)
        elif period == "This Year":
            if ed.year == today.year: filtered.append(e)
    return filtered

def build_ranking(history):
    counts  = defaultdict(int)
    units   = defaultdict(float)
    types   = {}
    for e in history:
        name = e["drink"]
        counts[name] += 1
        units[name]  += e["units"]
        types[name]   = e.get("type","ambiguous")
    ranking = sorted(counts.keys(), key=lambda n: (-counts[n], -units[n]))
    return [(n, counts[n], round(units[n],2), round(units[n]/counts[n],2), types[n]) for n in ranking]

def build_calendar_html(history, year, month):
    today = datetime.date.today()
    # aggregate units per day
    day_units = defaultdict(float)
    for e in history:
        d = e.get("date", str(today))
        try:
            ed = datetime.date.fromisoformat(d)
        except:
            ed = today
        if ed.year == year and ed.month == month:
            day_units[ed.day] += e["units"]

    max_u = max(day_units.values()) if day_units else 1

    def level(u):
        if u <= 0: return ""
        pct = u / max(max_u, 0.01)
        if pct < 0.25: return "level-1"
        if pct < 0.5:  return "level-2"
        if pct < 0.75: return "level-3"
        return "level-4"

    cal = calendar.monthcalendar(year, month)
    month_name = datetime.date(year, month, 1).strftime("%B %Y")

    dows = "".join(f'<div class="cal-dow">{d}</div>' for d in ["Mo","Tu","We","Th","Fr","Sa","Su"])
    cells = ""
    for week in cal:
        for day in week:
            if day == 0:
                cells += '<div class="cal-day empty"></div>'
            else:
                u = day_units.get(day, 0)
                lv = level(u)
                is_today = (today.year == year and today.month == month and today.day == day)
                cls = f"cal-day {lv} {'today' if is_today else ''} {'has-drink' if lv else ''}".strip()
                tip = f"{u:.1f}u" if u > 0 else str(day)
                cells += f'<div class="{cls}" title="{u:.2f} units">{tip}</div>'

    legend = """
    <div class="cal-legend">
      <span>Less</span>
      <div class="leg-box" style="background:#B7EBCA"></div>
      <div class="leg-box" style="background:#5AC87E"></div>
      <div class="leg-box" style="background:#34C759"></div>
      <div class="leg-box" style="background:#1A7A48"></div>
      <span>More</span>
    </div>"""

    return f"""
    <div class="cal-wrap">
      <div class="cal-title">{month_name}</div>
      <div class="cal-grid">{dows}{cells}</div>
      {legend}
    </div>"""

# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
tab_drink, tab_stats, tab_settings = st.tabs(["🍸 Drink Analyzer", "📊 Stats", "👤 Profile"])

# ───────────────────────────────────────
# Tab 1: Drink Analyzer
# ───────────────────────────────────────
with tab_drink:
    # -- Personal limit setting --
    with st.expander('⚙️ Personal Limit Setting', expanded=False):
        new_limit = st.slider(
            'My daily alcohol unit limit',
            min_value=1.0, max_value=20.0,
            value=float(st.session_state.unit_limit),
            step=0.5, format='%.1f u'
        )
        st.session_state.unit_limit = new_limit
        lim = new_limit
        st.markdown(f"""
        <div style='background:#F2F2F7;border-radius:10px;padding:0.7rem 0.9rem;font-size:0.78rem;color:#3C3C43;margin-top:0.5rem;'>
          <div>🟢 &nbsp;Below 50% of {lim:.1f} u (&lt; {lim*0.5:.1f} u) → <strong>Continue</strong></div>
          <div style='margin-top:0.3rem;'>🟡 &nbsp;50–85% ({lim*0.5:.1f}–{lim*0.85:.1f} u) → <strong>Caution</strong></div>
          <div style='margin-top:0.3rem;'>🔴 &nbsp;85%+ (&gt; {lim*0.85:.1f} u) → <strong>Stop</strong></div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<p class="section-label">Drink Details</p>', unsafe_allow_html=True)

    drink_name = st.text_input("Drink Name", placeholder="e.g. Cheese Milk Cap, Whisky, Red Wine…")

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
                    "category":      parsed.get("drinks",[{}])[0].get("category","ambiguous") if parsed.get("drinks") else "ambiguous",
                    "drink_summary": drink_name,
                    "abv_pct":       abv_pct,
                    "volume_ml":     volume_ml,
                    "quantity":      1
                }]
                cur = calculate_total_units(drinks)
                prior = sum(e["units"] for e in st.session_state.history)
                decision, cumulative, reason = make_decision(cur, prior, st.session_state.unit_limit)

            cat   = drinks[0]["category"]
            emoji = CATEGORY_EMOJI.get(cat,"🥤")
            dec_en = LABEL_MAP[decision]

            st.markdown('<p class="section-label">Result</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="stat-row">
              <div class="stat-card"><div class="stat-label">Type</div><div class="stat-value">{emoji}</div></div>
              <div class="stat-card"><div class="stat-label">This Drink</div><div class="stat-value">{cur} u</div></div>
              <div class="stat-card"><div class="stat-label">Session Total</div><div class="stat-value">{cumulative} u</div></div>
              <div class="stat-card"><div class="stat-label">ABV</div><div class="stat-value" style="font-size:1.1rem">{abv_pct}%</div></div>
            </div>""", unsafe_allow_html=True)
            st.markdown(
                '<p style="font-size:0.68rem;color:#C7C7CC;text-align:right;margin:-6px 0 8px;">1 u = 1 US standard drink (14 g pure alcohol = 17.7 ml)</p>',
                unsafe_allow_html=True
            )

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
                "date":     str(datetime.date.today()),
            })

    # ── Log (inline below analyzer) ──
    st.markdown('<p class="section-label">Session Log</p>', unsafe_allow_html=True)
    if st.session_state.history:
        total_u = round(sum(e["units"] for e in st.session_state.history), 2)
        count   = len(st.session_state.history)
        st.markdown(f"""
        <div class="summary-bar">
          <span>{count} drink{"s" if count!=1 else ""} logged</span>
          <span class="summary-total">Total: {total_u} units</span>
        </div>""", unsafe_allow_html=True)

        items_html = ""
        for i, entry in enumerate(reversed(st.session_state.history)):
            em  = CATEGORY_EMOJI.get(entry["type"],"🥤")
            dc  = DEC_COLOR.get(entry["decision"],"#8E8E93")
            sep = "" if i==len(st.session_state.history)-1 else "border-bottom:0.5px solid #E5E5EA;"
            items_html += f"""
            <div class="drink-item" style="{sep}">
              <div class="drink-icon">{em}</div>
              <div class="drink-info">
                <div class="drink-name">{entry['drink']}</div>
                <div class="drink-meta">{entry['type']} · {entry['ml']}ml · {entry['abv']} · {entry.get('date','')}</div>
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
        <div class="ios-card" style="text-align:center;padding:1.5rem 1rem;color:#C7C7CC;font-size:0.85rem;">
          No drinks logged yet.
        </div>""", unsafe_allow_html=True)

# ───────────────────────────────────────
# Tab 3: Stats
# ───────────────────────────────────────
with tab_stats:
    history = st.session_state.history

    if not history:
        st.markdown("""
        <div class="ios-card" style="text-align:center;padding:2rem 1rem;color:#8E8E93;font-size:0.88rem;">
          No data yet. Log some drinks to see your stats.
        </div>""", unsafe_allow_html=True)
    else:
        # ── Period filter ──
        today = datetime.date.today()
        periods = ["All", "This Week", "This Month", "This Year"]
        if "stats_period" not in st.session_state:
            st.session_state.stats_period = "All"

        period_choice = st.radio(
            "Period", periods, horizontal=True,
            index=periods.index(st.session_state.stats_period),
            label_visibility="collapsed"
        )
        if period_choice != st.session_state.stats_period:
            st.session_state.stats_period = period_choice
            st.rerun()

        filtered = filter_history(history, st.session_state.stats_period)

        if not filtered:
            st.markdown('<div class="ios-card" style="text-align:center;padding:1.5rem;color:#8E8E93;font-size:0.85rem;">No drinks in this period.</div>', unsafe_allow_html=True)
        else:
            ranking = build_ranking(filtered)

            # ── Top 3 podium ──
            st.markdown('<p class="section-label">Top 3</p>', unsafe_allow_html=True)
            podium_classes = ["podium-gold","podium-silver","podium-bronze"]
            medals = ["🥇","🥈","🥉"]
            top3 = ranking[:3]

            podium_html = '<div class="podium-row">'
            for idx, (name, cnt, total_u, avg_u, cat) in enumerate(top3):
                em = CATEGORY_EMOJI.get(cat,"🥤")
                pc = podium_classes[idx]
                medal = medals[idx]
                podium_html += f"""
                <div class="podium-item">
                  <div class="podium-circle {pc}">{medal}</div>
                  <div class="podium-name">{name}</div>
                  <div class="podium-count">{cnt} time{"s" if cnt!=1 else ""}</div>
                </div>"""
            podium_html += "</div>"
            st.markdown(podium_html, unsafe_allow_html=True)

            # ── Full ranking list ──
            st.markdown('<p class="section-label">Full Ranking</p>', unsafe_allow_html=True)
            rank_colors = ["gold","silver","bronze"]
            items_html = ""
            for idx, (name, cnt, total_u, avg_u, cat) in enumerate(ranking):
                em = CATEGORY_EMOJI.get(cat,"🥤")
                rc = rank_colors[idx] if idx < 3 else ""
                sep = "" if idx==len(ranking)-1 else "border-bottom:0.5px solid #E5E5EA;"
                items_html += f"""
                <div class="rank-item" style="{sep}">
                  <div class="rank-num {rc}">{idx+1}</div>
                  <div class="drink-icon" style="width:36px;height:36px;font-size:1.1rem;">{em}</div>
                  <div class="rank-info">
                    <div class="rank-drink-name">{name}</div>
                    <div class="rank-drink-meta">{cnt} time{"s" if cnt!=1 else ""} · {avg_u:.2f} u/drink</div>
                  </div>
                  <div class="rank-right">
                    <div class="rank-units">{total_u} u</div>
                  </div>
                </div>"""
            st.markdown(f'<div class="ios-card">{items_html}</div>', unsafe_allow_html=True)

        # ── Calendar heatmap ──
        st.markdown('<p class="section-label">Calendar</p>', unsafe_allow_html=True)

        cal_col1, cal_col2, cal_col3 = st.columns([1,2,1])
        with cal_col1:
            if st.button("←", key="cal_prev"):
                m = st.session_state.get("cal_month", today.month)
                y = st.session_state.get("cal_year",  today.year)
                if m == 1: st.session_state.cal_month=12; st.session_state.cal_year=y-1
                else:      st.session_state.cal_month=m-1
                st.rerun()
        with cal_col3:
            if st.button("→", key="cal_next"):
                m = st.session_state.get("cal_month", today.month)
                y = st.session_state.get("cal_year",  today.year)
                if m == 12: st.session_state.cal_month=1; st.session_state.cal_year=y+1
                else:       st.session_state.cal_month=m+1
                st.rerun()

        cal_year  = st.session_state.get("cal_year",  today.year)
        cal_month = st.session_state.get("cal_month", today.month)

        cal_html = build_calendar_html(history, cal_year, cal_month)
        st.markdown(cal_html, unsafe_allow_html=True)

        # ── Calendar legend note ──
        st.markdown('<p style="font-size:0.7rem;color:#8E8E93;text-align:center;">Color intensity reflects alcohol units consumed that day.</p>', unsafe_allow_html=True)

# ───────────────────────────────────────
# Tab 3: Profile / Settings
# ───────────────────────────────────────
with tab_settings:
    profile = st.session_state.profile

    AVATAR_OPTIONS = ["🙂","😎","🧑","👩","🧔","🥂","🍻","🎉","🦊","🐼","🌟","💫"]

    if not profile["logged_in"]:
        # ── Login / Sign-up view ──
        st.markdown("""
        <div style="text-align:center;padding:1.5rem 0 0.5rem;">
          <div style="font-size:3.5rem;margin-bottom:0.5rem;">🍸</div>
          <div style="font-size:1.2rem;font-weight:700;color:#1C1C1E;">Welcome to DrankDrunk</div>
          <div style="font-size:0.82rem;color:#8E8E93;margin-top:0.3rem;">Set up your profile to get started</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<p class="section-label">Choose Your Avatar</p>', unsafe_allow_html=True)
        avatar_cols = st.columns(6)
        for i, emo in enumerate(AVATAR_OPTIONS):
            with avatar_cols[i % 6]:
                selected = profile["avatar_emoji"] == emo
                border = "2px solid #007AFF" if selected else "2px solid transparent"
                bg = "#EAF3FF" if selected else "#F2F2F7"
                if st.button(emo, key=f"av_{i}"):
                    st.session_state.profile["avatar_emoji"] = emo
                    st.rerun()

        st.markdown('<p class="section-label">Your Info</p>', unsafe_allow_html=True)
        uname = st.text_input("Username", value=profile["username"], placeholder="e.g. Alex")
        bio   = st.text_input("Bio (optional)", value=profile["bio"], placeholder="e.g. Weekend sipper 🍷")

        if st.button("Save & Sign In", use_container_width=True):
            if not uname.strip():
                st.error("Please enter a username.")
            else:
                st.session_state.profile["username"]  = uname.strip()
                st.session_state.profile["bio"]       = bio.strip()
                st.session_state.profile["logged_in"] = True
                st.rerun()

    else:
        # ── Logged-in profile view ──
        av = profile["avatar_emoji"]
        uname = profile["username"]
        bio   = profile["bio"]
        total_drinks = len(st.session_state.history)
        total_units  = round(sum(e["units"] for e in st.session_state.history), 2)

        # Avatar + name hero
        st.markdown(f"""
        <div style="background:#FFFFFF;border-radius:20px;padding:1.5rem 1rem 1rem;text-align:center;margin-bottom:0.75rem;">
          <div style="font-size:4rem;line-height:1;margin-bottom:0.6rem;">{av}</div>
          <div style="font-size:1.25rem;font-weight:700;color:#1C1C1E;">{uname}</div>
          {"<div style='font-size:0.82rem;color:#8E8E93;margin-top:0.25rem;'>" + bio + "</div>" if bio else ""}
        </div>""", unsafe_allow_html=True)

        # Quick stats
        st.markdown(f"""
        <div class="stat-row">
          <div class="stat-card">
            <div class="stat-label">Drinks Logged</div>
            <div class="stat-value">{total_drinks}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Total Units</div>
            <div class="stat-value">{total_units} u</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Daily Limit</div>
            <div class="stat-value">{st.session_state.unit_limit:.1f} u</div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Edit profile
        st.markdown('<p class="section-label">Edit Profile</p>', unsafe_allow_html=True)
        with st.expander("✏️ Edit Name & Bio"):
            new_uname = st.text_input("Username", value=uname, key="edit_uname")
            new_bio   = st.text_input("Bio", value=bio, key="edit_bio")
            if st.button("Save Changes", key="save_profile"):
                st.session_state.profile["username"] = new_uname.strip() or uname
                st.session_state.profile["bio"]      = new_bio.strip()
                st.rerun()

        with st.expander("🎭 Change Avatar"):
            av_cols = st.columns(6)
            for i, emo in enumerate(AVATAR_OPTIONS):
                with av_cols[i % 6]:
                    if st.button(emo, key=f"chav_{i}"):
                        st.session_state.profile["avatar_emoji"] = emo
                        st.rerun()

        # Divider
        st.markdown('<div style="height:0.5px;background:#E5E5EA;margin:1rem 0;"></div>', unsafe_allow_html=True)

        # Danger zone
        st.markdown('<p class="section-label">Account</p>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🗑  Clear All Data", use_container_width=True):
                st.session_state.history = []
                st.rerun()
        with col_b:
            if st.button("🚪  Sign Out", use_container_width=True):
                st.session_state.profile["logged_in"] = False
                st.session_state.history = []
                st.rerun()

        st.markdown('<p style="font-size:0.7rem;color:#C7C7CC;text-align:center;margin-top:1rem;">DrankDrunk · Educational use only</p>', unsafe_allow_html=True)