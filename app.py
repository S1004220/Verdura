import streamlit as st
import json
from PIL import Image
import openai

# Load plant database once
@st.cache_data
def load_plant_db():
    with open("plant_db.json") as f:
        return json.load(f)

plant_db = load_plant_db()

# Set OpenAI API key from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# App Configuration
st.set_page_config(page_title="Plant Guardian – Smart Plant Care App", layout="wide")

st.title("🌿 Plant Guardian – Smart Plant Care App")

# Sidebar navigation
page = st.sidebar.selectbox("Select a feature", ["Plant Database", "AI Health Diagnostics", "Expert Chatbot"])

# --- Plant Database ---
if page == "Plant Database":
    st.header("📚 Plant Database Lookup")
    plant_name = st.text_input("Enter plant name to get care information (e.g. 'Monstera')")
    if plant_name:
        plant_info = plant_db.get(plant_name.strip())
        if plant_info:
            st.subheader(f"Care instructions for {plant_name.title()}:")
            st.write(f"💧 Watering: {plant_info['water']}")
            st.write(f"🌞 Light: {plant_info['light']}")
            st.write(f"🌿 Fertilizing: {plant_info['fertilizer']}")
        else:
            st.error("Plant not found in the database.")

# --- AI Health Diagnostics ---
elif page == "AI Health Diagnostics":
    st.header("🧠 AI Plant Health Diagnostic")
    uploaded_file = st.file_uploader("Upload a photo of your plant showing symptoms", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Plant Photo", use_column_width=True)
        
        # Placeholder for AI diagnosis
        # In production, send img to your ML model API and parse result
        st.info("Analyzing photo...")
        
        # Simulated response
        st.success("Diagnosis: No disease detected. Your plant looks healthy!")

# --- Expert Chatbot ---
elif page == "Expert Chatbot":
    st.header("👩‍🌾 Ask a Plant Expert")
    
    if "history" not in st.session_state:
        st.session_state.history = []
    
    user_input = st.text_input("Type your question about plant care here")
    
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        
        # Prepare messages for OpenAI chat completion
        messages = [{"role": "system", "content": "You are a helpful plant care expert."}]
        messages.extend(st.session_state.history)
        
        with st.spinner("Getting expert advice..."):
            from openai import OpenAI

            client = OpenAI()  # This will use your environment variable or st.secrets for the API key
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
       
            )
        answer = response.choices[0].message.content
        st.session_state.history.append({"role": "assistant", "content": answer})
        
        # Display chat history in reverse order (latest first)
        for chat in reversed(st.session_state.history):
            if chat["role"] == "user":
                st.markdown(f"**You:** {chat['content']}")
            else:
                st.markdown(f"**Expert:** {chat['content']}")
