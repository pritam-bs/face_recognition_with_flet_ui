#!/bin/bash
PROJECT_PATH="${HOME}/projects/face_recognition_with_flet_ui"
VENV=".face_venv"

echo "Project Path: ${PROJECT_PATH}"
echo "Virtual Environment: ${VENV}"

cd ${PROJECT_PATH}
echo "Current Path: ${pwd}"

source ${VENV}/bin/activate

# Check if the virtual environment is activated

if [ -n "$VIRTUAL_ENV" ]; then
    echo "Virtual environment is activated. Path: $VIRTUAL_ENV"
else
    echo "Virtual environment is not activated."
    exit 1
fi

echo "Going to run flet app"
flet run src/main.py
echo "Flet app started"