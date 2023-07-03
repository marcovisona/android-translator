#!/usr/bin/env bash

PROJECT_PATH=$1  # Example: ../wiser3

PROJECT_NAME=$(basename "$PROJECT_PATH")
CSV_PATH="out/$PROJECT_NAME"

python3 csv2androidproject.py $CSV_PATH/libutilities.csv $PROJECT_PATH/libutilities/src/main/
python3 csv2androidproject.py $CSV_PATH/libdata.csv $PROJECT_PATH/libdata/src/main/
python3 csv2androidproject.py $CSV_PATH/libcomm.csv $PROJECT_PATH/libcomm/src/main/
python3 csv2androidproject.py $CSV_PATH/libstate.csv $PROJECT_PATH/libstate/src/main/
python3 csv2androidproject.py $CSV_PATH/libui.csv $PROJECT_PATH/libui/src/main/

python3 csv2androidproject.py $CSV_PATH/laser.csv $PROJECT_PATH/laser/src/main/