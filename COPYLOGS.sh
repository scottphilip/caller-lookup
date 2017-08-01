#!/usr/bin/env bash
##################################################################################
echo "SAVING LOGS..."
##################################################################################
LOG_REPO="test-logs"
PROJECT_REPO_NAME="caller-lookup"
HOME_DIR="/home/travis"
GIT_ROOT="/home/travis/github"
BUILD_ARTIFACTS_ROOT="/home/travis/logs"
REPO_PATH="${GITHUB_PASSWORD}@github.com/${GITHUB_USERNAME}/${LOG_REPO}.git"
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
mkdir -p ${LOG_REPO}/${PROJECT_REPO_NAME}/${TRAVIS_JOB_NUMBER}
cd "${BUILD_ARTIFACTS_ROOT}/${TRAVIS_JOB_NUMBER}"
mv -v * ${LOG_REPO}/${PROJECT_REPO_NAME}/${TRAVIS_JOB_NUMBER}/

echo "ADDING FILES TO GIT..."
cd "${LOG_REPO}/${PROJECT_REPO_NAME}"
git add ${TRAVIS_JOB_NUMBER}

echo "COMMITTING CHANGES..."
git commit -m ${MESSAGE}

echo "UPLOADING FILES..."
git remote add origin https://${REPO_PATH} > /dev/null 2>&1
git push origin master

echo "COMPLETE"
