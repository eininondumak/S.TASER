#! /usr/bin/env python
# # -*- coding: utf-8 -*-

# import_page.py
import streamlit as st
import os
from datetime import datetime
import subprocess
import json
import math
import random
import folium
from folium.plugins import BeautifyIcon
import yaml
from typing import Optional

import src.config as cfg
import src.tag_parser as ps

import logging

# Set up logger
logger = logging.getLogger("app")

# -----------------------------#
# Function Definition

def app() -> None:
    """
    Streamlit application for parsing SmartThings and Samsung Find data.

    This app allows users to select folders and files, then parse and display the data.
    """
    logger.debug("Function called")

    # Initialize session state variables
    init_session_state_variables()

    # Generate paths for result DB and log files
    generate_result_paths()
    
    st.title("SmartTAg parSER")

    # Layout for selecting folders
    render_folder_selection_ui()
    
    # Layout for selecting DB and log file directories
    render_db_and_log_selection_ui()

    st.divider()
    if not st.session_state.smartthings_path:
        st.button(key="button_parsing", 
                  label="Start Parsing", 
                  use_container_width=True, 
                  disabled=True,
                  help="not selected SmartThings folder")
    elif st.session_state.parsing_state:
        st.button(key="button_parsing", 
                  label="Close", 
                  type="primary",
                  on_click=handle_click_close,
                  use_container_width=False)
    else:
        st.button(key="button_parsing", 
                  label="Start Parsing", 
                  type="primary", 
                  on_click=handle_click_parsing,
                  use_container_width=True)

    # Parsing and displaying data
    if st.session_state.get("parsing_state", False):
        render_parsed_data_ui()


def init_session_state_variables() -> None:
    """
    Initializes session state variables for storing file paths and parsing states.
    """
    logger.debug("Function called")

    state_vars = [
        "smartthings_path",
        "samsung_find_path",
        "result_db_file",
        "result_log_file",
        "parsing_state",
    ]

    for var in state_vars:
        if var not in st.session_state:
            st.session_state[var] = None


def generate_result_paths() -> None:
    """
    Generates file paths for result DB and log files if not already set in the session state.
    """
    logger.debug("Function called")

    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    current_path = os.getcwd()

    if not st.session_state.result_db_file:
        st.session_state.result_db_file = os.path.normpath(
            rf"{current_path}/resultdb/{current_timestamp}_{cfg.DB_FILE}"
        )

    if not st.session_state.result_log_file:
        st.session_state.result_log_file = os.path.normpath(
            rf"{current_path}/log/{current_timestamp}_{cfg.LOG_FILE}"
        )
        update_log_output(st.session_state.result_log_file)


def render_folder_selection_ui() -> None:
    """
    Renders the folder selection UI for SmartThings and Samsung Find data.
    """
    logger.debug("Function called")

    # Left column: SmartThings folder selection
    col_left, col_right = st.columns(2, vertical_alignment="top")

    col_left.subheader("Samsung SmartThings App", divider="blue")
    stinfo = col_left.info(f"Current Folder: {st.session_state.smartthings_path}")
    col_left.markdown("Select SmartThings folder.")

    if not st.session_state.parsing_state:
        if col_left.button(key="button_st", label="Select Folder", type="primary"):
            folder_path = open_folder_dialog()
            if folder_path and ps.check_smartThings_path(folder_path):
                st.session_state.smartthings_path = os.path.normpath(folder_path)
                col_left.success(f"Selected Folder: {folder_path}")
                stinfo.info(f"Current Folder: {st.session_state.smartthings_path}")
            else:
                col_left.error("Invalid SmartThings folder selected.")
    else:
        col_left.button(key="button_st", label="Select Folder", type="primary", disabled=True)

    # Right column: Samsung Find folder selection
    col_right.subheader("Samsung Find App (Optional)", divider="blue")
    sfinfo = col_right.info(f"Current Folder: {st.session_state.samsung_find_path}")
    col_right.markdown("Select Samsung Find folder.")

    if not st.session_state.parsing_state:
        if col_right.button(key="button_sf", label="Select Folder"):
            folder_path = open_folder_dialog()
            if folder_path:
                st.session_state.samsung_find_path = os.path.normpath(folder_path)
                col_right.success(f"Selected Folder: {folder_path}")
                sfinfo.info(f"Current Folder: {st.session_state.samsung_find_path}")
            else:
                col_left.error("Invalid SmartThings folder selected.")
    else:
        col_right.button(key="button_sf", label="Select Folder", disabled=True)


