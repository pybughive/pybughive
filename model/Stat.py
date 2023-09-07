class Stat:
    def __init__(self, additions, deletions, total, files, tests):
        self.total = total
        self.additions = additions
        self.deletions = deletions
        self.files = files
        self.tests = tests


    def __str__(self):
        return f"\t\t-Additions: {self.additions}\n\t\t-Deletions: {self.deletions}\n\t\t-Total: {self.total}\n\t\t-Files: {self.files}\n"
    
    def toJSON(self):
        return self.__dict__

