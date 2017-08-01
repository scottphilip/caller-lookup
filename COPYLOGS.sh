#!/usr/bin/env bash
##################################################################################
echo "SAVING LOGS..."
##################################################################################
LOG_REPO="test-logs"
HOME_DIR="/home/travis"
GIT_ROOT="/home/travis/github"
BUILD_ARTIFACTS_ROOT="/home/travis/logs"
REPO_PATH="${GITHUB_PASSWORD}@github.com/${GITHUB_USERNAME}/${LOG_REPO}.git"
PROJECT_REPO_NAME="${TRAVIS_REPO_SLUG}"
MESSAGE="${TRAVIS_COMMIT} (Job ${TRAVIS_JOB_NUMBER})"

cd "${HOME_DIR}"
mkdir github

echo "GIT PATH: ${GIT_ROOT}"
cd "${GIT_ROOT}"
git init .
git config user.email "travis@travis-ci.org"
git config user.name "Travis CI"

echo "ADDING TO GIT [https://${REPO_PATH}] ..."
git clone https://${REPO_PATH}

echo "MOVING FILES..."
mkdir -p ${GIT_ROOT}/${LOG_REPO}/${PROJECT_REPO_NAME}
mv ${BUILD_ARTIFACTS_ROOT}/* ${GIT_ROOT}/${LOG_REPO}/${PROJECT_REPO_NAME}/*

echo "ADDING FILES TO GIT..."
git add ${LOG_REPO}/${PROJECT_REPO_NAME}/*

echo "COMMITTING CHANGES..."
git commit -m ${MESSAGE}

echo "UPLOADING FILES..."
git remote add origin https://${REPO_PATH} > /dev/null 2>&1
git push origin master

echo "COMPLETE"