def render_db_and_log_selection_ui() -> None:
    """
    Renders the UI for selecting or changing the database and log file directories.
    """
    logger.debug("Function called")

    col_left, col_right = st.columns(2, vertical_alignment="top")

    # Left column: Result DB file selection
    col_left.subheader("Result SQLite DB", divider="blue")
    dfinfo = col_left.info(f"Current DB File: {st.session_state.result_db_file}")

    if not st.session_state.parsing_state:
        if col_left.button(key="button_db", label="Change Folder"):
            folder_path = open_folder_dialog()
            if folder_path:
                cur_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                ch_db_path = os.path.normpath(
                    rf"{folder_path}/{cur_timestamp}_{cfg.DB_FILE}"
                )
                st.session_state.result_db_file = ch_db_path
                col_left.success(f"Changed DB File Path: {ch_db_path}")
                dfinfo.info(f"Current DB File: {ch_db_path}")
            else:
                col_left.error("Invalid DB folder selected.")
    else:
        col_left.button(key="button_db", label="Change Folder", disabled=True)

    # Right column: Log file selection
    col_right.subheader("Result Log", divider="blue")
    lfinfo = col_right.info(f"Current Log File: {st.session_state.result_log_file}")

    if not st.session_state.parsing_state:
        if col_right.button(key="button_log", label="Change Folder"):
            folder_path = open_folder_dialog()
            if folder_path:
                cur_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                ch_log_path = os.path.normpath(
                    rf"{folder_path}/{cur_timestamp}_{cfg.LOG_FILE}"
                )
                st.session_state.result_log_file = ch_log_path
                col_right.success(f"Changed Log File Path: {ch_log_path}")
                lfinfo.info(f"Current Log File: {st.session_state.result_log_file}")
                update_log_output(ch_log_path)
            else:
                col_right.error("Invalid Log folder selected.")
    else:
        col_right.button(key="button_log", label="Change Folder", disabled=True)


def render_parsed_data_ui() -> None:
    """
    Renders the UI for displaying parsed data, including tags, location, and history.
    """
    logger.debug("Function called")
        
    st.subheader("Parsed Elements", divider="blue")
    columns_per_row = 6
    rows = math.ceil(len(st.session_state.checkbox_states) / columns_per_row)        
    keys = list(st.session_state.checkbox_states.keys())
    for row in range(rows):
        cols = st.columns(columns_per_row)
        for col, key in zip(cols, keys[row * columns_per_row : (row + 1) * columns_per_row]):
            with col:
                st.checkbox(
                    key,
                    value=st.session_state.checkbox_states[key],
                    disabled=True
                )

    # Display Tag Information
    st.subheader("Tag's Information", divider="blue")
    
    # Adjust the index to start from 1
    tag_data = st.session_state.all_tag_df.copy()
    tag_data.index = range(1, len(tag_data) + 1)

    # Display the DataFrame in Streamlit
    tag_data_event = st.dataframe(
        tag_data,
        use_container_width=True,
        on_select="rerun",
        selection_mode=["multi-row"],
    )
    selected_rows = tag_data_event.selection.rows
    selected_rows = [num + 1 for num in selected_rows]
    selected_uuids = tag_data.loc[
        selected_rows, "deviceId"
    ].tolist()

    # Display Tag Location History
    st.subheader("Tag's Location History", divider="blue")
    location_data_filtered = st.session_state.all_loc_df[
        st.session_state.all_loc_df["deviceId"].isin(selected_uuids)
    ]
    # Adjust the index to start from 1
    location_data_filtered.index = range(1, len(location_data_filtered) + 1)
    st.dataframe(location_data_filtered, use_container_width=True)

    if not location_data_filtered.empty:
        render_location_map(location_data_filtered)

    # Display Tag Enclocation History
    st.subheader("Tag's Enclocation History", divider="blue")
    enclocation_data_filtered = st.session_state.all_enc_df[
        st.session_state.all_enc_df["deviceId"].isin(selected_uuids)
    ]
    # Adjust the index to start from 1
    enclocation_data_filtered.index = range(1, len(enclocation_data_filtered) + 1)
    st.dataframe(enclocation_data_filtered, use_container_width=True)


