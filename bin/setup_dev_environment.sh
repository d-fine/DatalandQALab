#!/usr/bin/env bash
. bin/utils.sh

assert_called_from_project_root

set -euxo pipefail
mkdir -p "./clients"

# Generate clients
./bin/generate_dataland_api_clients.sh

# Setup PDM
pdm install
