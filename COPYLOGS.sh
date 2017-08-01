#!/usr/bin/env bash
##################################################################################
echo "SAVING LOGS..."
##################################################################################
echo "WORKING PATH: ${!TEST_ROOT_PATH}"
cd ${!TEST_ROOT_PATH}
##################################################################################
echo "CAPTURING PARAMETERS..."
LOG_REPO="test-logs"
EMAIL="${!GITHUB_EMAIL}"
USERNAME="${!GITHUB_USERNAME}"
PASSWORD="${!GITHUB_PASSWORD}"
REPO_PATH="github.com/${USERNAME}/${LOG_REPO}/.git"
MESSAGE="${!TRAVIS_COMMIT} (Job ${!TRAVIS_JOB_NUMBER})"
##################################################################################
echo "ADDING TO GIT..."
git clone git://${REPO_PATH}
git remote
git config user.email ${EMAIL}
git config user.name ${USERNAME}
git add *
echo "COMMITTING CHANGES..."
git commit -m ${MESSAGE}
git push "https://${PASSWORD}@${REPO_PATH}" master > /dev/null 2>&1
##################################################################################
echo "COMPLETE"
##################################################################################
