import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib
import urllib.parse
import pyodbc
import os
import sys
import sqlite3
import json
from sqlalchemy import text

def run_sql_script(script):
    """
    Execute a SQL script on a specified database.

    This function reads database configuration from environment variables,
    constructs a connection string, creates a SQLAlchemy engine, and executes
    the provided SQL script.

    Parameters:
    script (str): The SQL script to be executed.

    Environment Variables:
    DB_TYPE: The type of database (mysql, postgres, or sqlserver).
    DB_SERVER: The server name or IP address of the database.
    DB_USERNAME: The username for database authentication.
    DB_PASSWORD: The password for database authentication.
    DB_NAME: The name of the database.
    DB_PORT: The port number for the database connection.

    Raises:
    ValueError: If an unsupported database type is specified.
    EnvironmentError: If any required environment variables are missing.
    Exception: If there's an error while executing the SQL script.

    Returns:
    None

    Note:
    The function will exit the script with a status code of 1 if an error occurs
    during the execution of the SQL script.
    """
    # Use the appropriate driver name
    type = os.environ.get('DB_TYPE')
    if type.lower() == 'mysql':
        driver = "MySQL ODBC 8.0 ANSI Driver"  
    elif type.lower() == 'postgres':
        driver = "PostgreSQL Unicode"  
    elif type.lower() == 'sqlserver':
        driver = "ODBC Driver 18 for SQL Server"
    else:
        raise ValueError(f"Unsupported database type: {type}")
    
    server = os.environ.get('DB_SERVER')
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    database = os.environ.get('DB_NAME')
    port = os.environ.get('DB_PORT')
    if not server:
        raise EnvironmentError('Missing server name.')

    if not username:
        raise EnvironmentError('Missing database username.')
 
    if not password:
        raise EnvironmentError('Missing database password.')

    if not database:
        raise EnvironmentError('Missing database name.')
    
    # Construct the connection string for the SQL Server database using the provided
    # server name, database name, username, and password retrieved from environment variables.
    # The connection string is URL-encoded using urllib.parse.quote_plus to ensure
    # special characters are properly handled.
    # Create the connection string
    connection_string = urllib.parse.quote_plus(
        f"DRIVER={{{driver}}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes"
    )
    try:
        # Create a SQLAlchemy engine using the provided connection string for connecting to the SQL Server database
        if type.lower() == 'sqlserver':
            engine = create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")
        elif type.lower() == 'mysql':
            engine = engine = create_engine(f"mysql+pyodbc:///?odbc_connect={connection_string}")
        elif type.lower() == 'postgres':
            engine = create_engine(f"postgresql+pyodbc:///?odbc_connect={connection_string}")
        else:
            raise ValueError(f"Unsupported database type: {type}")

        # Execute the SQL script
        with engine.connect() as connection:
            for statement in script.split(';'):
                if statement.strip():
                    connection.execute(text(statement))
            connection.commit()
    except Exception as e:
        print(f"Error running SQL script: {e}")
        sys.exit(1)

def save_to_sql(df, table_name):
    """
    Save a pandas DataFrame to a SQL database.

    This function connects to a SQL database using environment variables for configuration,
    and saves the provided DataFrame to a specified table.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be saved to the SQL database.
    table_name: The name of the table where the data will be saved.

    Environment Variables:
    DB_TYPE: The type of database (mysql, postgres, or sqlserver).
    DB_SERVER: The server name or IP address of the database.
    DB_USERNAME: The username for database authentication.
    DB_PASSWORD: The password for database authentication.
    DB_NAME: The name of the database.

    Returns:
    int: 1 if data was successfully saved, 0 if there was no data to save.

    Raises:
    ValueError: If an unsupported database type is specified or if there's an error saving the DataFrame.
    EnvironmentError: If any required environment variables are missing.

    Note:
    This function uses SQLAlchemy to create a database engine and pandas' to_sql method to save the data.
    The data is appended to the specified table if it already exists.
    """
    # Use the appropriate driver name
    type = os.environ.get('DB_TYPE')
    if type.lower() == 'mysql':
        driver = "MySQL ODBC 8.0 ANSI Driver"  
    elif type.lower() == 'postgres':
        driver = "PostgreSQL Unicode"  
    elif type.lower() == 'sqlserver':
        driver = "ODBC Driver 18 for SQL Server"
    else:
        raise ValueError(f"Unsupported database type: {type}")
    
    server = os.environ.get('DB_SERVER')
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    database = os.environ.get('DB_NAME')
    port = os.environ.get('DB_PORT')
    if not server:
        raise EnvironmentError('Missing server name.')

    if not username:
        raise EnvironmentError('Missing database username.')
 
    if not password:
        raise EnvironmentError('Missing database password.')

    if not database:
        raise EnvironmentError('Missing database name.')

    if not table_name:
        raise EnvironmentError('Missing database table name.')
    
    # Construct the connection string for the SQL Server database using the provided
    # server name, database name, username, and password retrieved from environment variables.
    # The connection string is URL-encoded using urllib.parse.quote_plus to ensure
    # special characters are properly handled.
    # Create the connection string
    connection_string = urllib.parse.quote_plus(
        f"DRIVER={{{driver}}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes"
    )
    try:
        # Create a SQLAlchemy engine using the provided connection string for connecting to the SQL Server database
        if type.lower() == 'sqlserver':
            engine = create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")
        elif type.lower() == 'mysql':
            engine = engine = create_engine(f"mysql+pyodbc:///?odbc_connect={connection_string}")
        elif type.lower() == 'postgres':
            engine = create_engine(f"postgresql+pyodbc:///?odbc_connect={connection_string}")
        else:
            raise ValueError(f"Unsupported database type: {type}")
        
        # Use the to_sql method to save the DataFrame to the specified table in the SQL database
        # 'name' parameter: specifies the name of the table
        # 'con' parameter: takes the SQLAlchemy engine as the connection
        # 'if_exists' parameter: appends data to the table if it already exists
        # 'index' parameter: specifies not to write DataFrame index as a column
        if len(df) > 0:
            df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
            # Print a success message indicating the table name, database name, and server
            print(f"Data saved to table '{table_name}' in database '{database}' on server '{server}' successfully!")
            return 1
        else:
            print("No data to save.")
            return 0        
    except Exception as e:
        # Raise a ValueError with a message indicating an error occurred while saving the DataFrame to the SQL database
        raise ValueError(f"Error on saving DataFrame to database: {e}") from e

