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

def update_context():
    # Concatenate the conversation history
    conversation = "\n".join([f"{item['role']}: {item['content']}" for item in st.session_state.messages[1:]])
    
    # Use OpenAI to determine the context of the conversation
    response = openai.chat.completions.create(
        model=config_data["engine"],
        messages=[
            {"role": "system", "content": "You are a context classifier."},
            {"role": "user", "content": f"Summarize the context of the following conversation: {conversation}"}
        ],
        max_tokens=50
    )
    
    context_summary = response.choices[0].message.content.strip()
    return context_summary

def tag_conversation(question):
    # Use OpenAI to determine the topic of the question
    response = openai.chat.completions.create(
        model=config_data["engine"],
        messages=[
            {"role": "system", "content": "You are a context classifier."},
            {"role": "user", "content": f"What is the main topic of the following question? '{question}'"}
        ],
        max_tokens=10
    )
    
    topic = response.choices[0].message.content.strip()
    return topic

def get_keywords_and_relevant_conversations(question):
    # Add the new question to the conversation history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Update context with the current conversation history
    context_summary = update_context()
    
    # Formulate the prompt with context
    prompt = f"Generate keywords based on the question: '{question}' in the context of the following summary: {context_summary}."
    
    # Call the OpenAI API
    response = openai.chat.completions.create(
        model=config_data["engine"],
        messages=[
            {"role": "system", "content": "You are a context classifier."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    
    # Extract the keywords from the response
    keywords = response.choices[0].message.content.strip()
    
    # Tag the current question
    topic = tag_conversation(question)
    
    # Add the generated keywords and topic to the conversation history
    st.session_state.messages.append({"role": "assistant", "content": keywords, "topic": topic})
    
    # Identify relevant past conversations
    relevant_conversations = [item['content'] for item in st.session_state.messages[1:] if item.get('topic') == topic]
    
    return keywords, relevant_conversations

# React to user input
if prompt := st.chat_input("What do you want to ask your assistant today?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Send chat to openai
    keyword, relevance = get_keywords_and_relevant_conversations(prompt)
    print(relevance)
    # Display chatgpt response in chat message container
    with st.chat_message("assistant"):
        st.markdown(keyword)
