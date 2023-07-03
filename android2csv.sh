#!/usr/bin/env bash

PROJECT_PATH=$1  # Example: ../wiser3

PROJECT_NAME=$(basename "$PROJECT_PATH")
CSV_PATH="out/$PROJECT_NAME"

mkdir -p "$CSV_PATH"

python3 androidproject2csv.py $PROJECT_PATH/libutilities/src/main/ $CSV_PATH/libutilities.csv
python3 androidproject2csv.py $PROJECT_PATH/libdata/src/main/ $CSV_PATH/libdata.csv
python3 androidproject2csv.py $PROJECT_PATH/libcomm/src/main/ $CSV_PATH/libcomm.csv
python3 androidproject2csv.py $PROJECT_PATH/libstate/src/main/ $CSV_PATH/libstate.csv
python3 androidproject2csv.py $PROJECT_PATH/libui/src/main/ $CSV_PATH/libui.csv

python3 androidproject2csv.py $PROJECT_PATH/laser/src/main/ $CSV_PATH/laser.csv