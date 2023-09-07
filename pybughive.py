import os
import argparse
import json
import shutil
import subprocess

import pymongo
from dotenv import load_dotenv
from pymongo.errors import ServerSelectionTimeoutError


MONGO_URL = os.getenv('MONGO_URL')
INSTALL_DIRECTORY = os.getenv('INSTALL_DIRECTORY')

if load_dotenv():
    MONGO_URL = os.getenv('MONGO_URL')
    INSTALL_DIRECTORY = os.getenv('INSTALL_DIRECTORY')
elif os.path.exists('./config.py'):
    try:
        from config import MONGO_URL, INSTALL_DIRECTORY
    except ImportError as e:
        print(e)
        exit(1)

if MONGO_URL is None:
    print('Error. Variable MONGO_URL not found.')
    exit(1)

if INSTALL_DIRECTORY is None:
    print('Error. Variable INSTALL_DIRECTORY not found.')
    exit(1)

try:
    client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=100)
    db = client['python_db']['bug_data']
    db.find_one()
except ServerSelectionTimeoutError:
    print('Mongo server connection refused, exiting...')
    exit(1)

WORKDIR = os.getcwd()


def process_query(project, issue_number):
    """
    Downloads all issues of a project and saves them in INSTALL_DIRECTORY as json files.

    :param project: The project to query for in the database
    :param issue_number: The issue number to download
    """

    os.chdir(INSTALL_DIRECTORY)
    project_name = project['repository']
    if not os.path.exists(f'./{project_name}_issues'):
        os.mkdir(f'./{project_name}_issues')
    os.chdir(f'./{project_name}_issues')

    for issue in project['issues']:
        if issue['id'] == int(issue_number):
            with open(f'./{issue["id"]}.json', 'w', encoding='utf8') as f:
                json.dump(issue, f, indent=4)
            os.chdir(WORKDIR)
            return

    print('Error. No such issue number in database')
    exit(1)


def checkout(args):
    """
    Clones a project

    :param args: The project and issue number to check out
    """

    p, issue_number = args.project.split('-')

    project = db.find_one({'repository': p})

    if project is None:
        print('Error. No such project in database')
        exit(1)

    process_query(project, issue_number)

    os.chdir(INSTALL_DIRECTORY)

    with open(f'{p}_issues/{issue_number}.json', 'r') as f:
        issue = json.load(f)

    subprocess.run(f'git clone https://github.com/{project["username"]}/{project["repository"]}', shell=True)

    os.chdir(f'./{p}')
    subprocess.run(f'git checkout -q {issue["commits"][0]["hash"]} --force', shell=True)

    for file in issue['commits'][0]['stat']['tests']:
        if file['status'] != 'removed':
            folders = '/'.join(file['filename'].split('/')[:-1])
            os.makedirs(f'../temp/{folders}', exist_ok=True)
            shutil.copy(file['filename'], f'../temp/{folders}')

    subprocess.run(f'git checkout {issue["commits"][0]["parents"]} --force', shell=True)

    os.chdir(WORKDIR)


def install(args):
    """
    Installs a project by querying the install instructions from the database and running them.

    :param args: The project to install
    """
    p, issue_number = args.project.split('-')

    project = db.find_one({'repository': p})

    if project is None:
        print('Error. No such project in database')
        exit(1)

    os.chdir(INSTALL_DIRECTORY)

    if not os.path.isdir(f'./{p}_issues'):
        os.chdir(WORKDIR)
        checkout(args)
        os.chdir(INSTALL_DIRECTORY)

    if not os.path.exists(f'./{p}_issues/{issue_number}.json'):
        print('Error. No such issue number in database')
        exit(1)

    with open(f'./{p}_issues/{issue_number}.json', 'r', encoding='utf8') as f:
        issue = json.load(f)

    os.chdir(f'./{p}')

    steps = issue['installSteps'] if issue.get('installSteps') else project['installSteps']
    steps = steps.split('\n')
    steps[0] = 'PIPENV_NO_INHERIT=1 PIPENV_YES=1 ' + steps[0]

    for step in steps:
        subprocess.run(step, shell=True, check=True, cwd=os.getcwd())

    os.chdir(WORKDIR)


