import streamlit as st
import openai
import json
from datetime import datetime

# Configure OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Page config
st.set_page_config(page_title="Prompt Integrity Checker", layout="centered")

st.title("🧠 Prompt Integrity Checker (Lite Demo)")
st.markdown("Evaluate your prompt for bias, framing, and cognitive clarity.")

# User input
user_prompt = st.text_area("Enter your prompt (e.g., policy memo, HR question)", height=150)

# Set tolerance threshold
tolerance_threshold = st.slider("Set bias tolerance threshold (0 = strict, 10 = lenient)", 0, 10, 5)

# Initialize result container
result = {}

if st.button("Analyze Prompt"):
    with st.spinner("Analyzing prompt..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI prompt evaluation assistant. For the input below, do the following: (1) Score for cognitive bias (confirmation bias, emotional skew, framing assumptions) on a scale of 0-10; (2) Provide SHAP-style text explanations of bias markers; (3) Suggest 2 alternate framings."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )

        content = response.choices[0].message.content

        result = {
            "original_prompt": user_prompt,
            "bias_analysis": content,
            "timestamp": datetime.now().isoformat()
        }

        st.subheader("🔍 Bias Analysis & Attribution")
        st.markdown(content)

        if "bias score" in content.lower():
            score_line = [line for line in content.split("\n") if "bias score" in line.lower()]
            try:
                score_val = int(''.join(filter(str.isdigit, score_line[0])))
                if score_val > tolerance_threshold:
                    st.warning("⚠️ Prompt exceeds your bias tolerance threshold.")
                else:
                    st.success("✅ Prompt is within acceptable tolerance.")
            except:
                pass

# Log download
if result:
    json_log = json.dumps(result, indent=2)
    st.download_button(
        label="Download Audit Log (JSON)",
        data=json_log,
        file_name=f"prompt_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
