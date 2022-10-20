#!/bin/bash

set -e

if [ "${CI_COMMIT_BRANCH}" == "main" ]; then
  git clone git@gitlab.botthouse.net:botthouse/cftcli.git gitlab
  cd gitlab
  git remote add github git@github.com:tmb28054/cftcli.git
  git push -u github main
fi

