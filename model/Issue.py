from copy import copy
class Issue:
    def __init__(self, id = "", created_at = "", closed_at = "", title = "",labels = "", text_based = False, isChecked = False):
        self.id = id
        self.created_at = created_at
        self.closed_at = closed_at
        self.title = title
        self.labels = labels
        self.text_based = text_based
        self.isChecked = isChecked
        self.commits = []

    def __str__(self):
        issue =  f"Issue:\n\t-Title: {self.title}\n\t-Id: {self.id}\n\t-Created at: {self.created_at}\n\t-Closed at: {self.closed_at}\n\t-Labels: {self.labels}\n"
        for c in self.commits:
            issue+=c.__str__()
        return issue
    
    def toJSON(self, mongoDump = False):
        res = copy(self.__dict__)
        res["commits"] = [commit.toJSON() for commit in self.commits]
        if mongoDump:
            res["manuallyChecked"] = self.isChecked
        return res
