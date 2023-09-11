# PyBugHive

## Projects

PyBugHive is a benchmark of 105 real, manually validated bugs from 10 Python projects:

* [psf/black](https://github.com/psf/black)
* [cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter)
* [Rapptz/discord.py](https://github.com/Rapptz/discord.py)
* [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade)
* [numpy/numpy](https://github.com/numpy/numpy)
* [pandas-dev/pandas](https://github.com/pandas-dev/pandas)
* [python-poetry/poetry](https://github.com/python-poetry/poetry)
* [saltstack/salt](https://github.com/saltstack/salt)
* [scrapy/scrapy](https://github.com/scrapy/scrapy)
* [explosion/spaCy](https://github.com/explosion/spaCy)

## Using PyBugHive
Using PyBugHive is straightforward as all commands (besides the clean command) follow the same pattern: python pybughive.py {command} {project}-{issue}, where {project} is the name of the selected project’s repository and {issue} is the number of the selected issue. The possible commands are the following:

* checkout: Clones the selected repository and checks out the appropriate commit hash. This should be the first command when using this tool.
* install: Searches for the appropriate install steps and runs them. This should be the second command.
* test: Runs the appropriate test steps. When used with the --all flag, instead of testing just the file(s) included in the issue, it runs all tests.
* fix: Installs the fix for the selected bug.
* clean: This command does not need a project or an issue number. It deletes all temporary files generated during the run. When used with the --all flag, it deletes everything the tool downloaded, including the repositories.

  
Before PyBugHive can be used, it needs to be configured by setting the INSTALL_DIRECTORY, which specifies where to download the repositories, and the MONGO_URL, which specifies the connection string to MongoDB. There are three ways the user can provide these:

1. Add them to the system’s environment variables.
2. Create a .env file in the PyBugHive project root and add the above variables to it.
3. Same as 2), but with a config.py file. We offer a Docker image with everything pre-installed, which further helps with an isolated run of PyBugHive. Moreover, we provide an installer script (setup.sh) that installs all required Python versions and other dependencies needed to successfully run any bug presented in our database. However, for better isolation, we recommend using the Docker environment.
  
## Offline version
A major concern for bug databases is to continuously ensure
the reproducibility of bugs, for example, due to
continuously changing dependencies and improperly locked
dependency versions.
This is the main reason why we created an offline version
of PyBugHive. This version of the dataset does not need a
database connection or even an internet connection so the
database can be used in a completely offline environment as
well. For each bug, we downloaded the specific project both
before and after the fix, created the corresponding environment,
and compressed everything into a zip file. This way,
the users do not have to install the particular project manually;
the provided virtual environment is already prepared, and the
tests can be run. The drawback of this version is its large size.

