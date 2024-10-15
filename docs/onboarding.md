# Dataland QA Lab Onboarding Guide

Please follow the steps below to get started with the Dataland QA Lab project.

## Required Software
Please ensure the following software is installed on your machine:
* [Git](https://git-scm.com/downloads)
* [Python 3.12](https://www.python.org/downloads/)
* [PDM](https://pdm-project.org/en/latest/#installation) - a Python package manager
* A recent version of Java (on windows, we recommend [Eclipse Temurin](https://adoptium.net/de/temurin/releases/) 21 for easy installation. On linux, just use your package manager ;))
* An IDE of your choice (we recommend [VS Code](https://code.visualstudio.com/download). Alternatively you may use [IntelliJ Ultimate/PyCharm](https://www.jetbrains.com/de-de/pycharm/download/)))

## First Steps
* Create a [Github](https://github.com) account (if not already available)
* Generate an ssh private-public key pair if you haven't got any yet (run `ssh-keygen -t ed25519"` in your terminal)
* Add your ssh public key to your personal GitHub account [here](https://github.com/settings/keys)
* Clone the project repository to your local machine (run `git clone git@github.com:d-fine/DatalandQARG.git` in your terminal)
* Configure your git username and email (run `git config user.name "Your GitHub Username"` and `git config user.email "email@domain.com"` in the newly created project directory). The email must match one of the addresses you have registered with GitHub.
> [!CAUTION]
> The email address you use here will be publicly visible alongside your commits. Alternatively, you can obtain a pseudonymous email address by going to the [GitHub Email Settings](https://github.com/settings/emails) and activating "Keep my email addresses private".
> You can then use the displayed whatever@users.noreply.github.com address in the git configuration.
* Register an account on [Dataland](https://dataland.com/) and the [Dataland Testing Environment](https://test.dataland.com/)
* Send the following information to a project maintainer (i.e., Andreas and Marc):
  * Your GitHub username and email to become a project collaborator
  * The email address you used to register on Dataland to receive the necessary permissions on the platform
  * Your **public** ssh key so we can provide you with `ssh` access to our servers later

## Configuring Environment Variables
After opening the project in your IDE, you need to configure the required environment variables. Start by copying the `.env.template` file to `.env`.
Anything starting with `AZURE_` will be provided by the project maintainers. 
**After** having received elevated permissions, you can fill in the `DATALAND_API_KEY` field by going to [Dataland API Key Management](https://test.dataland.com/api-key) and creating a new API Key (make sure to select a suitable expiration date)

> [!CAUTION]
> All environment variables are confidential and must not be shared with anyone. Do not commit the `.env` file to the repository.
> Once any of the environment variables are compromised (e.g., by accidentally committing the `.env` file, a source code file containing a secret, or a jupyter notebook where the secret is printed in a cell output), they must be reset **IMMEDIATELY**. Undoing the commit (e.g., by force pushing or by deleting the branch) does not suffice. For resetting the Azure API Keys, contact a project maintainer ASAP.

## Installing Dependencies
To install the project dependencies, run `./bin/setup_dev_environment.sh` in your terminal (Use Git Bash if you are on Windows).

:grin: Congratulations! You are now ready to start contributing to the Dataland QA Lab project. If you have any questions, feel free to ask a project maintainer.
