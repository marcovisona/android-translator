#!/usr/bin/env bash

PROJECT_MODULE="laser"

usage() {
  echo "Usage: $0 [-h] [-m module_path] [project_path]" >&2
  exit 1
}

# Parse command-line options
while getopts ":m:h" opt; do
  case $opt in
    m)
      PROJECT_MODULE="$OPTARG"
      ;;
    h)
      usage
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      usage
      ;;
  esac
done

shift $((OPTIND-1))

PROJECT_PATH="$1"  # Example: ../wiser3

# Check if no options or positional arguments are provided
if [[ -z $PROJECT_PATH ]]; then
  usage
fi

PROJECT_NAME=$(basename "$PROJECT_PATH")

python3 export_translations.py $PROJECT_PATH/$PROJECT_MODULE/src/main/assets/html html/$PROJECT_NAME --keep-html-tags