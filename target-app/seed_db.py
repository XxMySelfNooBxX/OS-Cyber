import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyber_bank.db")

def init_and_seed_db(db_path=DB_PATH):
    print(f"[*] Initializing and seeding SQLite database at: {db_path}")
    
    # Remove existing db if fresh seed is needed
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            account_number TEXT NOT NULL UNIQUE,
            balance REAL NOT NULL,
            pan_card TEXT NOT NULL UNIQUE
        )
    """)
    
    # 2. Create audit_logs table for digital forensics
    cursor.execute("""
        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            account_id INTEGER,
            ip_address TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT NOT NULL
        )
    """)
    
    # 3. Seed customers with realistic Indian banking records
    customers_data = [
        (1001, "Rahul Sharma", "rahul.sharma@cyberbank.local", "ACC-98214532", 125400.50, "ABCDE1234F"),
        (1002, "Priya Verma", "priya.verma@cyberbank.local", "ACC-88349120", 342100.00, "BKLPV5678Q"),
        (1003, "Amit Patel", "amit.patel@cyberbank.local", "ACC-77491023", 89500.75, "CRXPT9012M"),
        (1004, "Sneha Kulkarni", "sneha.k@cyberbank.local", "ACC-66382019", 540250.25, "DZNMS3456L"),
        (1005, "Vikram Malhotra", "vikram.m@cyberbank.local", "ACC-55491204", 1200450.00, "EKJPM7890R")
    ]
    
    cursor.executemany("""
        INSERT INTO customers (id, full_name, email, account_number, balance, pan_card)
        VALUES (?, ?, ?, ?, ?, ?)
    """, customers_data)
    
    # 4. Seed audit logs with digital forensic trail
    now_iso = datetime.now(timezone.utc).isoformat()
    audit_data = [
        (now_iso, "SYSTEM_INIT", None, "127.0.0.1", "SUCCESS", "SQLite Database initialized with schema v1.0 and seeded records"),
        (now_iso, "AUTH_LOGIN", 1001, "192.168.1.45", "SUCCESS", "Customer Rahul Sharma logged into web portal"),
        (now_iso, "BALANCE_QUERY", 1001, "192.168.1.45", "SUCCESS", "Account ACC-98214532 balance requested"),
        (now_iso, "AUTH_LOGIN", 1002, "192.168.1.88", "SUCCESS", "Customer Priya Verma authenticated via session token"),
        (now_iso, "FUNDS_TRANSFER", 1002, "192.168.1.88", "SUCCESS", "NEFT transfer initiated: INR 25,000 to ACC-98214532"),
        (now_iso, "KYC_VERIFICATION", 1003, "10.0.0.12", "SUCCESS", "PAN Card verification completed for Amit Patel"),
        (now_iso, "SECURITY_ALERT", 1004, "203.0.113.19", "FLAGGED", "Multiple rapid API query requests detected"),
        (now_iso, "HIGH_VALUE_TX", 1005, "127.0.0.1", "SUCCESS", "Corporate RTGS credit recorded: INR 500,000")
    ]
    
    cursor.executemany("""
        INSERT INTO audit_logs (timestamp, event_type, account_id, ip_address, status, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """, audit_data)
    
    conn.commit()
    conn.close()
    print("[+] Database cyber_bank.db successfully initialized and seeded with 5 customers and 8 audit logs.")

if __name__ == "__main__":
    init_and_seed_db()
