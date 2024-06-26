import os
import openai
import streamlit as st
import pandas as pd
config_data = {
        "api_base": "https://openai-external-instance-02.openai.azure.com/",
        "api_key": "b6a3ec1c8f1048ce89d6199e3c660893",
        "engine": "gpt-4-32k"
    }
# Initialize
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
    

    openai.api_type = "azure"
    openai.api_base = config_data['api_base']
    openai.api_version = "2023-07-01-preview"
    openai.api_key = config_data['api_key']

    os.environ["OPENAI_API_TYPE"] = openai.api_type
    os.environ["OPENAI_API_VERSION"] = openai.api_version
    os.environ["OPENAI_API_BASE"] = openai.api_base
    os.environ["OPENAI_API_KEY"] = openai.api_key
    os.environ["AZURE_OPENAI_ENDPOINT"] = openai.api_base

# Display chat messages from history on app rerun
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# React to user input
if prompt := st.chat_input("What do you want to ask your assistant today?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Send chat to openai
    chat_completion = openai.chat.completions.create(
        messages=st.session_state.messages,
        model=config_data['engine']
    )
    # Display chatgpt response in chat message container
    response = chat_completion.choices[0].message.content
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})