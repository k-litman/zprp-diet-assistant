#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

celery -A diet_assistant.taskapp beat -l INFO
