"""
Setup script for Supabase database initialization.
Run this once to create the necessary table for PromoAgent.
"""
from src.supabase.client import supabase

def create_commented_threads_table():
    """
    Create the commented_threads table in Supabase.
    Note: This requires RLS (Row Level Security) to be disabled or properly configured.
    """
    try:
        # Create the table using SQL
        sql = """
        CREATE TABLE IF NOT EXISTS commented_threads (
            id BIGSERIAL PRIMARY KEY,
            thread_id TEXT UNIQUE NOT NULL,
            thread_title TEXT,
            subreddit TEXT,
            commented_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create index for faster lookups
        CREATE INDEX IF NOT EXISTS idx_thread_id ON commented_threads(thread_id);
        CREATE INDEX IF NOT EXISTS idx_commented_at ON commented_threads(commented_at);
        """
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ Table 'commented_threads' created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        print("\n📝 Manual Setup Instructions:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Run this SQL:")
        print("""
        CREATE TABLE commented_threads (
            id BIGSERIAL PRIMARY KEY,
            thread_id TEXT UNIQUE NOT NULL,
            thread_title TEXT,
            subreddit TEXT,
            commented_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX idx_thread_id ON commented_threads(thread_id);
        CREATE INDEX idx_commented_at ON commented_threads(commented_at);
        """)

def test_supabase_connection():
    """
    Test the Supabase connection and basic operations.
    """
    try:
        # Test insert
        test_data = {
            'thread_id': 'test_thread_123',
            'thread_title': 'Test Thread',
            'subreddit': 'test'
        }
        
        result = supabase.table('commented_threads').insert(test_data).execute()
        print("✅ Insert test successful!")
        
        # Test select
        result = supabase.table('commented_threads').select('*').eq('thread_id', 'test_thread_123').execute()
        if len(result.data) > 0:
            print("✅ Select test successful!")
        
        # Test delete
        supabase.table('commented_threads').delete().eq('thread_id', 'test_thread_123').execute()
        print("✅ Delete test successful!")
        
        print("🎉 All Supabase tests passed!")
        
    except Exception as e:
        print(f"❌ Supabase test failed: {e}")

if __name__ == "__main__":
    print("=== PromoAgent Supabase Setup ===")
    
    # Test connection first
    print("\n1. Testing Supabase connection...")
    test_supabase_connection()
    
    # Create table
    print("\n2. Creating table...")
    create_commented_threads_table()
    
    print("\n✅ Setup complete! You can now use Supabase for duplicate tracking.") 