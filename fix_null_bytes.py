#!/usr/bin/env python3
"""
Script to clean null bytes from corrupted files
"""
import os

def clean_null_bytes():
    files_to_check = [
        'start_app.py', 
        'run_healthyrizz.py', 
        'routes/main_routes.py', 
        'routes/admin_routes.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    
                if b'\x00' in content:
                    print(f'❌ {file_path} contains null bytes')
                    # Remove null bytes
                    clean_content = content.replace(b'\x00', b'')
                    with open(file_path, 'wb') as clean_f:
                        clean_f.write(clean_content)
                    print(f'✅ {file_path} cleaned')
                else:
                    print(f'✅ {file_path} is clean')
                    
            except Exception as e:
                print(f'❌ Error with {file_path}: {e}')
        else:
            print(f'📁 {file_path} not found')

if __name__ == '__main__':
    clean_null_bytes() 