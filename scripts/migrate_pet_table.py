import sqlite3
import os

PET_DB_PATH = os.environ.get('PET_DB_PATH', 'pet_game.db')

def migrate_pet_table():
    conn = sqlite3.connect(PET_DB_PATH)
    cur = conn.cursor()
    # 1. Rename old table
    cur.execute('''
        ALTER TABLE pet RENAME TO pet_old;
    ''')
    # 2. Create new table with username as TEXT PRIMARY KEY
    cur.execute('''
        CREATE TABLE pet (
            id TEXT PRIMARY KEY,
            name TEXT, species TEXT, gender TEXT,
            hunger INTEGER DEFAULT 70, happiness INTEGER DEFAULT 70,
            energy INTEGER DEFAULT 70, hygiene INTEGER DEFAULT 80,
            coins INTEGER DEFAULT 0, xp INTEGER DEFAULT 0,
            stage TEXT DEFAULT 'Baby', adventure_end REAL DEFAULT 0,
            last_updated REAL, hat TEXT DEFAULT 'None'
        );
    ''')
    # 3. Copy data: use rowid or best guess for username (if possible)
    # If old id was username, just copy; if not, skip or set as 'user{id}'
    for row in cur.execute('SELECT * FROM pet_old'):
        old_id, name, species, gender, hunger, happiness, energy, hygiene, coins, xp, stage, adventure_end, last_updated, hat = row
        # Try to use old_id as username if it looks like a string, else make a fake username
        username = str(old_id)
        cur.execute('''
            INSERT OR REPLACE INTO pet (id, name, species, gender, hunger, happiness, energy, hygiene, coins, xp, stage, adventure_end, last_updated, hat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, name, species, gender, hunger, happiness, energy, hygiene, coins, xp, stage, adventure_end, last_updated, hat))
    conn.commit()
    cur.execute('DROP TABLE pet_old;')
    conn.commit()
    conn.close()
    print('Pet table migration complete.')

if __name__ == '__main__':
    migrate_pet_table()
