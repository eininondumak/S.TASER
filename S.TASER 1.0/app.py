#! /usr/bin/env python
# # -*- coding: utf-8 -*-

# app.py
import streamlit as st
from streamlit_option_menu import option_menu
import logging.config
import yaml

import src.config
import src.parsing_page
import src.import_page

# -----------------------------#
# Function Definition

def main():

    if "logging_initialized" not in st.session_state:
        with open(src.config.LOG_CONF_FILE, "r") as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
        st.session_state.logging_initialized = True

    if "parsing_state" not in st.session_state:
        st.session_state.parsing_state = False
        
    if "import_state" not in st.session_state:
        st.session_state.import_state = False

    st.set_page_config(
        page_title="SmartTAg parSER (S.TASER 1.0)",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': "# This is SmartTAg parSER app!"
        }
    )

    with st.sidebar:
        choice = option_menu("Menu", ["Parsing", "Import"],
                    icons=['bi bi-robot', 'kanban'],
                    menu_icon="app-indicator", default_index=0,
                    styles={
                        "container": {"padding": "4!important", "background-color": "#fafafa"},
                        "icon": {"color": "black", "font-size": "20px"},
                        "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "--hover-color": "#fafafa"},
                        "nav-link-selected": {"background-color": "#83cdf2"},
                        }
                    )

    if choice == "Parsing":
        src.parsing_page.app()
    elif choice == "Import":
        src.import_page.app()


# -----------------------------#
# App Entry
if __name__ == "__main__":
    main()
