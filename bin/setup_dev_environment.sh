#!/usr/bin/env bash
. bin/utils.sh

assert_called_from_project_root

set -euxo pipefail
mkdir -p "./clients"

./bin/generate_dataland_api_clients.sh

pdm install

pdm run python -m dataland_qa_lab.bin.verify_config
