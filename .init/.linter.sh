#!/bin/bash
cd /home/kavia/workspace/code-generation/python-playground-127292-127301/python_playground_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

