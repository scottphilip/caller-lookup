#!/usr/bin/env bash
##################################################################################
echo "SAVING LOGS..."
##################################################################################
WORKING_DIR="/home/travis/temp/"
LOG_REPO="test-logs"
REPO_PATH="github.com/${GITHUB_USERNAME}/${LOG_REPO}/.git"
MESSAGE="${TRAVIS_COMMIT} (Job ${TRAVIS_JOB_NUMBER})"

echo "WORKING PATH: ${WORKING_DIR}"
cd "${WORKING_DIR}"

echo "ADDING TO GIT (${REPO_PATH}) ..."
git clone git://${REPO_PATH}
git remote
git config user.email ${GITHUB_EMAIL}
git config user.name ${GITHUB_USERNAME}
git add *

echo "COMMITTING CHANGES..."
git commit -m ${MESSAGE}
git push "https://${GITHUB_PASSWORD}@${REPO_PATH}" master > /dev/null 2>&1

echo "COMPLETE"
