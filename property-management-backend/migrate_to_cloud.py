import os
import psycopg2
from dotenv import load_dotenv

# Load the working connection string from your local .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    try:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not found in environment variables. Make sure your .env file is set up!")

        print("Connecting to cloud database and building tables...")
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        # 1. Clean up existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS tenants CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS applications CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS properties CASCADE;")

        # 2. Create Properties Table
        cursor.execute("""
            CREATE TABLE properties (
                property_id SERIAL PRIMARY KEY,
                address VARCHAR(255) NOT NULL,
                city VARCHAR(100) NOT NULL,
                monthly_rent NUMERIC(10, 2) NOT NULL,
                status VARCHAR(50) DEFAULT 'Empty' CHECK (status IN ('Empty', 'Full'))
            );
        """)

        # 3. Create Applications Table
        cursor.execute("""
            CREATE TABLE applications (
                application_id SERIAL PRIMARY KEY,
                property_id INT REFERENCES properties(property_id) ON DELETE CASCADE,
                applicant_name VARCHAR(255) NOT NULL,
                contact_email VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected'))
            );
        """)

        # 4. Create Tenants Table
        cursor.execute("""
            CREATE TABLE tenants (
                tenant_id SERIAL PRIMARY KEY,
                property_id INT REFERENCES properties(property_id) ON DELETE CASCADE,
                tenant_name VARCHAR(255) NOT NULL,
                payment_status VARCHAR(50) DEFAULT 'Unpaid' CHECK (payment_status IN ('Paid', 'Unpaid', 'Late'))
            );
        """)

        # 5. Populate Sample Properties
        sample_properties = [
            ("123 Main St", "Springfield", 2200.00, "Empty"),
            ("456 Elm St", "Springfield", 1800.00, "Empty"),
            ("789 Oak Ave", "Metro City", 3500.00, "Empty")
        ]
        
        cursor.executemany("""
            INSERT INTO properties (address, city, monthly_rent, status) 
            VALUES (%s, %s, %s, %s);
        """, sample_properties)

        # Commit everything to the cloud
        connection.commit()
        print("Migration successful! Tables created and seeded with sample properties.")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Migration failed! Error: {e}")

if __name__ == "__main__":
    migrate()