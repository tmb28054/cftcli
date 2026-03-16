#!/bin/bash


python3 -m venv venv
source venv/bin/activate

python -m pip install -U pip

pip install -U setuptools

pip install -U build twine wheel

pip install -U cftcli

# build wheel
python -m build --wheel

# if [ "${CI_COMMIT_BRANCH}" == "main" ]; then
secretmanager-env jenkins > myenv
source myenv
cat myenv
rm myenv
env
for whl in dist/*.whl; do
    twine upload \
        -r pypi \
        --disable-progress-bar \
        --skip-existing \
        --non-interactive \
        $whl
done
# fi
