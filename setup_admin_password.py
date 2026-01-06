"""
Admin Setup Script for NSS Management System
This script creates/updates the admin account with proper password hashing
"""

import bcrypt
import MySQLdb

# Database Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '3015'  # CHANGE THIS
MYSQL_DB = 'nss_management'

# Admin Details
ADMIN_ID = 'NSS_ADMIN_001'
USERNAME = 'admin'
PASSWORD = 'Admin2024'  # You can change this
EMAIL = 'admin@college.edu'
FULL_NAME = 'NSS Administrator'

def create_admin():
    """Create or update admin account with hashed password"""
    try:
        # Connect to database
        print("Connecting to database...")
        db = MySQLdb.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            db=MYSQL_DB
        )
        cursor = db.cursor()
        
        # Hash the password
        print("Hashing password...")
        password_bytes = PASSWORD.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        hashed_password_str = hashed_password.decode('utf-8')
        
        # Check if admin exists
        cursor.execute("SELECT id FROM admins WHERE admin_id = %s", (ADMIN_ID,))
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            # Update existing admin
            print(f"Updating existing admin account: {USERNAME}")
            cursor.execute("""
                UPDATE admins 
                SET username = %s, password = %s, email = %s, full_name = %s
                WHERE admin_id = %s
            """, (USERNAME, hashed_password_str, EMAIL, FULL_NAME, ADMIN_ID))
        else:
            # Insert new admin
            print(f"Creating new admin account: {USERNAME}")
            cursor.execute("""
                INSERT INTO admins (admin_id, username, password, email, full_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (ADMIN_ID, USERNAME, hashed_password_str, EMAIL, FULL_NAME))
        
        db.commit()
        
        print("\n" + "="*60)
        print("✅ Admin account created/updated successfully!")
        print("="*60)
        print(f"Admin ID: {ADMIN_ID}")
        print(f"Username: {USERNAME}")
        print(f"Password: {PASSWORD}")
        print(f"Email: {EMAIL}")
        print("="*60)
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        print("="*60 + "\n")
        
        cursor.close()
        db.close()
        
    except MySQLdb.Error as e:
        print(f"\n❌ Database Error: {e}")
        print("\nPlease check:")
        print("1. MySQL server is running")
        print("2. Database credentials are correct in this script")
        print("3. Database 'nss_management' exists")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

def test_login():
    """Test the admin login credentials"""
    try:
        print("\nTesting login credentials...")
        db = MySQLdb.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            db=MYSQL_DB
        )
        cursor = db.cursor()
        
        cursor.execute("SELECT password FROM admins WHERE admin_id = %s", (ADMIN_ID,))
        result = cursor.fetchone()
        
        if result:
            stored_password = result[0].encode('utf-8')
            test_password = PASSWORD.encode('utf-8')
            
            if bcrypt.checkpw(test_password, stored_password):
                print("✅ Password verification successful!")
                print("You can now login with these credentials.")
            else:
                print("❌ Password verification failed!")
        else:
            print("❌ Admin account not found!")
            
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("NSS Management System - Admin Setup")
    print("="*60 + "\n")
    
    # Update these before running
    print("⚠️  BEFORE RUNNING:")
    print("1. Update MYSQL_PASSWORD in this script")
    print("2. Ensure MySQL server is running")
    print("3. Ensure database 'nss_management' exists")
    print("\n" + "="*60 + "\n")
    
    response = input("Have you updated the configuration? (yes/no): ")
    
    if response.lower() == 'yes':
        create_admin()
        test_login()
    else:
        print("\n⚠️  Please update the configuration first!")
        print("Edit this file and change MYSQL_PASSWORD")