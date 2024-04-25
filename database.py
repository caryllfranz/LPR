import sqlite3


# Function to connect to the database
def connect_to_database():
    try:
        conn = sqlite3.connect("database.db")
        print("Connected to database successfully!")
        return conn
    except sqlite3.Error as e:
        print("Error connecting to database:", e)
        return None


# Function to create the vehicle table if it doesn't exist
def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS vehicle (
                            licenseplate TEXT
                          )"""
        )
        conn.commit()
        print("Table 'vehicle' created successfully!")
    except sqlite3.Error as e:
        print("Error creating table:", e)


# Function to insert a new record into the vehicle table
def insert_vehicle(conn, license_plate):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vehicle (licenseplate) VALUES (?)", (license_plate,)
        )
        conn.commit()
        print("Record inserted successfully!")
    except sqlite3.Error as e:
        print("Error inserting record:", e)


# Function to delete a record from the vehicle table
def delete_vehicle(conn, license_plate):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vehicle WHERE licenseplate = ?", (license_plate,))
        conn.commit()
        print("Record deleted successfully!")
    except sqlite3.Error as e:
        print("Error deleting record:", e)


# Main function
def main():
    # Connect to the database
    conn = connect_to_database()
    if conn is None:
        return

    # Create the table
    create_table(conn)

    # Example usage: Insert a record
    insert_vehicle(conn, "ABC123")

    # Example usage: Delete a record
    delete_vehicle(conn, "ABC123")

    # Close the database connection
    conn.close()


if __name__ == "__main__":
    main()
