import click
import os
import json
import shutil
import uuid
from datetime import datetime
import filecmp

def get_ignored_files():
    """Returns a list of files/directories to ignore based on .witignore."""
    ignored = {'.wit'}
    if os.path.exists('.witignore'):
        # הוספת encoding מוודאת שפייתון יקרא את הטקסט נכון גם אם הוא נוצר בווינדוס
        with open('.witignore', 'r', encoding='utf-8') as f:
            for line in f:
                # strip מנקה רווחים, ירידות שורה ותווים נסתרים
                line = line.strip()
                if line:
                    ignored.add(line)
    return ignored

def display_status_section(title, files, color):
    if files:
        click.secho(f"\n{title}:", bold=True)
        for f in files:
            click.secho(f"    {f}", fg=color)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@click.group()
def cli():
    """Basic Version Control System (WIT)"""
    pass


@cli.command()
def init():
    """Initializes a new .wit repository."""
    wit_path = '.wit'

    if os.path.exists(wit_path):
        click.echo("Repository already initialized.")
        return

    # יצירת התיקייה הראשית ותיקיות עזר (כמו staging area)
    os.makedirs(wit_path)
    os.makedirs(os.path.join(wit_path, 'staging'))  # כאן נשמור קבצים שעברו add

    # יצירת קובץ קונפיגורציה בסיסי
    metadata = {
        "last_commit": None,
        "version": "1.0"
    }

    with open(os.path.join(wit_path, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4)

    click.echo("Initialized empty WIT repository in .wit/")


@cli.command()
@click.argument('path')
def add(path):
    """Adds a file or directory to the staging area with directory structure."""
    wit_path = '.wit'
    staging_base = os.path.join(wit_path, 'staging')

    if not os.path.exists(wit_path):
        click.echo("Error: Run 'init' first.")
        return

    if not os.path.exists(path):
        click.echo(f"Error: Path {path} does not exist.")
        return

    ignored_list = get_ignored_files()

    # פונקציה פנימית לביצוע ההעתקה בפועל
    def copy_to_staging(target_path):
        # בדיקה אם הנתיב (או אחד מחלקיו) מופיע ב-ignore
        for ignored in ignored_list:
            if ignored in target_path:
                click.echo(f"Path '{target_path}' is ignored by .witignore.")
                return

        destination = os.path.join(staging_base, target_path)

        # יצירת מבנה התיקיות בתוך staging
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        if os.path.isfile(target_path):
            shutil.copy2(target_path, destination)
            click.echo(f"Added: {target_path}")

    if os.path.isfile(path):
        copy_to_staging(path)
    elif os.path.isdir(path):
        # os.walk עובר על כל עץ התיקיות מלמעלה למטה
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                copy_to_staging(full_path)


@cli.command()
@click.option('--message', '-m', required=True, help='Commit message')
def commit(message):
    """Creates a snapshot of the current staging area."""
    wit_path = '.wit'
    staging_path = os.path.join(wit_path, 'staging')
    images_path = os.path.join(wit_path, 'images')

    if not os.path.exists(wit_path):
        click.echo("Error: Run 'init' first.")
        return

    # יצירת תיקיית images אם היא לא קיימת
    os.makedirs(images_path, exist_ok=True)

    # בדיקה אם יש בכלל מה לעשות commit
    if not os.path.exists(staging_path) or not os.listdir(staging_path):
        click.echo("Nothing to commit (staging area is empty).")
        return

    # יצירת ID ייחודי ל-commit
    commit_id = str(uuid.uuid4())[:8]
    commit_dir = os.path.join(images_path, commit_id)

    # העתקת כל מה שיש ב-staging לתיקיית ה-commit החדשה
    shutil.copytree(staging_path, commit_dir)

    # עדכון המטא-דאטה לגבי ה-commit האחרון
    metadata_path = os.path.join(wit_path, 'metadata.json')
    with open(metadata_path, 'r') as f:
        data = json.load(f)

    data['last_commit'] = commit_id

    with open(metadata_path, 'w') as f:
        json.dump(data, f, indent=4)

    click.echo(f"Commit created successfully! ID: {commit_id}")


@cli.command()
def status():
    """Displays the state of the working directory and the staging area."""
    wit_path = '.wit'
    staging_path = os.path.join(wit_path, 'staging')
    images_path = os.path.join(wit_path, 'images')

    if not os.path.exists(wit_path):
        click.echo("Error: Not a WIT repository.")
        return

    ignored_list = get_ignored_files()

    # שליחת מזהה הקומיט האחרון מהמטא-דאטה
    with open(os.path.join(wit_path, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
    last_commit_id = metadata.get('last_commit')
    last_commit_path = os.path.join(images_path, last_commit_id) if last_commit_id else None

    click.echo(f"--- WIT STATUS ---")
    if last_commit_id:
        click.echo(f"On commit: {last_commit_id}")

    # רשימות לריכוז התוצאות
    to_be_committed = []
    not_staged = []
    untracked = []

    # מעבר על כל הקבצים בתיקייה הנוכחית
    for root, dirs, files in os.walk('.'):
        # מניעת כניסה לתיקיות מערכת
        if '.wit' in root or '.venv' in root or '.idea' in root:
            continue

        for file in files:
            full_path = os.path.join(root, file)
            # ניקוי הנתיב שייראה יפה (בלי .\ בהתחלה)
            relative_path = os.path.relpath(full_path, '.')

            if relative_path in ignored_list:
                continue

            staged_file = os.path.join(staging_path, relative_path)

            # 1. בדיקת Untracked (לא ב-staging ולא בקומיט האחרון)
            if not os.path.exists(staged_file):
                # בודקים אם קיים בקומיט האחרון
                exists_in_last = False
                if last_commit_path:
                    last_file = os.path.join(last_commit_path, relative_path)
                    if os.path.exists(last_file):
                        exists_in_last = True

                if not exists_in_last:
                    untracked.append(relative_path)

            # 2. בדיקת Changes not staged (קיים ב-staging אבל התוכן שונה)
            elif not filecmp.cmp(full_path, staged_file, shallow=False):
                not_staged.append(relative_path)

    # 3. בדיקת Changes to be committed (staging מול הקומיט האחרון)
    if os.path.exists(staging_path):
        for root, dirs, files in os.walk(staging_path):
            for file in files:
                staged_file = os.path.join(root, file)
                relative_path = os.path.relpath(staged_file, staging_path)

                if last_commit_path:
                    last_file = os.path.join(last_commit_path, relative_path)
                    # אם הקובץ לא קיים בקומיט או שהתוכן שלו שונה ממה שיש ב-staging
                    if not os.path.exists(last_file) or not filecmp.cmp(staged_file, last_file, shallow=False):
                        to_be_committed.append(relative_path)
                else:
                    # אם אין קומיט בכלל, כל מה שב-staging הוא חדש
                    to_be_committed.append(relative_path)

    # הדפסת התוצאות
    display_status_section("Changes to be committed", to_be_committed, "green")
    display_status_section("Changes not staged for commit", not_staged, "red")
    display_status_section("Untracked files", untracked, "yellow")

@cli.command()
@click.argument('commit_id')
def checkout(commit_id):
    """Restores the working directory to a specific commit state."""
    wit_path = '.wit'
    images_path = os.path.join(wit_path, 'images')
    commit_dir = os.path.join(images_path, commit_id)

    if not os.path.exists(commit_dir):
        click.echo(f"Error: Commit ID {commit_id} not found.")
        return

    # אישור מהמשתמש (כי זה הולך לדרוס קבצים קיימים)
    if not click.confirm("This will overwrite your current files. Continue?"):
        return

    # העתקת הקבצים מהקומיט לתיקיית העבודה
    for item in os.listdir(commit_dir):
        source = os.path.join(commit_dir, item)
        # דריסה של הקבצים הקיימים בתיקייה הראשית
        if os.path.isdir(source):
            if os.path.exists(item):
                shutil.rmtree(item)
            shutil.copytree(source, item)
        else:
            shutil.copy2(source, item)

    # עדכון המטא-דאטה שהקומיט הנוכחי השתנה
    metadata_path = os.path.join(wit_path, 'metadata.json')
    with open(metadata_path, 'r') as f:
        data = json.load(f)
    data['last_commit'] = commit_id
    with open(metadata_path, 'w') as f:
        json.dump(data, f, indent=4)

    click.echo(f"Checked out to commit: {commit_id}")

if __name__ == '__main__':
    cli()