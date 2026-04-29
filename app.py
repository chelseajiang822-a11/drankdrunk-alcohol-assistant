import os
import json
import re
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─────────────────────────────────────────────
# Page config & Light-mode iOS-style CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DrankDrunk",
    page_icon="🍸",
    layout="centered"
)

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

.ios-card {
    background: #FFFFFF; border-radius: 16px;
    padding: 0.1rem 1.1rem; margin-bottom: 0.75rem;
}

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

.eval-row   { display:flex; gap:10px; margin-bottom:1rem; }
.eval-card  { flex:1; background:#FFFFFF; border-radius:14px; padding:0.9rem 0.5rem; text-align:center; }
.eval-label { font-size:0.62rem; color:#8E8E93; font-weight:500; letter-spacing:0.04em; text-transform:uppercase; margin-bottom:0.25rem; }
.eval-target { font-size:0.65rem; color:#8E8E93; margin-top:0.2rem; }
.ev-pass { font-size:1.45rem; font-weight:700; color:#34C759; }
.ev-warn { font-size:1.45rem; font-weight:700; color:#FF9500; }
.ev-fail { font-size:1.45rem; font-weight:700; color:#FF3B30; }

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
div[data-testid="stExpander"] { background:#FFFFFF !important; border:0.5px solid #E5E5EA !important; border-radius:12px !important; }
[data-testid="stFileUploadDropzone"] { background:#FFFFFF !important; border:1.5px dashed #C7C7CC !important; border-radius:12px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
  <div class="brand-title">🍸 DrankDrunk</div>
  <div class="brand-sub">饮酒记录 · 智能决策</div>
</div>
""", unsafe_allow_html=True)

st.warning("⚠️ 本工具仅提供估算参考，不构成医疗或驾驶安全建议。")

# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
CATEGORY_EMOJI = {
    "beer": "🍺", "wine": "🍷", "spirit": "🥃",
    "cocktail": "🍹", "mixed": "🍸", "ambiguous": "🥤"
}


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found.")
    return json.loads(match.group(0))


def safe_number(value, default):
    try:
        if value is None or value == "":
            return default
        return float(value)
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
    if any(w in text for w in ["mojito", "margarita", "cocktail", "sour", "colada", "cosmopolitan", "negroni", "daiquiri"]):
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
        abv = safe_number(d.get("abv_pct"), da)
        vol = safe_number(d.get("volume_ml"), dv)
        qty = safe_number(d.get("quantity"), 1)
        total += vol * (abv / 100) * qty / 17.7
    return round(total, 2)


def make_decision(current_units, prior=0.0):
    total = round(current_units + prior, 2)
    if total <= 1.5:
        return "continue", total, f"累计摄入较低（{total} 单位）。保持水分补充，适度饮用。"
    elif total <= 3.0:
        return "caution", total, f"累计摄入中等（{total} 单位）。建议放慢节奏，喝些水。"
    else:
        return "stop", total, f"累计摄入较高（{total} 单位）。建议停止饮酒。"


def run_evaluation(csv_path, use_ai=True):
    df = pd.read_csv(csv_path)
    results = []
    for _, row in df.iterrows():
        ui, ec, eu, ed = row["input"], row["expected_category"], float(row["expected_units"]), row["expected_decision"]
        fb = False
        try:
            parsed = parse_drink_with_ai(ui) if use_ai else fallback_parse_drink(ui)
        except Exception:
            parsed = fallback_parse_drink(ui); fb = True
        drinks = parsed.get("drinks", [])
        if not drinks:
            parsed = fallback_parse_drink(ui); drinks = parsed["drinks"]; fb = True
        pu = calculate_total_units(drinks)
        pd_dec, _, _ = make_decision(pu)
        pc = parsed.get("category", "ambiguous")
        results.append({"input": ui, "expected_category": ec, "pred_category": pc,
                         "cat_correct": pc == ec, "expected_units": eu, "pred_units": pu,
                         "unit_MAE": round(abs(pu - eu), 2), "expected_decision": ed,
                         "pred_decision": pd_dec, "dec_correct": pd_dec == ed,
                         "parser": "fallback" if fb else "AI"})
    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
tab_drink, tab_log, tab_eval = st.tabs(["🍸 饮品分析", "📓 记录", "📊 评估"])

LABEL_MAP = {"continue": "继续", "caution": "注意", "stop": "停止"}
ICON_MAP  = {"continue": "✅", "caution": "⚠️", "stop": "🛑"}
DEC_COLOR = {"继续": "#34C759", "注意": "#FF9500", "停止": "#FF3B30"}

# ───────────────────────────────────────
# Tab 1: Drink Analyzer
# ───────────────────────────────────────
with tab_drink:
    drink_input = st.text_input(
        "输入饮品", placeholder="例如：2 beers and 1 whiskey shot",
        label_visibility="collapsed"
    )

    if st.button("分析饮品", use_container_width=True):
        if not drink_input.strip():
            st.error("请输入饮品描述。")
        else:
            with st.spinner("解析中…"):
                fb = False
                try:
                    parsed = parse_drink_with_ai(drink_input)
                except Exception:
                    parsed = fallback_parse_drink(drink_input); fb = True
                drinks = parsed.get("drinks", [])
                if not drinks:
                    parsed = fallback_parse_drink(drink_input); drinks = parsed["drinks"]; fb = True
                cur = calculate_total_units(drinks)
                prior = sum(e["units"] for e in st.session_state.history)
                decision, cumulative, reason = make_decision(cur, prior)

            emoji = CATEGORY_EMOJI.get(parsed.get("category", "ambiguous"), "🥤")
            conf_cn = {"high": "高", "medium": "中", "low": "低"}.get(parsed.get("confidence", "medium"), "中")
            dec_cn = LABEL_MAP[decision]

            st.markdown('<p class="section-label">本次结果</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="stat-row">
              <div class="stat-card"><div class="stat-label">类型</div><div class="stat-value">{emoji}</div></div>
              <div class="stat-card"><div class="stat-label">本次单位</div><div class="stat-value">{cur}</div></div>
              <div class="stat-card"><div class="stat-label">累计单位</div><div class="stat-value">{cumulative}</div></div>
              <div class="stat-card"><div class="stat-label">置信度</div><div class="stat-value" style="font-size:1rem">{conf_cn}</div></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(
                f'<div class="decision-{decision}"><strong>{ICON_MAP[decision]} {dec_cn}</strong>　{reason}</div>',
                unsafe_allow_html=True
            )

            if fb:
                st.info("AI 解析不可用，已切换至规则备用解析器。")

            with st.expander("查看解析明细"):
                st.dataframe(pd.DataFrame(drinks), use_container_width=True)

            st.session_state.history.append({
                "饮品": drink_input, "类型": parsed.get("category", "ambiguous"),
                "units": cur, "决策": dec_cn,
                "解析器": "备用" if fb else "AI"
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
          <span>共 {count} 条记录</span>
          <span class="summary-total">累计：{total_u} 单位</span>
        </div>
        """, unsafe_allow_html=True)

        items_html = ""
        for i, entry in enumerate(reversed(st.session_state.history)):
            em  = CATEGORY_EMOJI.get(entry["类型"], "🥤")
            dc  = DEC_COLOR.get(entry["决策"], "#8E8E93")
            sep = "" if i == len(st.session_state.history) - 1 else "border-bottom:0.5px solid #E5E5EA;"
            items_html += f"""
            <div class="drink-item" style="{sep}">
              <div class="drink-icon">{em}</div>
              <div class="drink-info">
                <div class="drink-name">{entry['饮品']}</div>
                <div class="drink-meta">{entry['类型']} · {entry['解析器']}解析</div>
              </div>
              <div class="drink-right">
                <div class="drink-units">{entry['units']} u</div>
                <div class="drink-dec" style="color:{dc}">{entry['决策']}</div>
              </div>
            </div>"""

        st.markdown(f'<div class="ios-card">{items_html}</div>', unsafe_allow_html=True)

        if st.button("清空记录"):
            st.session_state.history = []
            st.rerun()
    else:
        st.markdown("""
        <div class="ios-card" style="text-align:center;padding:2rem 1rem;color:#8E8E93;font-size:0.88rem;">
          暂无记录，前往「饮品分析」开始记录
        </div>""", unsafe_allow_html=True)

    st.markdown('<p style="font-size:0.72rem;color:#8E8E93;text-align:center;margin-top:1rem;">对比基准：手动电子表格。本应用通过自然语言输入替代多字段表单，提升效率。</p>', unsafe_allow_html=True)

# ───────────────────────────────────────
# Tab 3: Evaluation
# ───────────────────────────────────────
with tab_eval:
    st.markdown('<p class="section-label">评估配置</p>', unsafe_allow_html=True)
    eval_csv    = st.file_uploader("上传 evaluation_cases.csv", type=["csv"])
    use_ai_eval = st.checkbox("使用 AI 解析（取消勾选 = 仅规则备用解析）", value=True)

    if st.button("运行评估", use_container_width=True):
        if eval_csv is None:
            st.error("请先上传 evaluation_cases.csv。")
        else:
            import tempfile, os as _os
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(eval_csv.read()); tmp_path = tmp.name

            with st.spinner("评估中，请稍候…"):
                rdf = run_evaluation(tmp_path, use_ai=use_ai_eval)
            _os.unlink(tmp_path)

            cat_acc = round(rdf["cat_correct"].mean() * 100, 1)
            mae     = round(rdf["unit_MAE"].mean(), 3)
            dec_acc = round(rdf["dec_correct"].mean() * 100, 1)

            def ev_cls(v, ok, warn):
                return "ev-pass" if v >= ok else ("ev-warn" if v >= warn else "ev-fail")

            st.markdown('<p class="section-label">汇总指标</p>', unsafe_allow_html=True)
            mae_cls = "ev-pass" if mae <= 0.5 else ("ev-warn" if mae <= 1.0 else "ev-fail")
            st.markdown(f"""
            <div class="eval-row">
              <div class="eval-card">
                <div class="eval-label">分类准确率</div>
                <div class="{ev_cls(cat_acc,90,75)}">{cat_acc}%</div>
                <div class="eval-target">目标 ≥ 90%</div>
              </div>
              <div class="eval-card">
                <div class="eval-label">单位 MAE</div>
                <div class="{mae_cls}">{mae}</div>
                <div class="eval-target">目标 ≤ 0.5</div>
              </div>
              <div class="eval-card">
                <div class="eval-label">决策准确率</div>
                <div class="{ev_cls(dec_acc,90,75)}">{dec_acc}%</div>
                <div class="eval-target">目标 ≥ 90%</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<p class="section-label">逐条结果</p>', unsafe_allow_html=True)
            disp = rdf[["input","expected_category","pred_category","cat_correct",
                         "expected_units","pred_units","unit_MAE",
                         "expected_decision","pred_decision","dec_correct"]].rename(
                columns={"cat_correct":"cat✓","dec_correct":"dec✓"})
            st.dataframe(disp, use_container_width=True)

            st.download_button("⬇ 下载完整结果 CSV",
                               data=rdf.to_csv(index=False).encode(),
                               file_name="eval_results.csv", mime="text/csv")