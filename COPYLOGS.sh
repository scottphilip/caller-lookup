#!/usr/bin/env bash
##################################################################################
echo "SAVING LOGS..."
##################################################################################
LOG_REPO="test-logs"
GIT_ROOT="/home/travis/github/"
BUILD_ARTIFACTS_ROOT="/home/travis/logs/"
REPO_PATH="github.com/${GITHUB_USERNAME}/${LOG_REPO}.git"
MESSAGE="${TRAVIS_COMMIT} (Job ${TRAVIS_JOB_NUMBER})"

echo "GIT PATH: ${GIT_ROOT}"
cd "${GIT_ROOT}"

echo "ADDING TO GIT (https://${REPO_PATH}) ..."
git init .
git clone https://${REPO_PATH}
git remote add origin https://${REPO_PATH}

mv ${BUILD_ARTIFACTS_ROOT}/* ${GIT_ROOT}/${LOG_REPO}/*
git add *

echo "COMMITTING CHANGES..."
git commit -m ${MESSAGE}
git push https://${GITHUB_PASSWORD}@${REPO_PATH} master > /dev/null 2>&1

echo "COMPLETE"
