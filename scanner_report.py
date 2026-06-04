from jinja2 import Environment, FileSystemLoader
import webbrowser


class ReportGenerator:

    def __init__(self, issues, stats, config, date_time, mode):
        self.issues = issues
        self.stats = stats
        self.config = config
        self.date_time = date_time
        self.mode = mode

        self.generate()
        self.open()

    def generate(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template("report_template.html")

        pass_rate = self.calc_pass_rate()

        html = template.render(date_time=self.date_time, mode=self.mode, config=self.config, stats=self.stats, pass_rate=pass_rate, issues=self.issues)

        with open("report_output/report.html", "w", encoding="utf-8") as f:
            f.write(html)

    def calc_pass_rate(self):
        pass_rate = 100-round((self.stats["problems_found"]/self.stats["files_scanned"])*100)
        return pass_rate

    def open(self):
        webbrowser.open(r"C:\Users\jelen\Documents\Howest - DAE\second_year_part_2\portfolio\exam_project\B_DirectoryOrganiser\report_output\report.html")