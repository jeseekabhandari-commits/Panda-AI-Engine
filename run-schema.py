import os
import psycopg2
from dotenv import load_dotenv

# Load database credentials from your .env file
load_dotenv()

def apply_schema():
    try:
        # 1. Connect using your secure environment variables
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD")  # Reads your password from .env
        )
        cursor = connection.cursor()
        
        # 2. Read your exact schema.sql file
        print("📖 Reading schema.sql...")
        with open("schema.sql", "r") as schema_file:
            sql_script = schema_file.read()
        
        # 3. Execute the SQL commands
        print("🚀 Applying database tables...")
        cursor.execute(sql_script)
        connection.commit()
        
        print("📊 Relational database tables successfully initialized via schema.sql!")
        
        cursor.close()
        connection.close()
    except Exception as error:
        print(f"❌ Execution failed: {error}")

if __name__ == "__main__":
    apply_schema()