def test(args):
    """
    Runs all tests that were changed in the specified issue.
    If the --all flag is given, runs all tests in the project instead.

    :param args: The project and issue number to test
    """

    project, issue_number = args.project.split('-')

    os.chdir(INSTALL_DIRECTORY)

    if not os.path.exists(f'./{project}'):
        print('Error. Project not found in working directory, attempting to install.')
        os.chdir(WORKDIR)
        install(args)
        os.chdir(INSTALL_DIRECTORY)

    if not os.path.exists(f'./{project}_issues'):
        print('Error. Issues for project cannot be found.')
        exit(1)

    if not os.path.exists(f'./{project}_issues/{issue_number}.json'):
        print('Error. Issue does not exist.')
        exit(1)

    with open(f'./{project}_issues/{issue_number}.json', 'r', encoding='utf8') as f:
        issue = json.load(f)

    commit = issue['commits'][0]

    os.chdir(f'./{project}')

    for file in commit['stat']['tests']:
        folders = '/'.join(file['filename'].split('/')[:-1])
        os.makedirs(folders, exist_ok=True)
        shutil.copy(f'../temp/{file["filename"]}', folders)

    steps = issue['testSteps'] if not args.full else issue['testStepsFull']
    try:
        for step in steps.split('\n'):
            subprocess.run(step, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.output)

    os.chdir(WORKDIR)


def fix(args):
    """
    Applies the fix for the specified issue.

    :param args: The project and issue number to fix
    """

    p, issue_number = args.project.split('-')

    project = db.find_one({'repository': p})

    if project is None:
        print('Error. No such project in database')
        exit(1)

    os.chdir(INSTALL_DIRECTORY)

    with open(f'{p}_issues/{issue_number}.json', 'r') as f:
        issue = json.load(f)

    os.chdir(f'./{p}')
    subprocess.run(f'git checkout -q {issue["commits"][0]["hash"]} --force', shell=True)

    os.chdir(WORKDIR)
    install(args)


def clean(args):
    """
    Removes temporary files.
    If the --all flag is given, removes all downloaded projects as well.

    :param args: WHat to remove.
    """
    if not args.all:
        os.chdir(INSTALL_DIRECTORY)
        shutil.rmtree('./temp')
        os.chdir(WORKDIR)
    else:
        os.chdir(INSTALL_DIRECTORY)
        for root, dirs, files in os.walk('.', topdown=True):
            for dir in dirs:
                if '_issues' not in dir and dir != 'temp':
                    os.chdir(dir)
                    subprocess.run('pipenv --rm', shell=True, cwd=os.getcwd())
                    os.chdir('..')
            break
        os.chdir(WORKDIR)
        shutil.rmtree(INSTALL_DIRECTORY)


def prepare_env():
    """
    Creates a folder to download data into
    Must set INSTALL_DIRECTORY in config.py
    """
    if not os.path.exists(INSTALL_DIRECTORY):
        os.mkdir(INSTALL_DIRECTORY)

    os.chdir(INSTALL_DIRECTORY)

    if not os.path.exists('./temp'):
        os.mkdir('./temp')

    os.chdir(WORKDIR)


def main():
    prepare_env()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    checkout_parser = subparsers.add_parser('checkout')
    checkout_parser.add_argument('project', metavar='project-issue', help='Downloads the project before the issue was fixed')
    checkout_parser.set_defaults(func=checkout)

    install_parser = subparsers.add_parser('install')
    install_parser.add_argument('project', metavar='project-issue', help='Installs the project')
    install_parser.set_defaults(func=install)

    test_parser = subparsers.add_parser('test')
    test_parser.add_argument('project', metavar='project-issue', help='Tests the project with the tests files included in the fix')
    test_parser.add_argument('--full', action='store_true', help='Runs all tests')
    test_parser.set_defaults(func=test)

    fix_parser = subparsers.add_parser('fix')
    fix_parser.add_argument('project', metavar='project-issue', help='Installs the fix for the issue')
    fix_parser.set_defaults(func=fix)

    clean_parser = subparsers.add_parser('clean')
    clean_parser.add_argument('--all', action='store_true', help='If specified, cleans all downloaded data, otherwise only cleans temporary data.')
    clean_parser.set_defaults(func=clean)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
