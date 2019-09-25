#!/bin/bash

# Version: 0.1
# Usage: Control the behavior of the webapi process
#   command line args:
#       -k: Kill the process
#       -u: Update the code from gitlab
#       -r: Run the process
#       -s: Show the pid of process
#   example:  bash behavior.sh -k
#             bash behavior.sh -krs

echo $*

user="wyz"
process="python -u run.py"
process_args="--webapi --webapi_config test --graphapi_config test --esapi_config test --es_search_config test"
logfile="log_webapi.txt"
test_git_branch="dev-feature-aggregate_neighbor"

while getopts "kurs" opt
do
    case $opt in
        k)
        echo "\n********  Kill webapi ********"
        ps -ef| grep ".*$process.*$process_args.*"| grep -v grep| grep ^$user| cut -c 10-15| xargs kill -9
        ps -ef| grep ".*$process.*$process_args.*"| grep -v grep| grep ^$user
        ;;

        u)
        echo "\n********  Update code  ********"
        git checkout $test_git_branch
        git pull
        ;;

        r)
        echo "\n********  Run webapi  ********"
        nohup $process $process_args >$logfile 2>&1 &
        cat $logfile
        ;;

        s)
        echo "\n********  Show pid  ********"
        ps -ef| grep python| grep -v grep| grep $user
        ;;

        ?)
        echo "\n********  error args  ********"
        exit 1
        ;;
    esac
done
