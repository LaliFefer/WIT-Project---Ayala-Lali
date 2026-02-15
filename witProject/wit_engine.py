import os
import json
import shutil
import uuid
import filecmp
from datetime import datetime
from utils import get_ignored_files


class WitEngine:
    def __init__(self):
        self.wit_path = '.wit'
        self.staging_path = os.path.join(self.wit_path, 'staging')
        self.images_path = os.path.join(self.wit_path, 'images')
        self.metadata_path = os.path.join(self.wit_path, 'metadata.json')

    def init(self):
        if os.path.exists(self.wit_path):
            raise Exception("Repository already initialized.")

        os.makedirs(self.wit_path)
        os.makedirs(self.staging_path)
        os.makedirs(self.images_path)

        metadata = {"last_commit": None, "version": "1.0"}
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)

    def add(self, path):
        if not os.path.exists(self.wit_path):
            raise Exception("Run 'init' first.")

        ignored = get_ignored_files()

        def _copy_item(target):
            if any(ign in target for ign in ignored):
                return

            dest = os.path.join(self.staging_path, target)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if os.path.isfile(target):
                shutil.copy2(target, dest)

        if os.path.isfile(path):
            _copy_item(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    _copy_item(os.path.join(root, file))

    def commit(self, message):
        if not os.path.exists(self.staging_path) or not os.listdir(self.staging_path):
            return None

        commit_id = str(uuid.uuid4())[:8]
        commit_dir = os.path.join(self.images_path, commit_id)
        shutil.copytree(self.staging_path, commit_dir)

        with open(self.metadata_path, 'r') as f:
            data = json.load(f)

        data['last_commit'] = commit_id
        with open(self.metadata_path, 'w') as f:
            json.dump(data, f, indent=4)

        return commit_id

    def get_status(self):
        # מחזירה מילון עם כל המידע הנדרש במקום להדפיס
        with open(self.metadata_path, 'r') as f:
            metadata = json.load(f)

        last_commit_id = metadata.get('last_commit')
        last_commit_path = os.path.join(self.images_path, last_commit_id) if last_commit_id else None

        status_data = {
            "last_commit": last_commit_id,
            "to_be_committed": [],
            "not_staged": [],
            "untracked": []
        }

        ignored = get_ignored_files()

        for root, _, files in os.walk('.'):
            if '.wit' in root: continue
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), '.')
                if rel_path in ignored: continue

                staged_file = os.path.join(self.staging_path, rel_path)

                if not os.path.exists(staged_file):
                    exists_in_last = last_commit_path and os.path.exists(os.path.join(last_commit_path, rel_path))
                    if not exists_in_last:
                        status_data["untracked"].append(rel_path)
                elif not filecmp.cmp(rel_path, staged_file, shallow=False):
                    status_data["not_staged"].append(rel_path)

        # לוגיקה ל-to_be_committed (השוואה בין staging לקומיט אחרון)
        # ... (דומה לקוד המקורי שלך רק מחזיר רשימה)
        return status_data