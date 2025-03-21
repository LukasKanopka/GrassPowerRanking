from app import app, db
from models import Player, Game, Series
import sqlite3

def migrate_to_series():
    with app.app_context():
        # First create all tables using SQLAlchemy if they don't exist
        print("Creating tables if they don't exist...")
        db.create_all()
        print("Tables created/verified")
        
        # Use SQLite directly to update schema
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            print("Starting migration to series-based schema...")
            
            # 1. Create series table if not exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='series'")
            if not cursor.fetchone():
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS series (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(80) NOT NULL,
                    description VARCHAR(200),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                print("Created series table")
            
            # 2. Check if player table exists before trying to alter it
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player'")
            if cursor.fetchone():
                # Player table exists, check columns
                cursor.execute("PRAGMA table_info(player)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'series_id' not in columns:
                    cursor.execute("ALTER TABLE player ADD COLUMN series_id INTEGER")
                    print("Added series_id column to player table")
            else:
                print("Note: Player table doesn't exist yet, it will be created with series_id column")
            
            # 3. Check if game table exists before trying to alter it
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='game'")
            if cursor.fetchone():
                # Game table exists, check columns
                cursor.execute("PRAGMA table_info(game)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'series_id' not in columns:
                    cursor.execute("ALTER TABLE game ADD COLUMN series_id INTEGER")
                    print("Added series_id column to game table")
            else:
                print("Note: Game table doesn't exist yet, it will be created with series_id column")
            
            # Commit schema changes
            conn.commit()
            
            # 4. Create default series in ORM
            default_series = Series.query.filter_by(name="Default Series").first()
            if not default_series:
                default_series = Series(name="Default Series", description="Initial migration series")
                db.session.add(default_series)
                db.session.commit()
                print(f"Created default series with ID: {default_series.id}")
            
            # 5. Update players with series_id if there are any
            cursor.execute("SELECT COUNT(*) FROM player")
            player_count = cursor.fetchone()[0]
            if player_count > 0:
                cursor.execute("UPDATE player SET series_id = ? WHERE series_id IS NULL", (default_series.id,))
                updated_count = cursor.rowcount
                print(f"Updated {updated_count} players with default series")
            
            # 6. Update games with series_id if there are any
            cursor.execute("SELECT COUNT(*) FROM game")
            game_count = cursor.fetchone()[0]
            if game_count > 0:
                cursor.execute("UPDATE game SET series_id = ? WHERE series_id IS NULL", (default_series.id,))
                updated_count = cursor.rowcount
                print(f"Updated {updated_count} games with default series")
            
            # Commit data changes
            conn.commit()
            
            print("Migration complete!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_to_series()