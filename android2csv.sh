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
CSV_PATH="out/$PROJECT_NAME"

mkdir -p "$CSV_PATH"

python3 androidproject2csv.py $PROJECT_PATH/libutilities/src/main/ $CSV_PATH/libutilities.csv
python3 androidproject2csv.py $PROJECT_PATH/libdata/src/main/ $CSV_PATH/libdata.csv
python3 androidproject2csv.py $PROJECT_PATH/libcomm/src/main/ $CSV_PATH/libcomm.csv
python3 androidproject2csv.py $PROJECT_PATH/libstate/src/main/ $CSV_PATH/libstate.csv
python3 androidproject2csv.py $PROJECT_PATH/libui/src/main/ $CSV_PATH/libui.csv

python3 androidproject2csv.py $PROJECT_PATH/$PROJECT_MODULE/src/main/ $CSV_PATH/laser.csv