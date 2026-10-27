import uuid
from backend.src.utils.hash_password import hash_password
from backend.src.utils.db_connection import OpenDb

try:
    with OpenDb() as cursor:
        # create roles table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id CHAR(36) PRIMARY KEY,
            role VARCHAR(50) NOT NULL UNIQUE
        );
        """)

        # create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id CHAR(36) PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(128) NOT NULL,
            role_id CHAR(36),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );
        """)

        # insert default roles (ignore if already exists)
        cursor.execute("""
        INSERT IGNORE INTO roles (id, role) 
        VALUES (%s, 'admin'), (%s, 'user')
        """, (str(uuid.uuid4()), str(uuid.uuid4())))

        # fetch role IDs
        cursor.execute("SELECT id FROM roles WHERE role='admin'")
        admin_role_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM roles WHERE role='user'")
        user_role_id = cursor.fetchone()[0]

        # hash password with bcrypt
        hashed_password = hash_password("password123")

        # insert default users (ignore if already exists based on username)
        cursor.execute("""
        INSERT IGNORE INTO users (id, username, password, role_id)
        VALUES (%s, 'admin', %s, %s)
        """, (str(uuid.uuid4()), hashed_password, admin_role_id))

        cursor.execute("""
        INSERT IGNORE INTO users (id, username, password, role_id)
        VALUES (%s, 'testuser', %s, %s)
        """, (str(uuid.uuid4()), hashed_password, user_role_id))

        print("Database setup completed successfully!")

        print(f"Database created with default roles & users: ")

except Exception as e:
    print(f"Error: {e}")
