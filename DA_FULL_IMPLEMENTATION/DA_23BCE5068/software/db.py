import sqlite3

DB_NAME = 'locker_system.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Lockers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lockers (
            locker_id TEXT PRIMARY KEY,
            address TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            total_deliveries INTEGER DEFAULT 0
        )
    ''')
    
    # Deliveries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deliveries (
            delivery_id TEXT PRIMARY KEY,
            customer_phone TEXT NOT NULL,
            customer_email TEXT,
            locker_id TEXT NOT NULL,
            agent_qr TEXT NOT NULL,
            customer_qr TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending_delivery',
            priority TEXT DEFAULT 'standard',
            package_size TEXT DEFAULT 'medium',
            delivery_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            deposited_at TIMESTAMP,
            picked_up_at TIMESTAMP,
            FOREIGN KEY (locker_id) REFERENCES lockers (locker_id)
        )
    ''')
    
    # Access logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            locker_id TEXT,
            delivery_id TEXT,
            role TEXT,
            qr_token TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action TEXT,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (locker_id) REFERENCES lockers (locker_id),
            FOREIGN KEY (delivery_id) REFERENCES deliveries (delivery_id)
        )
    ''')
    
    # System metrics table for analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    ''')
    
    # Add indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deliveries_status ON deliveries(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deliveries_created_at ON deliveries(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deliveries_locker_id ON deliveries(locker_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_logs_locker_id ON access_logs(locker_id)')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Database initialized.')
