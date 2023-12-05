diet-assistant
==============

A short description of the project.

![Built with Cookiecutter Django https://github.com/pydanny/cookiecutter-django/](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)


Local Setup
-------------
### Requirements

This project uses [docker](https://docs.docker.com/engine/install/) and 
[docker-compose](https://docs.docker.com/compose/install/) for running the local development environment.
Please refer to the official installation instructions for both.

### Settings

The local environment is configured using an `.env` file located in the project root
folder. All the services specified in [docker-compose.yml]() read environment variable
values from that file. The file may require local modification, so it's ignored by 
git, and a template file - `.env.template` is provided. When setting up a local 
environment, run
```bash
cp .env.template .env
```
to create your local `.env` file.

The `.env.template` file is treated as the project's default configuration in 
non-production environments, which includes running tests via CI. As such, it should
be kept up-to-date when making changes to the application.

#### A note for Linux users

On Linux, Docker runs as a system daemon with root privileges, and can actively create
files inaccessible to the host user. If you'd like to avoid that, you'll need to add 
your UID to the `.env` file - the containers started by docker-compose will create files 
owned by this UID. Run 
```bash
echo "UID=${UID}" >> .env
```
to do so.

##### IMPORTANT: Don't run compose as root

Your Linux user won't have permission to use docker by default. This can be fixed by
adding them to the `docker` group, as explained in the [official docs](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user).

Running docker and compose commands with `sudo` will break the setup in this template
and re-introduce file permission problems we've worked hard to avoid. Please don't.

### Building and starting the local environment

Build the docker images with:
```bash
docker compose build
```

Then you can start the local environment with:
```bash
docker compose up
```

See also [Applying migrations](#applying-migrations) and [Setting up users](#setting-up-users).

### Configuring git `pre-commit` hooks

If you want to use `pre-commit` hooks, run the following command in your project root:
```bash
bin/install-git-hooks.sh
```

From now on, whenever you `git commit`, the `pre-commit` hooks will be 
executed first, validating or reformatting your code (depending on which hooks you
 are using). You won't be able to commit your changes until all hooks succeed.

Hook scripts are located in the `git-hooks` directory in the root of the project. 
You can easily add your own hooks by adding new `.sh` files to this folder.

**Note**: to skip git hooks, use the `--no-verify` or `-n` option. For example :
`git commit -n -m "your commit message"`.

### PyCharm support

We provide a default PyCharm configuration that includes interpreter settings, test 
templates, and some assorted settings. In order to use it, run

```bash
cp -R .idea.template .idea
```

Basic Commands
--------------

Project-related tasks in general are carried out using the [manage.sh](manage.sh) script
at the top level of the project. There's also an analogous script in the [backend folder](backend/manage.sh),
that the top-level script calls via `docker-compose`. Run
```bash
./manage.sh help
```
to see the available commands.

Add new commands to these scripts as they become available. Any action the project
requires with some regularity, and which isn't part of another standard interface
(like Django's `manage.py`) should be available as a command.

### Dependency management

This project uses [Pipenv](https://pipenv.kennethreitz.org) for dependency management.
Pipenv generates a lockfile containing pinned dependencies, and dependencies are
installed based on said lockfile, which should be added to source control and updated
manually when needed.

Pipenv's dependency specification lives in a [Pipfile](diet_assistant/Pipfile). Please note
that Pipenv stores both base and dev dependencies in the same file, and take care
to add your custom dependencies to the right section.

#### Managing the lockfile

After you first build the project, you need to run
```bash
./manage.sh lock-dependencies
```
and add the `diet_assistant/Pipfile.lock` file it creates to git.

This procedure should be repeated every time you modify the Pipfile, or when you'd like
to update the pinned versions of your dependencies while keeping them within the spec.


### Manual testing/linting

Before committing your changes, perform next steps (in same order):

1. test your code:
    ```bash
    ./manage.sh test
    ```

2. lint your code:
    ```bash
    ./manage.sh lint
    ```

3. sort python imports
    ```bash
    ./manage.sh sort
    ```

4. format your code:
    ```bash
    ./manage.sh format
    ```

#### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report::

```bash
./manage.sh run pytest --cov-report html --cov . --verbose
open diet_assistant/htmlcov/index.html
```

#### Running tests with py.test

```bash
./manage.sh run pytest .
```

### Applying migrations

To apply database migrations, run:
```bash
./manage.sh migrate
```

You only need to do this whenever new migrations have been added relative to the state
of your local database. If you start the environment without doing this, the Django dev
webserver is going to complain loudly in the logs.

### Setting up users

To create an **superuser account**, use this command:
```bash
./manage.sh django createsuperuser
```
which is an alias for
```bash
```bash
./manage.sh run python manage.py createsuperuser
```

For normal user accounts, follow the application's registration flow.

Redis
-----

This app is configured by default with `redis` cache backend.

### Password secured Redis

If your Redis broker is secured with password, it should be provided as HTTP basic auth
URL params like `redis://:Pa$$word@redis:6379`.

If your password includes [URL reserved characters](https://en.wikipedia.org/wiki/URL_encoding#Percent-encoding_reserved_characters)
you must first encode it, for example with help of Python's `urllib.parse.quote`: 

```python
urllib.parse.quote(password, safe="")
```

Celery
------

This app comes with Celery. By default, it is configured to use the `redis` broker.

### Testing Celery
By default all tasks are run synchronously in tests. If you need to test with async you
must change `CELERY_ALWAYS_EAGER` to `False` in [the test settings file](diet_assistant/settings/test.py)
then all tasks will use `redis` and docker configurations.
 
```
CELERY_ALWAYS_EAGER = False
```

More details in the [Celery documentation](https://docs.celeryq.dev/en/latest/userguide/configuration.html#task-always-eager).

### SSL/TLS in Redis broker

To use secured Redis broker just use `rediss://` scheme in your Celery broker URL.

The [base settings file](diet_assistant/settings/base.py) is configured 
to set appropriate Celery configs (`BROKER_USE_SSL` and `CELERY_REDIS_BACKEND_USE_SSL`)
based on that. 

Note that default settings do not validate the certificate. See how to set the
`BROKER_USE_SSL` to include cert files in [the official documentation](https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-use-ssl).

Sentry
------

Sentry is an error logging aggregator service. You can send email to DevOps 
team and ask about your account and project diet_assistant.

You must set the DSN url in production.

OpenAPI
-------

[OpenAPI](https://swagger.io/specification/) is a format for specifying REST API schemas
in a language-agnostic manner. This project contains an OpenAPI schema located at
[diet_assistant/schema/](diet_assistant/schema). The docker-compose definition also includes a
mock server which serves examples from the schema. This can be particularly useful to
frontend developers, who are able to check out the project and bring the mock server
up by running
```bash
docker compose up mockserver
```
without needing to build or configure anything else in the project.

Documentation
------------------
You can find more detailed documentation [here](docs/README.md). Make an effort to
keep it up-to-date.



