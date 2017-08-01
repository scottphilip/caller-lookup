#!/usr/bin/env bash
echo "SAVING LOGS..."
LOG_REPO="test-logs"
BUILD_DIR="${!TRAVIS_BUILD_DIR}"
JOB_NUMBER="${!TRAVIS_JOB_NUMBER}"
CURRENT_REPO="${!TRAVIS_REPO_SLUG##*/}"
EMAIL="${!GITHUB_EMAIL}"
USERNAME="${!GITHUB_USERNAME}"
PASSWORD="${!GITHUB_PASSWORD}"
REPO_PATH="github.com/${USERNAME}/${LOG_REPO}/.git"
MESSAGE="${!TRAVIS_COMMIT} (Job ${!TRAVIS_JOB_NUMBER})"
cd ${BUILD_DIR}
mkdir github
cd github
mkdir "${CURRENT_REPO}"
cp -r ${BUILD_DIR}/${JOB_NUMBER} ${BUILD_DIR}/github/${CURRENT_REPO}/${JOB_NUMBER}
git clone git://${REPO_PATH}
git remote
git config user.email ${EMAIL}
git config user.name ${USERNAME}
echo "ADDING ${BUILD_DIR}/github/${CURRENT_REPO}/${JOB_NUMBER} TO GIT"
git add ${BUILD_DIR}/github/${CURRENT_REPO}/${JOB_NUMBER}
git commit -m ${MESSAGE}
git push "https://${PASSWORD}@${REPO_PATH}" master > /dev/null 2>&1
echo "COMPLETE"
