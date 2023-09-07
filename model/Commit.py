from copy import copy

class Commit:
    def __init__(self, hash, commit_date, parents, stat):
        self.hash = hash
        self.commit_date = commit_date
        self.parents = parents
        self.stat = stat


    def __str__(self):
        return f"\t-Commit:\n\t\t-Hash: {self.hash}\n\t\t-Parents: {self.parents}\n\t\t-Date: {self.commit_date}\n"+self.stat.__str__()
    
    def toJSON(self):
        res = copy(self.__dict__)
        res["stat"] = self.stat.toJSON()
        return res