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
        """
        Load the previously saved UI state from 'ui_state.json',
        deserializes the issue list back into Issue objects.
        :return: Tuple of (state dict, files_checked, issues_found, issues_solved) or None if no saved state
        file exists.
        """
        if not os.path.exists("ui_state.json"):
            return None
        with open("ui_state.json", "r") as f:
            state = json.load(f)
        state["issues"] = [
            Issue(i["filename"], i["filepath"], i["issue"], i["info"])
            for i in state["issues"]
        ]
        files_scanned = state["files_checked"]
        issues_found = state["issues_found"]
        issues_solved = state["issues_solved"]
        return state, files_scanned, issues_found, issues_solved

    def load_config(self, config_filepath):
        """
        Load and parse a YAML config file from the given path, extracts allowed prefixes and suffixes from the naming
        section.
        :param config_filepath: Path to rules config file that should be loaded.
        :return: Error message on failure, or None on success.
        """
        if config_filepath == "":
            return "Please enter a config file path"
        if not os.path.exists(config_filepath):
            return "Given config file path doesn't exist"

        try:
            with open(config_filepath, "r") as file:
                self.config = yaml.safe_load(file)
                self.config_path = config_filepath

                self.correct_prefixes = [key if key else "" for key in self.config["game_ready"]["naming"]["prefixes"].values()]
                self.correct_suffixes = [key if key else "" for key in self.config["game_ready"]["naming"]["suffixes"].values()]
            return None
        except Exception as e:
            return str(e)

    def scan(self, directory, mode):
        """
        Walk the given directory recursively and check every file against all configured rules (extentions, prefix,
        suffix, folder location, file size, and image requirements).
        :param directory: Directory to scan.
        :return: Tuple of (nr_files, issues) where issues is a list of Issue object, or a plain error string if
        preconditions aren't met.
        """
        if directory == "":
            return 0, "Please enter a directory to scan"
        if not os.path.exists(directory):
            return 0, "Given directory to scan doesn't exist"

        if self.config_path is None:
            return 0, "Please enter a config file path"
        if not os.path.exists(self.config_path):
            return 0, "Given config file path doesn't exist"

        issues = []
        allowed_formats = self.config[mode]["allowed_formats"]

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

                size_issue = self.check_file_size(file, root, mode)
                if size_issue:
                    issues.append(size_issue)

                if self.helper_is_image(os.path.join(root, file)):
                    img_issue = self.check_image_requirements(file, root)
                    if img_issue:
                        issues.append(img_issue)

        return nr_files,issues

    def check_extension(self, file, allowed_formats, root):
        """
        Check whether the file's extension is in the list of allowed formats.
        :param file: File to be checked
        :param allowed_formats: Allowed formats specified in config file
        :param root: Root of file to be checked
        :return: Issue object if extension is not allowed, otherwise None
        """
        basename, extension = os.path.splitext(file)
        if extension not in allowed_formats:
            new_issue = Issue(file,
                              os.path.join(root, file),
                              "File format",
                              f"{extension} not allowed")
            return new_issue
        return None

    def check_prefix(self, file, root):
        """
        Check whether the filename starts with one of the configured valid prefixes.
        :param file: File to be checked
        :param root: Root of file to be checked
        :return: Issue object is no valid prefix is found, otherwise None
        """
        if not any(file.startswith(prefix) for prefix in self.correct_prefixes):
            return Issue(file, os.path.join(root, file), "Prefix",
                         f"No valid prefix found — expected one of: {', '.join(self.correct_prefixes)}")
        return None

    def check_suffix(self, file, root):
        """
        Check whether the filename starts with one of the configured valid suffixes.
        :param file: File to be checked
        :param root: Root of file to be checked
        :return: Issue object is no valid prefix is found, otherwise None
        """
        if not any(file.startswith(prefix) for prefix in self.correct_suffixes):
            return Issue(file, os.path.join(root, file), "Suffix",
                         f"No valid suffix found — expected one of: {', '.join(self.correct_suffixes)}")
        return None

    def check_folder(self, file, root):
        """
        Check whether the file is located in the correct folder based on its prefix, as defined in the config's folder
        section.
        :param file: File to be checked
        :param root: Root of the file to be checked
        :return: Issue object if the file is in the wrong folder, otherwise None
        """
        folder_map = self.config["game_ready"]["folders"]

        for prefix, expected_folder in folder_map.items():
            if file.startswith(prefix):
                if not root.endswith(expected_folder):
                    return Issue(file, os.path.join(root, file), "Folder location",
                                 f"'{prefix}' files should be in '{expected_folder}'")
        return None

    def check_file_size(self, file, root, mode):
        """
        Check whether the file's size in MB exceeds the configured maximum.
        :param file: File to be checked
        :param root: Root of file to be checked
        :return: Issue object if the file is too large, otherwise None
        """
        size = round(os.path.getsize(os.path.join(root, file)) / (1024 * 1024), 2)
        allowed_size = self.config[mode]["max_file_size_mb"]

        if size > allowed_size:
            return Issue(file, os.path.join(root, file), "File size", f"File is {size}MB, only {allowed_size}MB allowed")
        return None

    def helper_is_image(self, filepath):
        """
        Attempt to open and verify the file as an image using Pillow.
        :param filepath: Filepath to test
        :return: True if the file is a valid image, False otherwise
        """
        try:
            with Image.open(filepath) as img:
                img.verify()
            return True
        except Exception:
            return False

    def check_image_requirements(self, file, root):
        """
        Check image-specific rules: whether dimensions are equal (power-of-two requirement) and whether width or height
        exceed the configured maximum resolution.
        :param file: File to be checked
        :param root: Root of file to be checked
        :return: Issue object if any requirement is violated, otherwise None
        """
        with Image.open(os.path.join(root, file)) as image:
            width, height = image.size

            if self.config["game_ready"]["textures"]["require_power_of_two"]:
                if not width == height:
                    return Issue(file, os.path.join(root, file), "Image size",f"{width}x{height} is not power of two")

            max_res = self.config["game_ready"]["textures"]["max_resolution"]
            if width > max_res and height > max_res:
                return Issue(file, os.path.join(root, file), "Image size",f"{width}x{height}px is bigger than max resolution: {max_res}px")
            elif width > max_res:
                return Issue(file, os.path.join(root, file), "Image size", f"{width}px (width) is bigger than max resolution: {max_res}px")
            elif height > max_res:
                return Issue(file, os.path.join(root, file), "Image size",f"{height}px (height) is bigger than max resolution: {max_res}px")

    def open_in_explorer(self, files):
        """
        Open each given file path in Windows Explorer with the file selected.
        :param files: Files to be opened in explorer
        """
        for file in files:
            normalized = os.path.normpath(file)
            subprocess.Popen(f'explorer /select,"{normalized}"')

    def rename_file(self, issue):
        """
        Prompt the user for a new filename via a dialog, validate the prefix, and rename the file on disk. Recursively
        re-prompts if the entered name has an invalid prefix.
        :param issue: Issue object containing file to be renamed
        :return: True on success, False if user cancelled
        """
        if issue is None:
            return False

        known_prefixes = self.correct_prefixes
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
        """
        Move the file to its corerct folder based on its prefix and the config's folder data. If the destination folder
        doesn't exist, prompts the user to create it.
        :param issue: Issue object containing file to be moved
        :param scan_directory: Scanned directory to check if destination folder already exists
        :return: True on success, False if user cancelled or folder wasn't created
        """
        if issue is None:
            return False

        filepath = issue.filepath
        folder_map = self.config["game_ready"]["folders"]
        prefix = issue.filename.split("_")[0] + "_"
        correct_folder = folder_map[prefix]
        correct_folder_path = os.path.normpath(os.path.join(scan_directory, correct_folder))

        if not os.path.exists(correct_folder_path):
            reply = QMessageBox.question(None, "Create folder?", f"No existing {correct_folder} folder found. Create folder?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                os.mkdir(correct_folder_path)
            elif reply == QMessageBox.StandardButton.No:
                QMessageBox.information(None, "No folder created", f"No {correct_folder} folder created, move operation cancelled.")
                return False

        destination_path = os.path.join(correct_folder_path, issue.filename)
        os.rename(filepath, destination_path)
        return True

    def delete_files(self, issue):
        """
        Prompt the user for confirmation, then permanently delete the file from disk.
        :param issue: Issue object containing file to be deleted
        :return: True if deleted, False if user declined
        """
        issue_filepath = issue.filepath
        answer = QMessageBox.question(None, "Delete file", f"Are you sure you want to delete {issue.filename}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            os.remove(issue_filepath)
            return True
        elif answer == QMessageBox.StandardButton.No:
            return False

    def save_ui(self, directory, config_path, issues, files_checked, issues_solved):
        """
        Serialize and save the current UI state to 'ui_state.json', including the scanned directory, config path, issue
        list, and scan statistics.
        :param directory: Directory to scan
        :param config_path: Configuration file path
        :param issues: Current issues listed in the table
        :param files_checked: Current number of files checked
        :param issues_solved: Current number of issues solved
        """
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
            ],
            "files_checked": files_checked,
            "issues_found": len(issues),
            "issues_solved": issues_solved
        }
        with open("ui_state.json", "w") as f:
            json.dump(state, f, indent=2)


class Issue:

    def __init__(self, filename, filepath, issue, info):
        self.filename = filename
        self.filepath = filepath
        self.issue = issue
        self.info = info