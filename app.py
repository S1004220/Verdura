import streamlit as st
import json
from PIL import Image
import os
import requests

# --- OpenRouter OpenAI Client Setup ---
from openai import OpenAI

# Load OpenRouter API key securely
os.environ["OPENAI_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
client = OpenAI(base_url="https://openrouter.ai/api/v1")

# Load Trefle API token
TREFLE_TOKEN = st.secrets["TREFLE_TOKEN"]

# Cache plant database loading
@st.cache_data
def load_plant_db():
    with open("plant_db.json", "r") as f:
        return json.load(f)
plant_db = load_plant_db()

# Page setup
st.set_page_config(page_title="Verdura – Smart Plant Care App", layout="wide")
st.title("🌿 Verdura – Smart Plant Care App")

# Sidebar navigation
page = st.sidebar.radio("Select a feature:", [
    "Local Plant Database",
    "Trefle Plant Search",
    "AI Plant Health Diagnostics",
    "Ask an Expert Chatbot"
])

# ---------- Local Plant DB Lookup ----------
if page == "Local Plant Database":
    st.header("📚 Local Plant Database Lookup")
    plant_name = st.text_input("Enter a plant name (e.g., Monstera, Snake Plant, Succulent):")
    if plant_name:
        care_info = plant_db.get(plant_name.strip().title())
        if care_info:
            st.success(f"Care instructions for **{plant_name.title()}**")
            st.write(f"💧 Water: {care_info['water']}")
            st.write(f"🌞 Light: {care_info['light']}")
            st.write(f"🌿 Fertilizer: {care_info['fertilizer']}")
        else:
            st.error("Plant not found in local database.")

# ---------- Trefle Plant Search ----------
elif page == "Trefle Plant Search":
    st.header("🔎 Search Plants via Trefle.io API")
    query = st.text_input("Enter plant name to search:")
    
    if query:
        st.info("Searching Trefle database...")
        url = "https://trefle.io/api/v1/plants/search"
        params = {"token": TREFLE_TOKEN, "q": query}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            plants = data.get("data", [])
            if plants:
                for plant in plants[:5]:  # Show top 5 results
                    st.subheader(plant.get("common_name") or "Unnamed Plant")
                    st.write(f"Scientific Name: {plant.get('scientific_name', 'N/A')}")
                    st.write(f"Family: {plant.get('family', 'N/A')}")
                    if plant.get("image_url"):
                        st.image(plant["image_url"], width=200)
                    st.markdown("---")
            else:
                st.warning("No plants found for the query.")
        except Exception as e:
            st.error(f"Error calling Trefle API: {e}")

# ---------- AI Health Diagnostics ----------
elif page == "AI Plant Health Diagnostics":
    st.header("🧠 AI Plant Health Diagnostics")
    uploaded_file = st.file_uploader("Upload a photo of a plant showing symptoms", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Plant Photo", use_column_width=True)
        st.info("Analyzing photo (simulated)...")
        
        # TODO: Replace this with your actual AI call (or backend integration)
        # For now, showing static response:
        st.success("Diagnosis: No visible disease detected. Your plant looks healthy!")

# ---------- Expert Chatbot ----------
elif page == "Ask an Expert Chatbot":
    st.header("👩‍🌾 Ask Verdura Expert Chatbot")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You are a helpful plant care expert."}
        ]

    # Display chat messages
    for message in st.session_state.chat_history[1:]:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

    user_input = st.chat_input("Ask your plant care question...")
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Verdura is thinking..."):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-3.5-turbo",
                    messages=st.session_state.chat_history,
                    max_tokens=400,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content
            except Exception as e:
                answer = f"⚠️ Error: {e}"

        # Append assistant response and display
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

# Footer
st.markdown(
    """
    ---
    <small>Verdura © 2024 – Smart Plant Care App built with Streamlit & OpenRouter API</small>
    """,
    unsafe_allow_html=True,
)
