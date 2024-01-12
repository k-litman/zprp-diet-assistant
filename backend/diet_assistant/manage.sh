#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


cmd="$1"
shift 1
args="$*"


PYTEST="pytest"

# default test flags
RUNTEST="$PYTEST \
    --durations=10 \
    --cov"

# CI specific test flags
RUNCITEST="$PYTEST \
    --durations=10"

migrate() {
    python manage.py migrate --noinput
}

validate_spec() {
    python -m openapi_spec_validator schema/schema.yml
}

check_migrations() {
    python manage.py makemigrations --check --dry-run
}

lint() {
    black --check . || echo "Try running ./manage.sh format"
    isort --check-only --atomic . || echo "Try running ./manage.sh sort"
    flake8
}

typecheck() {
    mypy
}

shell() {
    python manage.py shell
}

ishell() {
    python manage.py shell_plus --ipython
}

populate() {
    python populate_data.py
}


case "$cmd" in
    check-migrations)
        check_migrations
    ;;
    lint)
        lint
    ;;
    typecheck)
        typecheck
    ;;
    validate-spec)
        validate_spec
    ;;
    sort)
        isort --atomic .
    ;;
    format)
        black .
    ;;
    run-git-hooks)
      lint
      validate_spec
      check_migrations
    ;;
    test)
        ${RUNTEST}
    ;;
    ci-test)
        ${RUNCITEST}
    ;;
    lock-dependencies)
        # If we don't have a Pipfile.lock in the app directory, that means this is the
        # first build and we should use the one generated during the build
        if [ ! -f Pipfile.lock ]; then
            cp "${BUILD_PIPFILE_LOCK}" Pipfile.lock
        else
          pipenv lock
        fi
    ;;
    migrate)
        migrate
    ;;
    shell)
        shell
    ;;
    ishell)
        ishell
    ;;
    run)
        $args  # run the command passed in as the argument
    ;;
    django)
        # shellcheck disable=SC2086
        python manage.py $args
    ;;
    populate)
        populate
    ;;
    *)
        echo "Unknown command: $cmd $args"
        exit 1
    ;;
esac
