import yaml, json
import os
import subprocess
from PIL import Image
from PySide6.QtWidgets import QInputDialog, QMessageBox

class Scanner:

    def __init__(self):
        self.config = None
        self.config_path = None

        self.correct_prefixes = None
        self.correct_suffixes = None

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

    def load_config(self, config_filepath):
        if config_filepath == "":
            return "Please enter a config file path"
        if not os.path.exists(config_filepath):
            return "Given config file path doesn't exist"

        try:
            with open(config_filepath, "r") as file:
                self.config = yaml.safe_load(file)
                self.config_path = config_filepath

                self.correct_prefixes = [key if key else "" for key in self.config["naming"]["prefixes"].values()]
                self.correct_suffixes = [key if key else "" for key in self.config["naming"]["suffixes"].values()]
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

        nr_files = 0
        for root, dirs, files in os.walk(directory):
            nr_files += len(files)

            for file in files:
                ext_issue = self.check_extension(file, allowed_formats, root)
                if ext_issue:
                    issues.append(ext_issue)

                prefix_issue = self.check_prefix(file, root)
                if prefix_issue:
                    issues.append(prefix_issue)

                suffix_issue = self.check_suffix(file, root)
                if suffix_issue:
                    issues.append(suffix_issue)

                location_issue = self.check_folder(file, os.path.normpath(root))
                if location_issue:
                    issues.append(location_issue)

                size_issue = self.check_file_size(file, root)
                if size_issue:
                    issues.append(size_issue)

                if self.helper_is_image(os.path.join(root, file)):
                    img_issue = self.check_image_requirements(file, root)
                    if img_issue:
                        issues.append(img_issue)

        return nr_files,issues

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
        print(self.correct_prefixes)

        if not any(file.startswith(prefix) for prefix in self.correct_prefixes):
            return Issue(file, os.path.join(root, file), "Prefix",
                         f"No valid prefix found — expected one of: {', '.join(self.correct_prefixes)}")
        return None

    def check_suffix(self, file, root):
        print(self.correct_suffixes)

        if not any(file.startswith(prefix) for prefix in self.correct_suffixes):
            return Issue(file, os.path.join(root, file), "Suffix",
                         f"No valid suffix found — expected one of: {', '.join(self.correct_suffixes)}")
        return None


    def check_folder(self, file, root):
        folder_map = self.config["folders"]

        for prefix, expected_folder in folder_map.items():
            if file.startswith(prefix):
                if not root.endswith(expected_folder):
                    print(f"Root: {root}")
                    print(f"Expected folder: {expected_folder}")
                    return Issue(file, os.path.join(root, file), "Folder location",
                                 f"'{prefix}' files should be in '{expected_folder}'")
        return None

    def check_file_size(self, file, root):
        size = round(os.path.getsize(os.path.join(root, file)) / (1024 * 1024), 2)
        allowed_size = self.config["max_file_size_mb"]

        if size > allowed_size:
            return Issue(file, os.path.join(root, file), "File size", f"File is {size}MB, only {allowed_size}MB allowed")
        return None

    def helper_is_image(self, filepath):
        try:
            with Image.open(filepath) as img:
                img.verify()
            return True
        except Exception:
            return False

    def check_image_requirements(self, file, root):
        with Image.open(os.path.join(root, file)) as image:
            width, height = image.size

            if self.config["textures"]["require_power_of_two"]:
                if not width == height:
                    return Issue(file, os.path.join(root, file), "Image size",f"{width}x{height} is not power of two")

            max_res = self.config["textures"]["max_resolution"]
            if width > max_res and height > max_res:
                return Issue(file, os.path.join(root, file), "Image size",f"{width}x{height}px is bigger than max resolution: {max_res}px")
            elif width > max_res:
                return Issue(file, os.path.join(root, file), "Image size", f"{width}px (width) is bigger than max resolution: {max_res}px")
            elif height > max_res:
                return Issue(file, os.path.join(root, file), "Image size",f"{height}px (height) is bigger than max resolution: {max_res}px")

    def open_in_explorer(self, files):
        for file in files:
            normalized = os.path.normpath(file)
            subprocess.Popen(f'explorer /select,"{normalized}"')

    def rename_file(self, issue):
        if issue is None:
            return False

        folder_map = self.config["folders"]
        known_prefixes = folder_map.keys()
        dir = os.path.dirname(issue.filepath)
        basename, extension = os.path.splitext(issue.filename)
        new_name, ok = QInputDialog.getText(None, "Rename", "New filename:", text=basename)

        if not ok or not new_name:
            return False
        if not any(new_name.startswith(prefix) for prefix in known_prefixes):
            QMessageBox.warning(None, "Wrong prefix",
                                f"{new_name} does not have an allowed prefix. Allowed prefixes: {', '.join(known_prefixes)}")
            return self.rename_file(issue)

        new_path = os.path.join(dir, f"{new_name}{extension}")
        os.rename(issue.filepath, new_path)
        issue.filepath = new_path
        issue.filename = f"{new_name}{extension}"
        return True

    def move_file(self, issue, scan_directory):
        if issue is None:
            return False

        filepath = issue.filepath
        folder_map = self.config["folders"]
        prefix = issue.filename.split("_")[0] + "_"
        correct_folder = folder_map[prefix]
        correct_folder_path = os.path.normpath(os.path.join(scan_directory, correct_folder))
        print(f"Filepath: {filepath}")

        if not os.path.exists(correct_folder_path):
            reply = QMessageBox.question(None, "Create folder?", f"No existing {correct_folder} folder found. Create folder?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                os.mkdir(correct_folder_path)
            elif reply == QMessageBox.StandardButton.No:
                QMessageBox.information(None, "No folder created", f"No {correct_folder} folder created, move operation cancelled.")
                return False

        destination_path = os.path.join(correct_folder_path, issue.filename)
        print(f"Destination: {destination_path}")
        os.rename(filepath, destination_path)
        return True

    def delete_files(self, issue):
        issue_filepath = issue.filepath
        answer = QMessageBox.question(None, "Delete file", f"Are you sure you want to delete {issue.filename}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            os.remove(issue_filepath)
            return True
        elif answer == QMessageBox.StandardButton.No:
            return False

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


class Issue:

    def __init__(self, filename, filepath, issue, info):
        self.filename = filename
        self.filepath = filepath
        self.issue = issue
        self.info = info