#!/usr/bin/env bats

# msiem bash test script

# Requires: bats-core https://github.com/bats-core/bats-core
# tests/bats-assert from https://github.com/bats-core/bats-assert.git\
# and tests/bats-support from https://github.com/bats-core/bats-support

HERE=$BATS_TEST_DIRNAME

# Load BATS script libraries
load "$HERE/bats-support/load.bash"
load "$HERE/bats-assert/load.bash"

@test "Test JSON alarm parsing and length with jq" {
    # Query alarms and save resutls as json file
    run python3 -m msiem alarms -t CURRENT_DAY --no_events --json > "${HERE}/alarms.json"

    # Test status ok
    assert_success

    # Test parsable with jq
    echo '$output' | jq '.[] | .summary, (.events[]? | .ruleMessage)' "${HERE}/alarms.json"

    # Store length
    echo '$output' | jq '.[] | length' ${HERE}/alarms.json > "${HERE}/alarms.json.length"
    
    # Query list of alarms with raw method alarmGetTriggeredAlarms
    run python3 -m msiem api -m "v2/alarmGetTriggeredAlarms?triggeredTimeRange=CURRENT_DAY&status=&pageSize=500&pageNumber=1" -d {} > "${HERE}/alarms.fromapi.json"
    
    # Test status ok
    assert_success

    # Store length
    echo '$output' | jq '.[] | length' ${HERE}/alarms.fromapi.json > "${HERE}/alarms.fromapi.json.length"
    
    # Compare length and fail if differs
    assert bash -c "[[ $(cat ${HERE}/alarms.fromapi.json.length) == $(cat ${HERE}/alarms.json.length) ]]"

    # Cleanup tests files
    rm -f "${HERE}/alarms.json" "${HERE}/alarms.json.length" "${HERE}/alarms.fromapi.json" "${HERE}/alarms.fromapi.json.length"
}
