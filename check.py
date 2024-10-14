import os
import django

# Set the environment variable for Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_project.settings")  # Replace with your project name

# Setup Django
django.setup()

from django.db import connection

def list_all_tables():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        tables = cursor.fetchall()
    
    # Print the table names
    for table in tables:
        print(table[0])

# Example usage
if __name__ == "__main__":
    list_all_tables()
