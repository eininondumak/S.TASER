#! /usr/bin/env python
# # -*- coding: utf-8 -*-

# import_page.py

import streamlit as st
import subprocess
import random
import json
import os
import folium
from folium.plugins import BeautifyIcon
import logging
from typing import Optional

from src.tag_parser import get_parsed_data

# Set up logger
logger = logging.getLogger("app")

# -----------------------------#
# Function Definition

def app() -> None:
    """
    Streamlit app to import and display Result DB data.

    Allows the user to select a DB file, parses its data, and displays relevant information.
    """
    logger.debug("Function called")

    # Initialize session state variables
    if "db_file_path" not in st.session_state:
        st.session_state.db_file_path = None
    if "tag_data" not in st.session_state:
        st.session_state.tag_data = None
    if "location_data" not in st.session_state:
        st.session_state.location_data = None
    if "enclocation_data" not in st.session_state:
        st.session_state.enclocation_data = None

    st.title("Result DB Import")
    st.markdown("Choose a Result DB file")

    # UI for selecting a database file
    col_button, col_info = st.columns([0.1, 0.9], vertical_alignment="center")
    db_info_board = col_info.info(
        f"Current DB File: {st.session_state.db_file_path}"
    )

    if col_button.button(key="button_import_db", label="Choose File", type="primary"):
        db_file_path = select_file_dialog()
        if db_file_path:
            db_file_path = os.path.normpath(db_file_path)
            st.success(f"Selected DB File: {db_file_path}")
            db_info_board.info(f"Current DB File: {db_file_path}")
            st.session_state.db_file_path = db_file_path

            if st.session_state.tag_data is not None:
                del st.session_state.tag_data
                st.session_state.tag_data = None
            if st.session_state.location_data is not None:
                del st.session_state.location_data
                st.session_state.location_data = None
            if st.session_state.enclocation_data is not None:
                del st.session_state.enclocation_data
                st.session_state.enclocation_data = None

            tag_data, location_data, enclocation_data = get_parsed_data(db_file_path)

            st.session_state.tag_data = tag_data
            st.session_state.location_data = location_data
            st.session_state.enclocation_data = enclocation_data
            st.session_state.import_state = True
        else:
            st.error("No DB file selected")

    if st.session_state.get("import_state"):

        # Display Tag Information
        st.subheader("Tag's Information", divider="blue")
        # Adjust the index to start from 1
        tag_data = st.session_state.tag_data.copy()
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
            selected_rows, "UUID"
        ].tolist()

        # Display Tag Location History
        st.subheader("Tag's Location History", divider="blue")
        location_data_filtered = st.session_state.location_data[
            st.session_state.location_data["UUID"].isin(selected_uuids)
        ]
        # Adjust the index to start from 1
        location_data_filtered.index = range(1, len(location_data_filtered) + 1)
        st.dataframe(location_data_filtered, use_container_width=True)

        if not location_data_filtered.empty:
            render_location_map(location_data_filtered)

        # Display Tag Enclocation History
        st.subheader("Tag's Enclocation History", divider="blue")
        enclocation_data_filtered = st.session_state.enclocation_data[
            st.session_state.enclocation_data["UUID"].isin(selected_uuids)
        ]
        # Adjust the index to start from 1
        enclocation_data_filtered.index = range(1, len(enclocation_data_filtered) + 1)
        st.dataframe(enclocation_data_filtered, use_container_width=True)


def select_file_dialog() -> Optional[str]:
    """
    Opens a file selection dialog and returns the selected file path.

    Returns:
        Optional[str]: The path to the selected file or None if no file is selected.
    """
    logger.debug("File selection dialog called")
    try:
        result = subprocess.run(
            ["python", "src/file_selector.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout:
            file_data = json.loads(result.stdout)
            return file_data.get("file_path")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during file selection: {e}")
    return None


def render_location_map(location_data) -> None:
    """
    Renders a map with the location data.

    Args:
        location_data: A DataFrame containing location data to render on the map.
    """
    map_ = folium.Map(zoom_start=6, tiles="CartoDB positron")
    unique_uuids = location_data["UUID"].unique()

    for uuid in unique_uuids:
        random_color = f"#{random.randint(0, 0xFFFFFF):06x}"
        uuid_data = location_data[location_data["UUID"] == uuid]
        coordinates = uuid_data[["Latitude", "Longitude"]].values.tolist()
        folium.PolyLine(locations=coordinates, color=random_color).add_to(map_)

        for index, row in uuid_data.iterrows():
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

    st.components.v1.html(map_._repr_html_(), height=600)