def ETL(conn):
    """
    Perform ETL (Extract, Transform, Load) operations on data from a SQLite database.

    This function reads configuration from a JSON file, executes SQL queries from
    separate files for each table, and saves the resulting data to a SQL database.

    Parameters:
    conn (sqlite3.Connection): A connection object to the source SQLite database.

    The function performs the following steps:
    1. Reads configuration from 'query_scripts/queries.json'.
    2. For each item in the configuration:
        a. Reads the SQL query from the specified file.
        b. Executes the query on the source database.
        c. Stores the result in a pandas DataFrame.
        d. Prints the data volume for the table.
        e. Saves the data to the destination SQL database.

    Raises:
    FileNotFoundError: If the SQL script file specified in the configuration is not found.
    IOError: If there's an error reading the SQL script file.

    Note:
    - The function uses the 'save_to_sql' function to save data to the destination database.
    - Additional ETL steps can be added where indicated in the code.
    """
    # Get items from a json file
    with open('query_scripts/queries.json', 'r') as config_file:
        config = json.load(config_file)
        prequisites = config['prequisites']
        items = config['extract_loads']
        transformations = config['transformations']
    
    # for each item in the prequisites list
    for item in prequisites:
        sql_file_path = item['query']
        # run the sql script
        try:
            with open(sql_file_path, 'r') as file:
                script = file.read()
        except IOError as e:
            raise IOError(f"Error reading SQL script file: {e}")
        # run the sql script
        run_sql_script(script)
        print(f"The prequisites steps (at {sql_file_path}) were executed successfully!")

    # for each item in the extracts list
    for item in items:
        table_name = item['table']
        sql_file_path = item['query']

        # Check if the file exists
        if not os.path.isfile(sql_file_path):
            raise FileNotFoundError(f"SQL script file not found: {sql_file_path}")

        # Read the SQL query from the file
        try:
            with open(sql_file_path, 'r') as file:
                source_query = file.read()
        except IOError as e:
            raise IOError(f"Error reading SQL script file: {e}")
        # Extract the data from the source database using the provided connection & SQL query
        # and store the result in a Pandas DataFrame
        print(f"The query of {sql_file_path} is running...")
        source_df = pd.read_sql_query(source_query, conn)
        # Add here if you have additional ETL steps
        # Todo: Add your ETL steps here
        print(f"The data volume added on {table_name} is: {len(source_df)}")
        # Save the final data into SQL Server database
        save_to_sql(source_df, table_name)
    
    # for each item in the transformation list
    for item in transformations:
        sql_file_path = item['query']
        # run the sql script
        try:
            with open(sql_file_path, 'r') as file:
                script = file.read()
        except IOError as e:
            raise IOError(f"Error reading SQL script file: {e}")
        # run the sql script
        run_sql_script(script)
        print(f"The transformation steps (at {sql_file_path}) were executed successfully!")

def main():
    """
    Main function to process a sqlite db file and save its contents to a SQL database.

    This function performs the following tasks:
    1. Checks if a file path is provided as a command-line argument.
    2. Verifies if the provided file has a .db extension.
    3. Attempts to read the sqlite db file into a pandas DataFrame.
    4. Displays basic information about the loaded DataFrame.
    5. Calls the save_to_sql function to save the DataFrame to a SQL database.

    The function handles various exceptions that may occur during file processing:
    - FileNotFoundError: If the specified file does not exist.
    - pd.errors.EmptyDataError: If the sqlite db file is empty.
    - Other exceptions that may occur during file reading.

    Usage:
        Run the script from the command line with the sqlite db file path as an argument:
        python script_name.py path/to/your/sqlite.db

    Returns:
        None. The function will exit the script with a status code of 1 if an error occurs.
    """
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Error: Please provide the path to the SQL Lite DB file as a command-line argument.")
        sys.exit(1)

    # Get the file path from command-line argument
    file_path = sys.argv[1]

    # Check if the file has a .db extension
    if not file_path.endswith('.db'):
        print("Error: The provided file is not a sqlite db file.")
        sys.exit(1)

    try:
        # connect to sqlite db file
        conn = sqlite3.connect(file_path)
        # ETL to get the proper data from the sqlite db file
        ETL(conn)
        # close the connection to the sqlite db file
        conn.close()        
        
    except FileNotFoundError as e:
        print(f"Error: The file {file_path} was not found. The detailed error message is: {str(e)}")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
