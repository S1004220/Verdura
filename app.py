import streamlit as st
import json
from PIL import Image
import os

# --------- Chatbot Setup (OpenRouter) -----------
from openai import OpenAI

# Read OpenRouter API key
os.environ["OPENAI_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
client = OpenAI(base_url="https://openrouter.ai/api/v1")

# --------- Plant DB Loader ------------
@st.cache_data
def load_plant_db():
    with open("plant_db.json") as f:
        return json.load(f)
plant_db = load_plant_db()

# ---- UI & Routing ----
st.set_page_config(page_title="Verdura – Smart Plant Care App", layout="wide")
st.title("🌿 Verdura – Smart Plant Care App")

pages = ["Plant Database", "Plant Health Diagnostics", "Ask an Expert"]
page = st.sidebar.radio("Choose a feature", pages)
st.sidebar.markdown("---")
st.sidebar.info("Made with OpenRouter, Streamlit & 💚 by Verdura!")

# --------- Plant Database Feature --------------
if page == "Plant Database":
    st.header("📚 Plant Database Lookup")
    name = st.text_input(
        "Enter plant name (e.g., Monstera, Snake Plant, Succulent):"
    )
    if name:
        plant = plant_db.get(name.strip())
        if plant:
            st.success(f"🌱 **{name.title()}** Care")
            st.write(f"**💧 Water:** {plant['water']}")
            st.write(f"**🌞 Light:** {plant['light']}")
            st.write(f"**🌿 Fertilizer:** {plant['fertilizer']}")
        else:
            st.error("Plant not found! Try Monstera, Snake Plant, Succulent.")

# --------- AI Plant Health Diagnostics --------------
elif page == "Plant Health Diagnostics":
    st.header("🧠 AI Plant Health Diagnostics")
    uploaded = st.file_uploader("Upload photo showing plant symptoms", type=["jpg", "jpeg", "png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="Uploaded Plant", width=320)
        st.write("Analyzing (simulated)...")
        # Here you would send image to your backend API!
        st.success("Prediction: No visible disease detected. Your plant looks healthy!")
        st.info("Tip: Connect your own ML model/service for real-time diagnosis.")

# --------- Ask an Expert Chatbot --------------
elif page == "Ask an Expert":
    st.header("👩‍🌾 Verdura Expert Chatbot")

    if "history" not in st.session_state:
        st.session_state.history = [
            {"role": "system", "content": "You are a helpful plant care expert providing actionable, concise advice."}
        ]

    def show_chat_history(history):
        for chat in history[1:]:  # skip the system prompt
            is_user = chat["role"] == "user"
            st.chat_message("user" if is_user else "assistant").write(chat["content"])

    show_chat_history(st.session_state.history)

    user_input = st.chat_input("Ask about your plant, care issues, or tips!")
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.spinner("Expert is thinking..."):
            try:
                response = client.chat.completions.create(
                    model="deepseek/deepseek-r1-0528:free",
                    messages=st.session_state.history,
                    max_tokens=400,
                    temperature=0.7
                )
                assistant_reply = response.choices[0].message.content
            except Exception as e:
                assistant_reply = f"Error: {e}"
            st.session_state.history.append({"role": "assistant", "content": assistant_reply})
            st.rerun()  # Refresh chat

# --------- Footer -----------
st.markdown(
    """
    ---
    <small>
    Verdura © 2024 — Smart plants, thriving lives.  
    <br>
    Powered by Streamlit & OpenRouter.
    </small>
    """,
    unsafe_allow_html=True
)
