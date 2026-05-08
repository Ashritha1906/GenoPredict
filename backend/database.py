import mysql.connector
from mysql.connector import Error
import pandas as pd

class DatabaseManager:
    def __init__(self, host='localhost', user='root', password='', database='bioinformatics_db'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            # First connect without database to create it if it doesn't exist
            temp_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            temp_conn.close()

            # Connect to the specific database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False

    def create_tables(self):
        if not self.connection:
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # Create main genomics table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS genomic_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                gene_id VARCHAR(50),
                gene_name VARCHAR(100),
                condition_name TEXT,
                variation TEXT,
                protein_change TEXT,
                consequence TEXT,
                location VARCHAR(100),
                review_status VARCHAR(100),
                disease VARCHAR(100)
            )
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error creating tables: {e}")
            return False

    def import_csv_to_db(self, csv_file_path):
        """Imports the final combined CSV into the MySQL database."""
        if not self.connection:
            if not self.connect():
                return False
                
        try:
            df = pd.read_csv(csv_file_path)
            # Replace NaNs with None for MySQL
            df = df.where(pd.notnull(df), None)
            
            cursor = self.connection.cursor()
            
            # Check if data already exists to avoid duplication
            cursor.execute("SELECT COUNT(*) FROM genomic_data")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"Database already contains {count} records. Skipping import.")
                return True
                
            print("Importing data to MySQL... This may take a moment.")
            
            insert_query = """
            INSERT INTO genomic_data 
            (gene_id, gene_name, condition_name, variation, protein_change, consequence, location, review_status, disease) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Convert dataframe to list of tuples
            # Make sure column names match exactly or map them properly
            # Assuming CSV columns are: gene_id, gene_name, condition, variation, protein_change, consequence, location, review_status, disease
            
            records = []
            for _, row in df.iterrows():
                # Provide defaults if columns are missing
                records.append((
                    row.get('gene_id'),
                    row.get('gene_name'),
                    row.get('condition'),
                    row.get('variation'),
                    row.get('protein_change'),
                    row.get('consequence'),
                    row.get('location'),
                    row.get('review_status'),
                    row.get('disease')
                ))
            
            # Insert in chunks to avoid memory issues
            chunk_size = 1000
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i + chunk_size]
                cursor.executemany(insert_query, chunk)
                self.connection.commit()
                print(f"Inserted {i + len(chunk)} / {len(records)} records")
                
            print("Data import complete!")
            return True
            
        except Exception as e:
            print(f"Error importing data: {e}")
            return False
            
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

if __name__ == "__main__":
    db = DatabaseManager()
    if db.connect():
        db.create_tables()
        # Adjust path as necessary
        db.import_csv_to_db("../final_genomic_dataset.csv")
        db.close()
