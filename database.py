import mariadb
import json


# Make a function to insert_data into database
def insert_data(connection, table_name, column_names, values):
    # Prepare the INSERT statement with placeholders for the values
    insert_statement = f"INSERT INTO {table_name}({','.join(column_names)}) VALUES (?, ?, ...);"
    
    # Prepare the tuple of values to be inserted
    values_tuple = tuple(values)
def get_database_connection():
    """Returns a connection to the database using credentials in config.json"""
    with open("config.json", "r") as f:
        data = json.load(f)
        db_data = data["database"]

    host = db_data["host"]
    user = db_data["user"]
    password = db_data["password"]
    database = db_data["database"]

    try:
        connection = mariadb.connect(
            host=host, user=user, password=password, port=3306, database=database
        )
        cursor = connection.cursor()

        return connection
    except mariadb.Error as e:
        print("Error connecting to MariaDB:", e)
        return None
