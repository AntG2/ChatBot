import os
import openai
import streamlit as st
config_data = {
        "api_base": "https://openai-external-instance-02.openai.azure.com/",
        "api_key": st.secrets["OPENAI_API_KEY"],
        "engine": "gpt-4-32k"
    }
# Initialize
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a context classifier."}]

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

def tag_conversation(question):
    # Use OpenAI to determine the topic of the question
    response = openai.chat.completions.create(
        model=config_data["engine"],
        messages=[
            {"role": "user", "content": f"Generate keywords that summarizes the following: '{question}'"}
        ],
        max_tokens=15
    )
    
    topic = response.choices[0].message.content.strip()
    return topic

def get_keywords(question):
    # Add the new question to the conversation history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Formulate the prompt with context
    prompt = f"Reconstruct the following user statement or question '{question}' in the context of the following conversation history: {st.session_state.messages[1:]}."
    
    # Call the OpenAI API
    response = openai.chat.completions.create(
        model=config_data["engine"],
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    
    # Extract the keywords from the response
    reconstructed = response.choices[0].message.content.strip()
    
    # Tag the current question
    topic = tag_conversation(reconstructed)

    reconstructed = (reconstructed + "\n\n" + topic)
    # Add the generated keywords and topic to the conversation history
    st.session_state.messages.append({"role": "assistant", "content": reconstructed})
    
    return reconstructed

# React to user input
if prompt := st.chat_input("What do you want to ask your assistant today?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Send chat to openai
    keyword = get_keywords(prompt)
    # Display chatgpt response in chat message container
    with st.chat_message("assistant"):
        st.markdown(keyword)
