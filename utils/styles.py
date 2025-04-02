def get_css():
    return """
    /* General styles */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Link styles */
    a {
        text-decoration: none;
    }
    a:hover {
        text-decoration: none;
    }
    
    /* Card styles */
    .stCard {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Button styles */
    .stButton>button {
        background-color: #4169e1;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #3158d1;
    }
    """

def apply_custom_styles():
    import streamlit as st
    # Hide Streamlit's default menu and footer
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* Hide sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }
        /* Center all content */
        .main .block-container {
            max-width: 1200px;
            padding-top: 1rem;
            padding-right: 1rem;
            padding-left: 1rem;
            padding-bottom: 1rem;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True) 