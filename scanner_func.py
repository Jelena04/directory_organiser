import yaml, json
import os
# from PySide6.QtCore import QObject, Signal

class Scanner:

    # progress_updated = Signal(int)  # emits the current count
    # scan_started = Signal(int)  # emits the total file count

    def __init__(self):
        # super().__init__()
        self.config = None
        self.config_path = None

    # {'folders': {'M_': '/Materials', 'SKM_': '/Meshes/Skeletal', 'SM_': '/Meshes', 'T_': '/Textures'},
    # 'naming': {'prefixes': {'material': 'M_', 'skeletal_mesh': 'SK_', 'static_mesh': 'SM_', 'texture': 'T_'},
    # 'suffixes': {'static_mesh': None, 'skeletal_mesh': None, 'base_color': '_BC', 'metalness': '_M', 'normal': '_N',
    # 'roughness': '_R'}}, 'textures': {'allowed_formats': ['.png', '.tga', '.fbx'], 'max_file_size_mb': 50,
    # 'max_resolution': 2048, 'require_power_of_two': True}}
    def load_config(self, config_filepath):
        if config_filepath == "":
            return "Please enter a config file path"
        if not os.path.exists(config_filepath):
            return "Given config file path doesn't exist"

        try:
            with open(config_filepath, "r") as file:
                self.config = yaml.safe_load(file)
                self.config_path = config_filepath
            return None
        except Exception as e:
            return str(e)

    def scan(self, directory):
        if directory == "":
            return "Please enter a directory to scan"
        if not os.path.exists(directory):
            return "Given directory to scan doesn't exist"

        if self.config_path is None:
            return "Please enter a config file path"
        if not os.path.exists(self.config_path):
            return "Given config file path doesn't exist"

        issues = []
        allowed_formats = self.config["allowed_formats"]
        for root, dirs, files in os.walk(directory):
            # self.scan_started.emit(len(files))
            # count = 0
            for file in files:
                ext_issue = self.check_extension(file, allowed_formats, root)
                if ext_issue:
                    issues.append(ext_issue)

                prefix_issue = self.check_prefix(file, root)
                if prefix_issue:
                    issues.append(prefix_issue)

                location_issue = self.check_folder(file, root)
                if location_issue:
                    issues.append(location_issue)

                size_issue = self.check_file_size(file, root)
                if size_issue:
                    issues.append(size_issue)

                # count += 1
                # self.progress_updated.emit(count)

        return issues

    def check_extension(self, file, allowed_formats, root):
        basename, extension = os.path.splitext(file)
        if extension not in allowed_formats:
            new_issue = Issue(file,
                              os.path.join(root, file),
                              "File format",
                              f"{extension} not allowed")
            return new_issue
        return None

    def check_prefix(self, file, root):
        folder_map = self.config["folders"]
        known_prefixes = folder_map.keys()

        if not any(file.startswith(prefix) for prefix in known_prefixes):
            return Issue(file, os.path.join(root, file), "Prefix",
                         f"No valid prefix found — expected one of: {', '.join(known_prefixes)}")
        return None

    def check_folder(self, file, root):
        folder_map = self.config["folders"]

        for prefix, expected_folder in folder_map.items():
            if file.startswith(prefix):
                if not root.endswith(expected_folder):
                    return Issue(file, os.path.join(root, file), "Folder location",
                                 f"'{prefix}' files should be in '{expected_folder}'")
        return None

    def check_file_size(self, file, root):
        size = round(os.path.getsize(os.path.join(root, file)) / (1024 * 1024),2)
        allowed_size = self.config["max_file_size_mb"]

        if size > allowed_size:
            return Issue(file, os.path.join(root, file), "File size", f"File is {size}MB, only {allowed_size}MB allowed")
        return None

    def save_ui(self, directory, config_path, issues):
        state = {
            "directory": directory,
            "config_path": config_path,
            "issues": [
                {
                    "filename": issue.filename,
                    "filepath": issue.filepath,
                    "issue": issue.issue,
                    "info": issue.info
                }
                for issue in issues
            ]
        }
        with open("ui_state.json", "w") as f:
            json.dump(state, f, indent=2)

    def load_ui(self):
        if not os.path.exists("ui_state.json"):
            return None
        with open("ui_state.json", "r") as f:
            state = json.load(f)
        state["issues"] = [
            Issue(i["filename"], i["filepath"], i["issue"], i["info"])
            for i in state["issues"]
        ]
        return state


class Issue:

    def __init__(self, filename, filepath, issue, info):
        self.filename = filename
        self.filepath = filepath
        self.issue = issue
        self.info = info