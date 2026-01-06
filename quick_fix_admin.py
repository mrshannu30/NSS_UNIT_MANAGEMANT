#!/usr/bin/env python3
"""
Quick Fix Script for Admin Login Issue
Run this script to fix the admin password problem
"""

import bcrypt
import sys

print("\n" + "="*70)
print("NSS MANAGEMENT SYSTEM - ADMIN PASSWORD FIX")
print("="*70 + "\n")

# Step 1: Install required packages
print("Step 1: Checking required packages...")
try:
    import MySQLdb
    print("✅ MySQLdb is installed")
except ImportError:
    print("❌ MySQLdb not found. Installing...")
    import os
    os.system('pip install mysqlclient')
    import MySQLdb
    print("✅ MySQLdb installed successfully")

# Step 2: Get database credentials
print("\n" + "-"*70)
print("Step 2: Database Configuration")
print("-"*70)

MYSQL_HOST = input("Enter MySQL host [localhost]: ").strip() or 'localhost'
MYSQL_USER = input("Enter MySQL username [root]: ").strip() or 'root'
MYSQL_PASSWORD = input("Enter MySQL password: ").strip()
MYSQL_DB = input("Enter database name [nss_management]: ").strip() or 'nss_management'

# Step 3: Get admin details
print("\n" + "-"*70)
print("Step 3: Admin Account Details")
print("-"*70)

ADMIN_ID = input("Enter Admin ID [NSS_ADMIN_001]: ").strip() or 'NSS_ADMIN_001'
USERNAME = input("Enter username [admin]: ").strip() or 'admin'
PASSWORD = input("Enter new password [Admin@123]: ").strip() or 'Admin@123'
EMAIL = input("Enter admin email [admin@college.edu]: ").strip() or 'admin@college.edu'
FULL_NAME = input("Enter admin full name [NSS Administrator]: ").strip() or 'NSS Administrator'

# Step 4: Create/Update admin
print("\n" + "-"*70)
print("Step 4: Creating/Updating Admin Account...")
print("-"*70 + "\n")

try:
    # Connect to database
    print("🔄 Connecting to database...")
    db = MySQLdb.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB
    )
    print("✅ Connected to database successfully")
    
    cursor = db.cursor()
    
    # Hash the password
    print("🔄 Hashing password...")
    password_bytes = PASSWORD.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    hashed_password_str = hashed_password.decode('utf-8')
    print("✅ Password hashed successfully")
    
    # Delete existing admin
    print("🔄 Removing old admin account (if exists)...")
    cursor.execute("DELETE FROM admins WHERE admin_id = %s", (ADMIN_ID,))
    print("✅ Old account removed")
    
    # Insert new admin
    print("🔄 Creating new admin account...")
    cursor.execute("""
        INSERT INTO admins (admin_id, username, password, email, full_name, is_active)
        VALUES (%s, %s, %s, %s, %s, TRUE)
    """, (ADMIN_ID, USERNAME, hashed_password_str, EMAIL, FULL_NAME))
    
    db.commit()
    print("✅ Admin account created successfully")
    
    # Verify the account
    print("\n🔄 Verifying admin account...")
    cursor.execute("SELECT * FROM admins WHERE admin_id = %s", (ADMIN_ID,))
    result = cursor.fetchone()
    
    if result:
        print("✅ Admin account verified in database")
        
        # Test password
        print("\n🔄 Testing password...")
        cursor.execute("SELECT password FROM admins WHERE admin_id = %s", (ADMIN_ID,))
        stored_password = cursor.fetchone()[0].encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, stored_password):
            print("✅ Password test successful!")
        else:
            print("❌ Password test failed!")
            sys.exit(1)
    else:
        print("❌ Admin account not found after creation!")
        sys.exit(1)
    
    cursor.close()
    db.close()
    
    # Success message
    print("\n" + "="*70)
    print("✅✅✅ ADMIN ACCOUNT SETUP COMPLETE! ✅✅✅")
    print("="*70)
    print("\n📋 Your Login Credentials:")
    print("-"*70)
    print(f"🆔 Admin ID:  {ADMIN_ID}")
    print(f"👤 Username:  {USERNAME}")
    print(f"🔑 Password:  {PASSWORD}")
    print(f"📧 Email:     {EMAIL}")
    print("-"*70)
    print("\n🌐 Login URL: http://localhost:5000/login")
    print("\n⚠️  IMPORTANT:")
    print("   1. Change this password after your first login!")
    print("   2. Use Admin ID (not username) in the login form")
    print("   3. Select 'Admin' tab before logging in")
    print("\n" + "="*70 + "\n")
    
    input("Press Enter to exit...")
    
except MySQLdb.Error as e:
    print(f"\n❌ Database Error: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Make sure MySQL server is running")
    print("   2. Check if database 'nss_management' exists")
    print("   3. Verify your MySQL username and password")
    print("   4. Try connecting manually: mysql -u root -p")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
    print("\n💡 Please check:")
    print("   1. Python version (should be 3.8+)")
    print("   2. All required packages are installed")
    print("   3. Database connection details are correct")
    sys.exit(1)