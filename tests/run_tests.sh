#!/usr/bin/env bash
# Copyright (c) 2017 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.


# If the SHOTGUN_EXTERNAL_REPOS_ROOT is not set, we're going to assume every repo
# needed is a sibling of the publish 2 repo.
if [ -z ${SHOTGUN_EXTERNAL_REPOS_ROOT+x} ]; then
    export SHOTGUN_EXTERNAL_REPOS_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../.."
fi

${SHOTGUN_EXTERNAL_REPOS_ROOT}/tk-core/tests/run_tests.sh --test-root "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" $*