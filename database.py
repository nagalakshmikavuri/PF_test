"""
SQLite Database Functions

This script contains functions to handle interactions with an SQLite database to store JSON data.
It includes functions to create a table, insert data, retrieve data, and delete data.

Developer: Ashish Kumar

Website: https://ashishkrb7.github.io/

Contact Email: ashish.krb7@gmail.com
"""
import json
import sqlite3

# Define the path to the SQLite database file
DATABASE_FILE = "data.db"


def create_table():
    """
    Create a table in the database to store JSON data.

    This function creates a table named 'json_data' in the SQLite database to store JSON data.
    The table has two columns: 'email' (as the primary key) and 'data' (to store JSON data).

    Returns:
        None
    """
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # Create a table to store JSON data with email as the primary key
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS json_data (
            email TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()


def insert_data(email, data):
    """
    Insert JSON data into the database.

    This function inserts JSON data into the 'json_data' table in the SQLite database.
    The 'email' is used as the primary key, and the 'data' is converted to a JSON string before insertion.

    Args:
        email (str): User's email address (used as the primary key).
        data (dict): JSON data to be inserted into the database.

    Returns:
        None
    """
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # Convert the JSON data to a string and insert it into the database
    c.execute(
        "INSERT OR REPLACE INTO json_data (email, data) VALUES (?, ?)",
        (email, json.dumps(data)),
    )

    conn.commit()
    conn.close()


def get_data(email):
    """
    Retrieve JSON data from the database based on the email address.

    This function retrieves JSON data from the 'json_data' table in the SQLite database
    based on the provided email address.

    Args:
        email (str): User's email address to retrieve the corresponding JSON data.

    Returns:
        dict or None: JSON data corresponding to the email address, or None if not found.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # Retrieve data for a specific email from the database
    c.execute("SELECT data FROM json_data WHERE email = ?", (email,))
    row = c.fetchone()

    # If data is found for the email, convert the JSON data (as a string) back to JSON format
    if row:
        json_data = json.loads(row[0])
    else:
        json_data = None

    conn.close()

    return json_data


def delete_data(email):
    """
    Delete user data from the database based on the email address.

    This function deletes the row with the provided email address from the 'json_data' table
    in the SQLite database.

    Args:
        email (str): User's email address to identify the row to be deleted.

    Returns:
        None
    """
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()

    # Delete the row with the provided email address from the 'json_data' table
    c.execute("DELETE FROM json_data WHERE email = ?", (email,))

    conn.commit()
    conn.close()
