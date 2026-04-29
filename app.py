import os
import json
import re
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="DrankDrunk Alcohol Decision Assistant",
    page_icon="🍸",
    layout="centered"
)

st.title("🍸 DrankDrunk")
st.subheader("AI Alcohol Intake Decision Assistant")

st.write(
    "Enter a drink description in natural language. "
    "The app estimates alcohol intake and gives a simple safety recommendation."
)

st.warning(
    "This tool provides rough educational estimates only. "
    "It is not medical, legal, or driving-safety advice."
)

if "history" not in st.session_state:
    st.session_state.history = []


def extract_json(text):
    """Extract JSON object from model output."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output.")
    return json.loads(match.group(0))


def fallback_parse_drink(user_input):
    """Rule-based fallback parser for reliability."""
    text = user_input.lower()
    drinks = []

    def get_quantity(word):
        if "4" in word or "four" in word:
            return 4
        if "3" in word or "three" in word or "several" in word:
            return 3
        if "2" in word or "two" in word or "couple" in word:
            return 2
        return 1

    if "beer" in text:
        drinks.append({
            "category": "beer",
            "drink_summary": "beer",
            "abv_pct": 5,
            "volume_ml": 330,
            "quantity": get_quantity(text)
        })

    if "wine" in text or "champagne" in text:
        drinks.append({
            "category": "wine",
            "drink_summary": "wine",
            "abv_pct": 12,
            "volume_ml": 150,
            "quantity": get_quantity(text)
        })

    if "whiskey" in text or "vodka" in text or "rum" in text or "shot" in text:
        drinks.append({
            "category": "spirit",
            "drink_summary": "spirit shot",
            "abv_pct": 40,
            "volume_ml": 30,
            "quantity": get_quantity(text)
        })

    if "mojito" in text or "margarita" in text or "cocktail" in text:
        drinks.append({
            "category": "cocktail",
            "drink_summary": "cocktail",
            "abv_pct": 12,
            "volume_ml": 150,
            "quantity": get_quantity(text)
        })

    if not drinks:
        drinks.append({
            "category": "ambiguous",
            "drink_summary": user_input,
            "abv_pct": 12,
            "volume_ml": 150,
            "quantity": get_quantity(text)
        })

    category = "mixed" if len(drinks) > 1 else drinks[0]["category"]

    return {
        "category": category,
        "drink_summary": user_input,
        "drinks": drinks,
        "confidence": "medium" if category != "ambiguous" else "low"
    }


def parse_drink_with_ai(user_input):
    prompt = f"""
You are an alcohol intake parsing assistant.

Convert the user's natural-language drink input into valid JSON only.

Important rules:
- Return JSON only. No markdown. No explanation.
- If multiple drink types are mentioned, category must be "mixed".
- Split multiple drinks into a drinks list.
- Estimate missing information using common default assumptions.
- "couple" means 2.
- "several" means 3.

Default assumptions:
- beer: 330ml, 5% ABV
- wine glass: 150ml, 12% ABV
- spirit shot: 30ml, 40% ABV
- cocktail: 150ml, 12% ABV

Return exactly this structure:
{{
  "category": "beer/wine/spirit/cocktail/mixed/ambiguous",
  "drink_summary": "short summary",
  "drinks": [
    {{
      "category": "beer/wine/spirit/cocktail/ambiguous",
      "drink_summary": "short summary",
      "abv_pct": 5,
      "volume_ml": 330,
      "quantity": 1
    }}
  ],
  "confidence": "high/medium/low"
}}

User input: {user_input}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a strict JSON generator. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    return extract_json(content)


def calculate_units_for_drink(abv_pct, volume_ml, quantity):
    pure_alcohol_ml = volume_ml * (abv_pct / 100) * quantity
    units = pure_alcohol_ml / 17.7
    return round(units, 2)


def calculate_total_units(drinks):
    total = 0
    for drink in drinks:
        total += calculate_units_for_drink(
            float(drink["abv_pct"]),
            float(drink["volume_ml"]),
            float(drink["quantity"])
        )
    return round(total, 2)


def make_decision(units):
    if units <= 1.5:
        return "continue", "Your estimated intake is relatively low. Continue carefully and stay hydrated."
    elif units <= 3.0:
        return "caution", "Your intake is increasing. Consider slowing down, drinking water, and avoiding more alcohol."
    else:
        return "stop", "Your estimated intake is high. It is safer to stop drinking alcohol for now."


drink_input = st.text_input(
    "What did you drink?",
    placeholder="Example: 2 beers and 1 whiskey shot"
)

if st.button("Analyze Drink"):
    if not drink_input.strip():
        st.error("Please enter a drink description.")
    else:
        used_fallback = False

        try:
            parsed = parse_drink_with_ai(drink_input)
        except Exception:
            parsed = fallback_parse_drink(drink_input)
            used_fallback = True

        units = calculate_total_units(parsed["drinks"])
        decision, reason = make_decision(units)

        st.divider()
        st.subheader("Result")

        col1, col2, col3 = st.columns(3)
        col1.metric("Category", parsed["category"])
        col2.metric("Alcohol Units", units)
        col3.metric("Decision", decision.upper())

        st.write("**Drink Summary:**", parsed["drink_summary"])
        st.write("**Confidence:**", parsed["confidence"])

        if used_fallback:
            st.info("AI parsing was unavailable or returned invalid JSON, so the app used a rule-based fallback parser.")

        st.write("**Parsed Drinks:**")
        drinks_df = pd.DataFrame(parsed["drinks"])
        st.dataframe(drinks_df, use_container_width=True)

        st.info(reason)

        st.session_state.history.append({
            "input": drink_input,
            "category": parsed["category"],
            "units": units,
            "decision": decision,
            "parser": "fallback" if used_fallback else "AI"
        })


st.divider()
st.subheader("Lifestyle Log")

if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df, use_container_width=True)

    total_units = history_df["units"].sum()
    st.metric("Total Estimated Units This Session", round(total_units, 2))
else:
    st.write("No drinks logged yet.")


st.divider()
st.subheader("Baseline Comparison")

st.write(
    "Baseline: manual spreadsheet tracking. Compared with the baseline, this app reduces user effort "
    "by allowing natural-language input, automatic drink classification, estimated alcohol units, "
    "and a real-time recommendation."
)