import os
import streamlit as st

st.set_page_config(layout="wide")

def main():
    
    # Render Logo and Name in sidebar
    st.sidebar.markdown(
        f"""
        <div style="display: flex; align-items: center; padding: 1rem 0;">
            <h1 style="margin: 0; font-size: 2.5rem;">Welcome!</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Add global settings in Service-GPT sidebar here
    description = "This is an AI-powered chatbot designed to answer your questions using the information provided in the source document. \n\n Please upload a document (pdf or txt only)"
    st.sidebar.caption(description)

    # Setup page navigation
    pg = st.navigation(pages=[
        "file_loader.py",
    ])
    pg.run()

if __name__ == "__main__":
    main()