#! /usr/bin/env python
# -*- coding: utf-8 -*-

# sqlite3db.py
import sqlite3 as sqlite
import sqlparse

import logging
logger = logging.getLogger("app")

# Test SQL query: Retrieve all table names from the database
DB_TEST_QUERY = """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    AND name!='sqlite_sequence';
"""

def test(fname: str) -> bool:
    """
    Test whether the database file is valid.

    Args:
        fname (str): Path to the database file.

    Returns:
        bool: True if the database is valid and contains tables, False otherwise.
    """
    logger.debug("Function called")

    try:
        # Connect to the database
        db_conn = sqlite.connect(fname)
        db_cursor = db_conn.cursor()

        # Execute SQL to fetch table names
        db_cursor.execute(DB_TEST_QUERY)
        table_names = db_cursor.fetchall()
        db_conn.close()

        if not table_names:
            return False  # Return False if no tables exist

        return True

    except Exception as e:
        logger.error(e)  # Log the exception
        return False


def fetch_query(fname: str = None, sql: str = None, data: tuple = None) -> list | None:
    """
    Execute an SQL query and return the results.

    Args:
        fname (str): Path to the database file.
        sql (str): SQL query string to execute.
        data (tuple, optional): Parameters for the SQL query.

    Returns:
        list | None: A list of dictionaries representing the query results, or None if an error occurs or results are empty.
    """
    #logger.debug("Function called")

    try:
        if not sql:
            raise ValueError('SQL string is EMPTY.')  # Raise error if SQL is empty
    except ValueError as w:
        logger.info(w)
        return None

    try:
        # Connect to the database
        db_connect = sqlite.connect(fname)
        db_cursor = db_connect.cursor()

        # Execute the SQL query
        if data:
            db_cursor.execute(sql, data)
        else:
            db_cursor.execute(sql)

        # Process results: Convert column names and rows to a list of dictionaries
        desc = db_cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row)) for row in db_cursor.fetchall()]
        db_connect.close()

    except Exception as e:
        logger.error(e)  # Log the error
        db_connect.close()
        return None

    return data if len(data) > 0 else None  # Return results or None


def execute_query(fname: str = None, sql: str = None, data: tuple = None) -> bool:
    """
    Execute an SQL query and return success status.

    Args:
        fname (str): Path to the database file.
        sql (str): SQL query string to execute.
        data (tuple, optional): Parameters for the SQL query.

    Returns:
        bool: True if the query executes successfully, False otherwise.
    """
    #logger.debug("Function called")

    try:
        if not sql:
            raise ValueError('SQL string is EMPTY.')  # Raise error if SQL is empty
    except ValueError as w:
        logger.info(w)
        return False

    # Split the SQL statement into individual commands
    statements = sqlparse.split(sql)

    try:
        # Connect to the database
        db_connect = sqlite.connect(fname)
        db_cursor = db_connect.cursor()

        # Execute the appropriate type of query
        if data:
            db_cursor.execute(sql, data)  # Parameterized query
        elif len(statements) > 1:
            db_cursor.executescript(sql)  # Execute multiple SQL commands
        else:
            db_cursor.execute(sql)  # Execute a single SQL command

        db_connect.commit()  # Commit the changes
        db_connect.close()
        return True

    except Exception as e:
        logger.error(e)  # Log the error
        db_connect.close()
        return False
