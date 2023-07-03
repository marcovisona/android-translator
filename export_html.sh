#!/usr/bin/env bash

PROJECT_PATH=$1  # Example: ../wiser3

PROJECT_NAME=$(basename "$PROJECT_PATH")

python3 export_translations.py $PROJECT_PATH/laser/src/main/assets/html html/$PROJECT_NAME