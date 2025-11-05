#!/usr/bin/env python3
"""
Database initialization script for Career Roadmap Generator
Run this script to set up the database with sample data
"""

import os
import sys
from database import DatabaseManager

def main():
    """Initialize the database and insert sample data."""
    print("🚀 Initializing Career Roadmap Generator Database...")
    print("=" * 60)
    
    try:
        # Create database manager (this will automatically initialize the database)
        db_manager = DatabaseManager()
        
        print("✅ Database tables created successfully!")
        
        # Get and display statistics
        stats = db_manager.get_database_stats()
        print(f"\n📊 Database Statistics:")
        print(f"   • Users: {stats['users']}")
        print(f"   • Career Paths: {stats['career_paths']}")
        print(f"   • Skills: {stats['skills']}")
        print(f"   • Roadmaps: {stats['roadmaps']}")
        
        # Display sample career paths
        print(f"\n🎯 Sample Career Paths Available:")
        career_paths = db_manager.get_sample_career_paths(limit=5)
        for i, path in enumerate(career_paths, 1):
            print(f"   {i}. {path['title']} ({path['duration_weeks']} weeks)")
        
        # Display sample skills by category
        print(f"\n🛠  Sample Skills by Category:")
        skills = db_manager.get_all_skills()
        skills_by_category = {}
        for skill in skills:
            category = skill['category']
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill['name'])
        
        for category, skill_list in skills_by_category.items():
            print(f"   • {category}: {', '.join(skill_list[:5])}")
            if len(skill_list) > 5:
                print(f"     ... and {len(skill_list) - 5} more")
        
        print(f"\n✅ Database initialization completed successfully!")
        print(f"📁 Database file: {os.path.abspath(db_manager.db_path)}")
        print(f"\n🚀 You can now run the Streamlit app with:")
        print(f"   streamlit run app.py --server.port 5000")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
