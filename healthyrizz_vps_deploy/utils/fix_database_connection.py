"""
Fix database connection in main.py to handle transaction issues properly.
"""
import os
import sys
from pathlib import Path

def main():
    """Update the database configuration in main.py."""
    print("Looking for main.py...")
    
    # Find main.py file
    main_file = Path('main.py')
    if not main_file.exists():
        print(f"❌ Error: main.py not found in {os.getcwd()}")
        return 1
    
    print(f"✅ Found main.py: {main_file.absolute()}")
    
    # Read the file
    content = main_file.read_text()
    
    # Check for SQLAlchemy engine options
    if 'SQLALCHEMY_ENGINE_OPTIONS' not in content:
        print("❌ SQLALCHEMY_ENGINE_OPTIONS not found in main.py")
        return 1
    
    # Look for pool_pre_ping and isolation_level
    needs_update = False
    if 'isolation_level' not in content or 'pool_pre_ping' not in content:
        needs_update = True
    
    if needs_update:
        print("Updating main.py with improved database connection settings...")
        
        # Find the engine options section
        lines = content.splitlines()
        updated_lines = []
        in_engine_options = False
        engine_options_updated = False
        
        for line in lines:
            if 'SQLALCHEMY_ENGINE_OPTIONS' in line:
                in_engine_options = True
                updated_lines.append(line)
            elif in_engine_options and '}' in line and not engine_options_updated:
                # Add our options before the closing brace
                indentation = line.split('}')[0]
                updated_lines.append(f'{indentation}    "pool_pre_ping": True,')
                updated_lines.append(f'{indentation}    "pool_timeout": 30,')
                updated_lines.append(f'{indentation}    "pool_recycle": 300,')
                updated_lines.append(line)
                in_engine_options = False
                engine_options_updated = True
            else:
                updated_lines.append(line)
        
        # Write the updated content
        main_file.write_text('\n'.join(updated_lines))
        print("✅ Updated main.py with improved database connection settings")
    else:
        print("✅ main.py already has proper connection settings")
    
    # Create backup version of file with original database connection
    backup_file = Path('main.py.bak')
    if not backup_file.exists():
        print("Creating backup of main.py...")
        backup_file.write_text(content)
        print(f"✅ Created backup at {backup_file.absolute()}")
    
    print("\n✅ Database connection fix completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())