def render_location_map(location_data) -> None:
    """
    Renders a map with the location data.

    Args:
        location_data: A DataFrame containing location data to render on the map.
    """

    map_center = [location_data['Latitude'].mean(), location_data['Longitude'].mean()]
    bounds = [
    [location_data['Latitude'].min(), location_data['Longitude'].min()],
    [location_data['Latitude'].max(), location_data['Longitude'].max()]]

    map_ = folium.Map(location=map_center, tiles="CartoDB positron")

    unique_deviceIds = location_data["deviceId"].unique()

    for deviceId in unique_deviceIds:
        random_color = f"#{random.randint(0, 0xFFFFFF):06x}"
        deviceId_data = location_data[location_data["deviceId"] == deviceId]
        coordinates = deviceId_data[["Latitude", "Longitude"]].values.tolist()
        folium.PolyLine(locations=coordinates, color=random_color).add_to(map_)

        for index, row in deviceId_data.iterrows():
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                icon=BeautifyIcon(
                    icon="arrow-down",
                    icon_shape="circle",
                    border_width=2,
                    number=index + 1,
                    background_color=random_color,
                ),
                tooltip=f"Time: {row['StartTime(UTC)']}, Count: {row['Count']}",
            ).add_to(map_)
    
    map_.fit_bounds(bounds)
    st.components.v1.html(map_._repr_html_(), height=600)


def open_folder_dialog() -> Optional[str]:
    """
    Opens a folder selection dialog and returns the selected folder path.

    Returns:
        Optional[str]: The selected folder path, or None if no selection was made.
    """
    logger.debug("Function called")

    try:
        result = subprocess.run(
            ["python", "src/folder_selector.py"], capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout:
            folder_data = json.loads(result.stdout)
            return folder_data.get("folder_path")
    except Exception as e:
        logger.error(f"Error opening folder dialog: {e}")
    return None


def handle_click_parsing() -> None:
    """
    Handles the Start Parsing button click event.
    """
    logger.debug("Function called")

    st.session_state.parsing_state = True

    parsing_ret, all_tag_df, all_loc_df, all_enc_df = ps.start_parsing(st.session_state.smartthings_path,
                                                                        st.session_state.samsung_find_path,
                                                                        st.session_state.result_db_file)
    
    st.session_state.checkbox_states = parsing_ret.copy()
    st.session_state.all_tag_df = all_tag_df
    st.session_state.all_loc_df = all_loc_df
    st.session_state.all_enc_df = all_enc_df


def handle_click_close() -> None:
    """
    Handles the Close Parsing button click event and resets parsing states.
    """
    logger.debug("Function called")

    st.session_state.clear()
    st.session_state.parsing_state = False


def update_log_output(log_file_path: str) -> None:
    """
    Updates the log output file to the specified path.

    Args:
        log_file_path (str): The path to the new log file.
    """
    logger.debug("Function called")

    # Remove existing log handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()

    # Load logging configuration and apply it
    with open(cfg.LOG_CONF_FILE, "r") as file:
        config = yaml.safe_load(file.read())

    handler_config = config.get("handlers", {}).get("file_handler", {})
    log_level = handler_config.get("level", "DEBUG")
    
    # Create the FileHandler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.getLevelName(log_level))  # Use the configured log level

    # Define formatter from the handler config or use a default formatter
    formatter_config = handler_config.get("formatter", "default_formatter")
    formatter_settings = config.get("formatters", {}).get(formatter_config, {})
    log_format = formatter_settings.get("format", '%(asctime)s - %(levelname)s - %(message)s')
    date_format = formatter_settings.get("datefmt", None)

    # Apply formatter to the FileHandler
    formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)
    logger.info(f"File logging has been added with level {log_level}. Logs will be saved to {log_file_path}")

