#!/usr/bin/env bash
# Update the Bintray release

build_dir="$(pwd)/build"
current_api_url="https://api.bintray.com/packages/livecli/livecli-nightly/livecli/versions/$(date +'%Y.%m.%d')/release_notes"
curl -u "${BINTRAY_USER}:${BINTRAY_KEY}" -H "Content-Type: application/json" -d @"${build_dir}/bintray-changelog.json" ${current_api_url}
