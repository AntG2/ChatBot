import os
import openai
import streamlit as st
import json
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
            {"role": "system", "content": "You are an expert at extracting keywords from user queries. reply with keywords in a list"},
            {"role": "user", "content": f"生成以下问题的关键词，突出主要主题：'{question}'. Do not extract keywords from my prompt, only the question. Ignore meaningless words in text like 吗,是, like."}
        ]
    )
    
    topic = response.choices[0].message.content.strip()
    return topic

def get_keywords(question):
    # Add the new question to the conversation history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Formulate the prompt with context
    prompt = f"Reconstruct the following user statement or question '{question}'. \
                in the context of the following conversation history: {st.session_state.messages[1:]}. \
                Keep the original statement or question if there is no context correlations. \
                You must keep reconstructions in the original language the user uses for that statement or question being reconstructed. \
                Return your response as json format with the following fields: \
                'related' to write any earlier question or conversation that is used to reconstruct the statement or question, \
                if there are no related conversations, put 'None', and \
                'reconstructed' to write the reconstructed statement or question. \
                Do not respond with any other text, only json."
    
    # Call the OpenAI API
    response = openai.chat.completions.create(
        model=config_data["engine"],
        messages=[
            {"role": "system", "content": "You are a professional at filling in missing information of user query from context clues"},
            {"role": "user", "content": prompt}
        ]
    )
    print(response.choices[0].message.content.strip())
    # Extract the keywords from the response
    response = json.loads(response.choices[0].message.content.strip())

    reconstructed = response['reconstructed']
    # Tag the current question
    topic = tag_conversation(reconstructed)

    response['topic'] = topic
    # Add the generated keywords and topic to the conversation history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    return response

# React to user input
if prompt := st.chat_input("What do you want to ask your assistant today?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Send chat to openai
    response = get_keywords(prompt)
    # Display chatgpt response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
