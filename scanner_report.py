from jinja2 import Environment, FileSystemLoader
import webbrowser

class ReportGenerator:
    def __init__(self, issues, stats, config, date_time):
        self.issues = issues
        self.stats = stats
        self.config = config
        self.date_time = date_time

        self.generate()
        self.open()

    def generate(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template("report_template.html")
        html = template.render(variable="Yes!")

        with open("report_output/report.html", "w") as f:
            f.write(html)

    def open(self):
        webbrowser.open(r"C:\Users\jelen\Documents\Howest - DAE\second_year_part_2\portfolio\exam_project\B_DirectoryOrganiser\report_output\report.html")