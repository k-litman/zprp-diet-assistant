#!/bin/sh

# This is just a convenient wrapper script for the in-project backend/manage.sh. It runs
# commands in docker-compose's app container. It can also contain some project tasks
# that needn't be run inside the main container, like load tests with locust.

set -o errexit
set -o nounset

cmd="$*"

help() {
    cli_name=${0##*/}
    echo "
diet_assistant management CLI
Usage: $cli_name [command]
Commands:
  help
      This message
  build-local
      Build the local environment using docker-compose
  test
      Run tests
  ci-test
      Run tests with additional instrumentation for CI
  lint
      Run linters
  sort
      Sort imports using isort
  format
      Format code using black
  check-migrations
      Check if current Django database migrations are consistent with the code
  validate-spec
      Validate the OpenAPI specification
  lock-dependencies
      Generate a lockfile containing current dependencies
  migrate
      Apply Django database migrations
  shell
      Start a Django interactive shell
  ishell
      Start a nicer Django interactive shell with ipython support
  django <command>
      Shortcut for Django's manage.py script
      For example: \`./manage.sh django makemigrations\` is equivalent to \`./manage.sh run python manage.py
      makemigrations\`
      Important: This command does not use quoting and can cause globbing. To prevent that, make sure your command does not fall under filename expansion pattern.
  run <command>
      Run the provided command inside the local application container
"
}

build_local() {
    docker compose build
}

case "$cmd" in
    build-local)
        build_local
    ;;
    help)
        help
    ;;
    "")
        help
    ;;
    *)
        # shellcheck disable=SC2086
        docker compose run --rm app manage.sh ${cmd}
    ;;
esac
