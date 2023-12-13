import pymysql
import sys

try:
    connection = pymysql.connect(host="localhost", user="root", password="groupx", database="etherealhyperspacebattleshipsdb")
    cursor = connection.cursor()
except Exception as e:
    print("Error connecting to MariaDB:", e)
    sys.exit(1)

# Prompt the user for the table name
table_name = input("Enter the table name: ")

# Prompt the user for the column names and values
column_names = input("Enter the column names separated by commas: ")
column_names = column_names.split(", ")
values = input("Enter the corresponding values separated by commas: ")
values = values.split(", ")

# Prepare the INSERT statement with placeholders for the values
insert_statement = f"INSERT INTO {table_name}({','.join(column_names)}) VALUES (%s, %s, ...);"

# Prepare the tuple of values to be inserted
values_tuple = tuple(values)
try:
    cursor.execute(insert_statement, values_tuple)
    connection.commit()
    print("Data inserted successfully.")
except Exception as e:
    connection.rollback()
    print("Error inserting data:", e)

connection.close()
