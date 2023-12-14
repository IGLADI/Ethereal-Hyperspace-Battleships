import mariadb


# Make a function to insert_data into database
def insert_data(connection, table_name, column_names, values):
    # Prepare the INSERT statement with placeholders for the values
    insert_statement = f"INSERT INTO {table_name}({','.join(column_names)}) VALUES (?, ?, ...);"
    
    # Prepare the tuple of values to be inserted
    values_tuple = tuple(values)

    # Execute the INSERT statement and commit the changes
    try:
        cursor.execute(insert_statement, values_tuple)
        connection.commit()
        print("Data inserted successfully.")
    except Exception as e:
        connection.rollback()
        print("Error inserting data:", e)

def get_database_connection():
    try:
        # Connect to MariaDB server
        connection = mariadb.connect(
            host="localhost", 
            user="root", 
            password="projectx", 
            host="192.0.2.1", port=3306, 
            database="etherealhyperspacebattleshipsdb")
        cursor = connection.cursor()

        # Return the connection object
        return connection
    except mariadb.Error as e:
        # Print error message
        print("Error connecting to MariaDB:", e)
        sys.exit(1)
        return None


