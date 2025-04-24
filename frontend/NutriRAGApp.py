import streamlit as st
import requests

st.set_page_config(page_title="NutriBot 🍽️", page_icon="🥦")
st.title("🥦 NutriBot: Your Nutrition Assistant")

st.caption("Ask for healthy meal suggestions based on your ingredients and goals.")

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! What are your ingredients and your nutrition goal today?"}]

# Display past messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input section
with st.chat_message("user"):
    with st.form("user_input_form", clear_on_submit=True):
        ingredients = st.text_input("Ingredients you have (comma-separated)", placeholder="e.g., chicken, broccoli, rice")
        goal = st.text_input("Your nutrition or fitness goal", placeholder="e.g., high protein, weight loss")
        allergies = st.text_input("Any allergies (optional)", placeholder="e.g., peanuts, gluten")
        submitted = st.form_submit_button("Ask NutriBot")

if submitted:
    preferences = [i.strip() for i in ingredients.split(",") if i.strip()]
    allergy_list = [a.strip() for a in allergies.split(",") if a.strip()]

    user_prompt = f"I have {', '.join(preferences)}. My goal is {goal}."
    if allergy_list:
        user_prompt += f" I am allergic to {', '.join(allergy_list)}."

    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    st.chat_message("user").write(user_prompt)

    try:
        # payload = {
        #     "goal": goal,
        #     "preferences": preferences,
        #     "allergies": allergy_list
        # }

        payload = {
            "query": user_prompt
        }

        response = requests.post("http://localhost:8000/recommend", json=payload)
        if response.status_code == 200:
            result = response.json()
            reply = f"🥗 Here's a suggestion based on your input:\n\n{result.get('markdown_response', '')}"
        else:
            reply = f"❌ Error from backend: {response.status_code}"
    except Exception as e:
        reply = f"⚠️ Failed to connect to backend: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)

# Footer
st.markdown("---")
st.markdown("💡 Powered by RAG and LLM magic for nutrition guidance.")
