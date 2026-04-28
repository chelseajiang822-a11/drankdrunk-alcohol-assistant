import os
import json
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


def parse_drink_with_ai(user_input):
    prompt = f"""
You are an alcohol intake parsing assistant.

Convert the user's natural-language drink input into valid JSON only.

Use these assumptions when information is missing:
- beer: 330ml, 5% ABV
- wine glass: 150ml, 12% ABV
- spirit shot: 30ml, 40% ABV
- cocktail: 150ml, 12% ABV
- "couple" means 2
- "several" means 3

Return only this JSON format:
{{
  "category": "beer/wine/spirit/cocktail/mixed/ambiguous",
  "drink_summary": "short summary",
  "abv_pct": number,
  "volume_ml": number,
  "quantity": number,
  "confidence": "high/medium/low"
}}

User input: {user_input}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You return only valid JSON. No extra text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    return json.loads(content)


def calculate_units(abv_pct, volume_ml, quantity):
    pure_alcohol_ml = volume_ml * (abv_pct / 100) * quantity
    units = pure_alcohol_ml / 17.7
    return round(units, 2)


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
        try:
            parsed = parse_drink_with_ai(drink_input)

            units = calculate_units(
                parsed["abv_pct"],
                parsed["volume_ml"],
                parsed["quantity"]
            )

            decision, reason = make_decision(units)

            st.divider()
            st.subheader("Result")

            col1, col2, col3 = st.columns(3)
            col1.metric("Category", parsed["category"])
            col2.metric("Alcohol Units", units)
            col3.metric("Decision", decision.upper())

            st.write("**Drink Summary:**", parsed["drink_summary"])
            st.write("**Estimated ABV:**", f"{parsed['abv_pct']}%")
            st.write("**Estimated Volume:**", f"{parsed['volume_ml']} ml")
            st.write("**Quantity:**", parsed["quantity"])
            st.write("**Confidence:**", parsed["confidence"])
            st.info(reason)

            st.session_state.history.append({
                "input": drink_input,
                "category": parsed["category"],
                "units": units,
                "decision": decision
            })

        except Exception as e:
            st.error("The app could not parse this input. Please try a more specific description.")
            st.write("Error:", e)


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
    "Baseline: manual spreadsheet tracking. "
    "Compared with the baseline, this app reduces user effort by allowing natural-language input, "
    "automatic drink classification, estimated alcohol units, and a real-time recommendation."
)