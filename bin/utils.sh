function assert_called_from_project_root() {
  if ! [ -d .git ]; then
    echo "Please ensure that you call this script from the root of the python project (i.e., using ./bin/generate_dataland_api_clients.sh)"
    exit 1
  fi
}
