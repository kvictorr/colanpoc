import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader

main_script_path = os.path.join(os.getcwd())
main_script_directory = os.path.dirname(main_script_path)

st.markdown(f"**Welcome Guest! I am your virtual assistant!**\n\nPlease choose a file to upload.")
# Create the file uploader widget
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf", "txt"])
if uploaded_file is not None:
    #st.markdown(f"{uploaded_file} File uploaded.")
    st.session_state.input_file = uploaded_file
    pg = st.navigation(pages=[
        "chat_assistant.py",
    ])
    pg.run()
else:
    st.session_state.input_file = None
