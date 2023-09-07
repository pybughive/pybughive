import json
import os
import subprocess
from model.Issue import Issue
from model.Commit import Commit
from model.Stat import Stat
from copy import copy

class Project(dict):
    def __init__(self, username, repository):
        self.username = username
        self.repository = repository
        self.issues = []

    def __str__(self):
        project =  f"Bugs in {self.repository}: {len(self.issues)}\n"
        for i in self.issues:
            project+=i.__str__()
        return project

    def save_to_json(self):
        with open(f"bugs_in_{self.repository}.json", "w", encoding="utf8") as file:
            json.dump(self.toJSON(), file, indent=2)
    
    def load_from_json(self):
        with open(f"bugs_in_{self.repository}.json", "r", encoding="utf8") as fp:
            self.load_issues_from_list(json.load(fp)['issues'])

    def load_issues_from_list(self, source):
        for issue_info in source:
            cur_issue = Issue(
                issue_info['id'],
                issue_info['created_at'],
                issue_info['closed_at'],
                issue_info['title'],
                issue_info['labels'],
                isChecked = issue_info['manuallyChecked'],
            )
            for cur_commit in issue_info['commits']:
                cur_issue.commits.append(
                    Commit(
                        cur_commit['hash'],
                        cur_commit['commit_date'],
                        cur_commit['parents'],
                        Stat(
                            cur_commit['stat']['additions'],
                            cur_commit['stat']['deletions'],
                            cur_commit['stat']['total'],
                            cur_commit['stat']['files'],
                            cur_commit['stat']['tests'],
                        )
                    )
                )
            self.issues.append(cur_issue)
        

    def toJSON(self, mongoDump = False):
        res = copy(self.__dict__)
        res["issues"] = [issue.toJSON(mongoDump) for issue in self.issues]
        if mongoDump:
            res["installSteps"] = ""
        return res

    def clone(self):
        if not os.path.exists(f'repo/{self.repository}'):
            github_repository_url = f'https://github.com/{self.username}/{self.repository}.git'
            subprocess.run(f'git clone {github_repository_url} repo/{self.repository}', check=True, shell=True)
