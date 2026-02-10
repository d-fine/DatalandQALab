# Dataland QA Lab Onboarding Guide

Please follow the steps below to get started with the Dataland QA Lab project. There are two ways to get the datalandqalab running on your computer. It's recommended to use devcontainers as this ensures an equal setup on everyone's computer.

* [Using devcontainers](#1-Using-devcontainers) (recommended)
* [Installing manually](#2-Installing-manually) 

## 1. Using devcontainers

### Required software
Make sure the following software is installed locally on your computer:
* [Git](https://git-scm.com/downloads)
* [Docker](https://docker.com/)

### First steps
* Create a [Github](https://github.com) account (if not already available)
* Generate an ssh private-public key pair if you haven't got any yet (run `ssh-keygen -t ed25519` in your terminal)
* Add your ssh public key to your personal GitHub account [here](https://github.com/settings/keys)
* Clone the project repository to your local machine (run `git clone git@github.com:d-fine/DatalandQaLab.git` in your terminal). Especially on Windows, take care to select a relatively short base path because of Windows max path length restrictions.
* Configure your git username and email (run `git config user.name "Your GitHub Username"` and `git config user.email "email@domain.com"` in the newly created project directory). The email must match one of the addresses you have registered with GitHub.
> [!CAUTION]
> The email address you use here will be publicly visible alongside your commits. Alternatively, you can obtain a pseudonymous email address by going to the [GitHub Email Settings](https://github.com/settings/emails) and activating "Keep my email addresses private".
> You can then use the displayed whatever@users.noreply.github.com address in the git configuration.

### Contact the Maintainers
Before proceeding further, please text Marc via your usual communication channel (e.g., Teams or email) to get:
Access permissions for the project on GitHub and Dataland,
The required `AZURE_` API keys, and confirmation that your SSH key has been added to the server configuration. You can also reach out to Andreas if Marc is unavailable.

### Configuring Environment Variables
* Create a copy of the .env.template file called .env in the project's root directory.
* Open the .env file and edit the following fields (this configuration is for testing):
  * DATALAND_URL=https://test.dataland.com
  * DATALAND_API_KEY= {generate from the dataland website}

  * AZURE_OPENAI_API_KEY= {get your OpenAI api key}
  * AZURE_OPENAI_ENDPOINT=https://qalab-openai.openai.azure.com/

  * AZURE_DOCINTEL_API_KEY= {obtain an Azure Document Intelligence API key}
  * AZURE_DOCINTEL_ENDPOINT=https://qalab-docintel.cognitiveservices.azure.com/

  * POSTGRES_USER=postgres
  * POSTGRES_PASSWORD=password

  * PGADMIN_DEFAULT_EMAIL=admin@example.com
  * PGADMIN_DEFAULT_PASSWORD=password


### Open the project
When you open VS Code, a pop-up will appear in the bottom right corner asking whether you want to reopen the project using Devcontainers. Confirm this prompt.

VS Code will then open a new window and begin connecting — please wait while it sets everything up. During this process, two containers will be created:
- a PostgreSQL database container, and
- a Debian container where all dependencies are automatically installed.

### DevContainer-Specific Features
Once the DevContainer is running, you have access to:
- **Pre-installed Extensions:** All VS Code extensions from `.vscode/extensions.json` are automatically installed.
- **GitHub Copilot:** The workspace is pre-configured with Copilot settings from `.copilotignore`.
- **Database Tools:** PGAdmin is available at `http://localhost:5050` (login with credentials from `.env`).

Once the setup is complete, run the following command to start the server:

```bash
pdm run dev
```
VS Code will automatically expose port 8000, where you can access the API documentation at /docs to manually test the project.

## 2. Installing manually


### Required Software
Please ensure the following software is installed on your machine:
* [Git](https://git-scm.com/downloads)
* [Python 3.12](https://www.python.org/downloads/)
* [PDM](https://pdm-project.org/en/latest/#installation) - a Python package manager
* A recent version of Java (on Windows, we recommend [Eclipse Temurin](https://adoptium.net/de/temurin/releases/) 21 for easy installation. On Linux, just use your package manager ;))
* We would recommend everyone to use [VS Code](https://code.visualstudio.com/download) for consistency.
* [PostgreSQL](https://www.postgresql.org/) or [Docker](https://docs.docker.com/).

### First Steps
* Create a [Github](https://github.com) account (if not already available)
* Generate an ssh private-public key pair if you haven't got any yet (run `ssh-keygen -t ed25519` in your terminal)
* Add your ssh public key to your personal GitHub account [here](https://github.com/settings/keys)
* Clone the project repository to your local machine (run `git clone git@github.com:d-fine/DatalandQaLab.git` in your terminal). Especially on windows, take care to select a relatively short base path because of windows max path length restrictions.
* Open the project in VS Code. To work effectively with this codebase, you need to install some extensions. These have been configured as recommended extensions for this repository.
  * When you first open the project, VS Code should prompt you to install the recommended extensions. If prompted, click yes.
  * If this does not work, press `CTRL+P` and enter `Extensions: Show Recommended Extensions`. This should open the extensions menu. At the top, there should be a section called `Workspace Recommendations`. Install all extensions listed here.
* Configure your git username and email (run `git config user.name "Your GitHub Username"` and `git config user.email "email@domain.com"` in the newly created project directory). The email must match one of the addresses you have registered with GitHub.
> [!CAUTION]
> The email address you use here will be publicly visible alongside your commits. Alternatively, you can obtain a pseudonymous email address by going to the [GitHub Email Settings](https://github.com/settings/emails) and activating "Keep my email addresses private".
> You can then use the displayed whatever@users.noreply.github.com address in the git configuration.
* Register an account on [Dataland](https://dataland.com/) and the [Dataland Testing Environment](https://test.dataland.com/)
* Send the following information to a project maintainer (i.e., Andreas and Marc):
  * Your GitHub username and email to become a project collaborator
  * The email address you used to register on Dataland to receive the necessary permissions on the platform
  * Your **public** ssh key so we can provide you with `ssh` access to our servers later

### Configuring Environment Variables
After opening the project in your IDE, you need to configure the required environment variables. Start by copying the `.env.template` file to `.env`.
Any values starting with `AZURE_` will be provided by the project maintainers. 
**After** having received elevated permissions on the Dataland testing environment, you can fill in the `DATALAND_API_KEY` field by going to [Dataland Test Instance API Key Management](https://test.dataland.com/api-key) and creating a new API Key (make sure to select a suitable expiration date).
Enter `https://test.dataland.com` for the `DATLAND_URL`. 

> [!CAUTION]
> All environment variables are confidential and must not be shared with anyone. Do not commit the `.env` file to the repository.
> Once any of the environment variables are compromised (e.g., by accidentally committing the `.env` file, a source code file containing a secret, or a Jupyter notebook where the secret is printed in a cell output), they must be reset **IMMEDIATELY**. Undoing the commit (e.g., by force pushing or by deleting the branch) does not suffice. For resetting the Azure API Keys, contact a project maintainer ASAP.

Finally, you need to configure the database connection by setting `DATABASE_CONNECTION_STRING` to a valid PostgreSQL connection string (e.g., `postgresql+pg8000://postgres:password@localhost:5432/dataland_qa_lab` when there is a local DB named `dataland_qa_lab` accessible with username `postgres` and password `password`)

All other environment variables are used for the Docker-based cloud deployment and are not required for local use.
- `POSTGRES_USER`: The username for the PostgreSQL database created in Docker
- `POSTGRES_PASSWORD`: The password for the PostgreSQL database created in Docker
- `PGADMIN_DEFAULT_EMAIL`: An e-mail address for the pgadmin (needs to have a valid format) docker container
- `PGADMIN_DEFAULT_PASSWORD`: The pgadmin password
- `QALAB_SERVER_VERSION`: Used for pulling the correct Docker images on the servers during deployment
- `SLACK_WEBHOOK_URL`: A Slack webhook to send status messages
- `ENVIRONMENT`: The name of the environment (dev/prod) for inclusion in the Slack messages.

### Quick-Start using Docker
The easiest way to set up a local PostgreSQL database is using Docker Compose. To get up and running quickly, copy these envs into your `.env` file:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=password

DATABASE_CONNECTION_STRING="postgresql+pg8000://postgres:password@localhost:5432/dataland_qa_lab"
```

Then start the database by running `docker compose up -d data_reviewer-db`

### Installing Dependencies
To install the project dependencies, run `./bin/setup_dev_environment.sh` in your terminal in the project directory (Use Git Bash if you are on Windows).

### Verifying everything works
Lets check if the server starts up correctly by running `pdm run start`. If you see the server starting without any error messages, you are good to go. Please look through the whole log, sometimes error messages appear at the beginning but the server appears to have started correctly.

:grin: Congratulations! You are now ready to start contributing to the Dataland QA Lab project. If you have any questions, feel free to ask a project maintainer.
