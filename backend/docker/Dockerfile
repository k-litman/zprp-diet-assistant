# User ID for the django user we're creating. The builder can set this to the
# host user's ID to avoid file permissions problems.
ARG USER_ID=1000

# Whether we're running in local development mode
ARG DEV_MODE=0


#------------------------------------------------------------------------------
# The base stage for the final image. This is where we set system configuration
# and install system dependencies.
FROM python:3.11-slim as base

# Explicitly set the application user's home folder
ENV HOME=/home/django
ENV \
# Set locale
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
# Disable buffering on writing to stdout/stderr. This is to avoid loss of logs in
# the event of an application crash.
    PYTHONUNBUFFERED=1 \
# Store bytecode cache in a temporary filesystem. This not only reduces the image
# size but also lets us write cache for the standard library modules which normally
# reside in folders only writable by root. This speeds up subsequent interpreter
# invocations, which does matter in some cases - for example when we have a health
# check that uses a python command line utility.
    PYTHONPYCACHEPREFIX=/dev/shm/python \
# Pipenv version, PIPENV_VERSION is taken
    PIPENV_RELEASE=2023.7.23 \
# Disable Pipenv's spinner to stop it from filling logs with garbage
    PIPENV_NOSPIN=1 \
# Increase the pipenv timeout, it can take a while to lock dependencies
    PIPENV_TIMEOUT=900 \
# And a location for the application virtualenv based on the above
    VIRTUAL_ENV=$HOME/venv \
# Add virtualenv bin folder to the PATH
    PATH="$HOME/venv/bin:/app:$PATH" \
# Add the project folder to PYTHONPATH so the main package is always importable
    PYTHONPATH="/app:$PYTHONPATH" \
# Save the lock file here if this is the first build
    BUILD_PIPFILE_LOCK=$HOME/Pipfile.lock.build

# Install ops tools
RUN apt-get -qq update \
    && apt-get -qq -y install \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq -y clean


#------------------------------------------------------------------------------
# The build stage. The virtual environment for our application is built here. This
# includes installing build dependencies for C extensions that aren't necessary in the
# final image.
FROM base as builder-base

# Install build dependencies
RUN apt-get -qq update \
    && apt-get -qq -y install \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq -y clean

# Install pipenv globally
RUN HOME=/tmp pip install --no-cache-dir pipenv==$PIPENV_RELEASE


FROM builder-base as builder
ARG DEV_MODE

# Pull in Pipfile and Pipfile lock. This is done separately for layer caching reasons.
# We copy Pipfile.lock using a wildcard because it might not exist.
COPY ./diet_assistant/Pipfile ./diet_assistant/*.lock $HOME/
WORKDIR $HOME

# Prepare virtualenv and install Python dependencies
RUN python3 -m venv $VIRTUAL_ENV \
    && if [ $DEV_MODE -eq 1 ]; then \
        # dev mode, install dev dependencies
        # We'd like this to fail if the Pipfile.lock is out of date, but also to
        # generate the lockfile if it doesn't exist, which it won't on the first build.
        pipenv install --dev --deploy; \
        # Copy Pipfile.lock to a temporary location, from which we can retrieve it
        # if this is the first build and we don't want to regenerate it pointlessly
        cp -f Pipfile.lock $BUILD_PIPFILE_LOCK; \
    else \
        # normal (production) mode, install non-dev dependencies while verifying that
        # Pipfile.lock is up to date. Manually check if Pipfile.lock exists because
        #  --deploy will still generate a new one if it's not there.
        [ -f Pipfile.lock ] || { echo 'No Pipfile.lock found' ; exit 1; }; \
        pipenv install --deploy; \
    fi \
    && rm -rf $HOME/.cache/*


#------------------------------------------------------------------------------
# The final stage. We only install dependencies necessary for runtime operation, like
# dynamically linked shared libraries. We copy the Python virtual environment from the
# builder stage and the application code from context.
FROM base AS final

# Need to redeclare build args due to Dockerfile semantics
ARG USER_ID
ARG DEV_MODE

# Install runtime dependencies
RUN apt-get -qq update \
    && apt-get -qq -y install \
    # Translations dependencies
    gettext \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq -y clean

# Install pipenv if we're in dev mode
RUN if [ $DEV_MODE -eq 1 ]; then HOME=/tmp pip install --no-cache-dir pipenv==$PIPENV_RELEASE; fi

# Create the user and group to run the Django application as
RUN addgroup --system --gid $USER_ID django \
    && adduser --system --home $HOME --uid $USER_ID --ingroup django django

# Copy the start scripts, make them executable, and set ownership
COPY --chown=django:django ./docker/scripts/celery/ ./docker/scripts/web/ /
RUN chmod +x /*.sh

# Create the application folder with the right dependencies
RUN mkdir -p /app && chown django /app

# Create a folder to store media in if we're in dev mode
RUN if [ $DEV_MODE -eq 1 ]; then \
        mkdir -p /media && chown django /media; \
    fi

USER django

# Copy the built virtualenv from the builder stage
COPY --from=builder --chown=django:django $VIRTUAL_ENV $VIRTUAL_ENV
#COPY --from=builder --chown=django:django $BUILD_PIPFILE_LOCK $BUILD_PIPFILE_LOCK

# Copy the application data in
COPY --chown=django:django ./diet_assistant /app/

WORKDIR /app

# Make the runner script executable
RUN chmod +x /app/manage.sh

CMD ["/start-gunicorn.sh"]
