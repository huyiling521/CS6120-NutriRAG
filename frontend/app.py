import requests
import streamlit as st

# Sidebar: name input
with st.sidebar:
    your_name = st.text_input("What's your name?")
    st.markdown("[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)")
    st.markdown("[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)")

# Title with optional name and credit
if your_name:
    st.title(f"💬 Hi there, {your_name}!")
else:
    st.title("💬 My Very Own Chatbot")

st.subheader("🤖 Created by Yiling")

# Description
st.caption("🚀 A Streamlit chatbot powered by a local GPU-based LLaMA model via Ollama")

# Initialize chat session
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display message history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input & response
if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # 向 FastAPI 后端发送 POST 请求
        payload = {
            "goal": prompt,  # 简化处理：用用户输入作为 "goal"
            "preferences": [],
            "allergies": []
        }

        response = requests.post("http://localhost:8000/recommend", json=payload)

        if response.status_code == 200:
            result = response.json()
            reply = f"✅ 推荐成功：{result}"
        else:
            reply = f"❌ 后端返回错误 {response.status_code}"
    except Exception as e:
        reply = f"⚠️ 请求失败：{e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)

# Footer note
st.markdown("<br><hr style='margin-top:30px;'><p style='font-size:0.8em; color:gray;'>🔧 This chatbot is running on a locally served model via Ollama in Docker.</p>", unsafe_allow_html=True)
