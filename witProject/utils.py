import os

def get_ignored_files():
    ignored = {'.wit', '.git', '__pycache__'}
    if os.path.exists('.witignore'):
        with open('.witignore', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignored.add(line)
    return ignored