#!/usr/bin/env bash
. bin/utils.sh

assert_called_from_project_root

set -euxo pipefail
mkdir -p "./clients"

function openapi_generator() {
  if [ ! -f "./clients/openapi-generator-cli.jar" ]; then
    echo "OpenAPI Generator not found. Downloading..."
    curl https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.7.0/openapi-generator-cli-7.7.0.jar -o ./clients/openapi-generator-cli.jar
  fi
  java -jar ./clients/openapi-generator-cli.jar "$@"
}

# Dataland Backend
rm -rf ./clients/backend
openapi_generator generate \
    -i https://dataland.com/api/v3/api-docs/public \
    -g python \
    --additional-properties=packageName=dataland_backend \
    -o './clients/backend'

# Dataland Document Manager
rm -rf ./clients/documents
openapi_generator generate \
    -i https://dataland.com/documents/v3/api-docs/public \
    -g python \
    --additional-properties=packageName=dataland_documents \
    -o './clients/documents'

# Dataland QA Service
rm -rf ./clients/qa
openapi_generator generate \
    -i https://dataland.com/qa/v3/api-docs/public \
    -g python \
    --additional-properties=packageName=dataland_qa \
    -o './clients/qa'
