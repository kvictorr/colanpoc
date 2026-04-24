import streamlit as st
import sys, os, re
from chat_agents import RoutingAgent

# Initialize session variables
if "chat_assistant_messages" not in st.session_state:
    st.session_state.chat_assistant_messages = []
    #st.session_state.chat_assistant_example_radio = True

if "chat_assistant_disabled" not in st.session_state:
    st.session_state.chat_assistant_disabled = False
    st.session_state.chat_assistant_example = False

# Feedback functions
def input_prompt():
    st.session_state.chat_assistant_disabled = False
    st.session_state.chat_assistant_setting_change = False

def disable():
    st.session_state.chat_assistant_disabled = True
    st.session_state.chat_assistant_setting_change = True

def setting_change():
    st.session_state.chat_assistant_setting_change = True

### Main content area ###
def run_example():
    st.session_state.chat_assistant_example = st.session_state["chat_assistant_example_radio"]
    input_prompt()

def split_by_capitals(s):
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', s)

llm_agent = RoutingAgent
st.markdown(f"**Great!**\n\nI have been trained with your document {st.session_state["input_file"].name}. Ask me anything in plain language, here are a few examples to get started:")
st.radio("To get started, you can select any of the examples below:",
            key='chat_assistant_example_radio',
            options=["Please provide summary of the document.",
            "Comment on the sentiment of the document.",
            "Give a suitable title to the document."],
            index=None,
            on_change=run_example,
            disabled=st.session_state.chat_assistant_disabled)

# Chat input
new = st.container(height= 75, border = False)
with new:
    typed_prompt = st.chat_input("Ask your question", 
                    key='chat_assistant_real', 
                    on_submit=input_prompt, 
                    disabled=st.session_state.chat_assistant_disabled)

# Chat interface
container1 = st.container(border=True)
#container1 = st.container(height=700, border=False)

if typed_prompt or st.session_state.chat_assistant_example:
    
    prompt = typed_prompt if typed_prompt else st.session_state.chat_assistant_example  
    print(prompt)      
    message = {'role':'user', 'content':[{'type':'text', 'text':prompt}]}
    
    response = llm_agent.interact(prompt)
    #response = "I am processing your request!"
    print(response)
    #with container1:
        #response = st.write_stream(response)
        #st.write(response)      

    feedback = 'None'
    messages = [{"role":"user", "content": prompt},
                {"role":"assistant", "content":response},
                {"role":"feedback", "content":feedback}
            ]

    st.session_state.chat_assistant_messages.append(messages)
    
    st.session_state.chat_assistant_disabled = False
    st.session_state.chat_assistant_example = None
    st.rerun()

for count in range(len(st.session_state.chat_assistant_messages)-1, -1, -1):
    user_message, assistant_message, feedback_message = st.session_state.chat_assistant_messages[count]

    with container1:
        with st.chat_message(assistant_message["role"]):
            st.write(assistant_message["content"])

        with st.chat_message(user_message["role"]):
            st.write(user_message["content"])
        st.markdown('***')
