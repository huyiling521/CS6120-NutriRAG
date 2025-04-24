import streamlit as st
import requests
import os

POST_URL = 'http://app:8000/'

st.set_page_config(page_title="NutriBot 🍽️", page_icon="🥦")
st.title("🥦 NutriBot: Your Nutrition Assistant")

st.caption("Ask me anything about healthy cooking, recipes, or nutritional info!")

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! How can I help you with your healthy eating today?"}]

# Display past messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Send user prompt to backend
    try:
        payload = {
            "query": prompt  # Use the user's full input as the query
        }

        # --- Make the API Call ---
        # Display a thinking indicator with placeholder
        assistant_placeholder = st.chat_message("assistant").empty()

        with assistant_placeholder.container():
            with st.spinner("NutriBot is thinking..."):
                response = requests.post(f"{POST_URL}/recommend", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    reply = result.get('markdown_response', 'Sorry, I could not process your request.')
                elif response.status_code == 422:
                    reply = f"❌ Input Error: {response.json().get('detail', 'Invalid input')}"
                else:
                    reply = f"❌ Error from backend: {response.status_code} - {response.text}"

        # Save & render assistant reply
        st.session_state.messages.append({"role": "assistant", "content": reply})
        assistant_placeholder.markdown(reply)

    except requests.exceptions.RequestException as e:
        reply = f"⚠️ Could not connect to the NutriBot backend: {e}. Please ensure it's running."
    except Exception as e:
        reply = f"⚠️ An unexpected error occurred: {e}"


# Footer
st.markdown("---")
st.markdown("💡 Powered by RAG and LLM magic for nutrition guidance.")
