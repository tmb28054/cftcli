#!/bin/bash


python3 -m venv venv
source venv/bin/activate

python -m pip install -U pip

pip install -U setuptools

pip install -U build twine wheel

pip install -U cftcli

# build wheel
python -m build --wheel

if [ "${CI_COMMIT_BRANCH}" == "main" ]; then
    secretmanager-env jenkins > myenv
    source myenv
    rm myenv
    for whl in dist/*.whl; do
        twine upload -r pypi dist/$whl
    done
fi
