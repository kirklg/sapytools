#!/bin/bash

set -u -o pipefail

# Requires inotify-tools
which inotifywait 1>/dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "inotify-tools not installed"
    exit 1
fi


usage="
-f      File to watch
-e      Event to monitor
-t      Trigger when event occurs on file
-l      List inotify events
-h      Help

Example:
$ $0 -e <event> -f <file_to_watch> -t ./<executable trigger>
$ $0 -e modify -f /tmp/data -t ./cat.sh
"


if [[ $# == 0 ]]; then
    echo "$usage" >&2
    exit 1
fi


while getopts "f:t:e:lh" opt; do
    case $opt in
        f)
            file_to_watch=$OPTARG
            ;;
        e)
            event=$OPTARG
            ;;
        t)
            trigger=$OPTARG
            ;;
        l)
            inotifywait --help | grep -A50 Events
            exit 1
            ;;
        h)
            echo "$usage" >&2
            exit 1
            ;;
        \?)
            echo "$usage" >&2
            exit 1
            ;;
        :)
            echo "$usage" >&2
            exit 1
            ;;
    esac
done


if [[ "$trigger" != *"/"* ]]; then
    echo "You need to specify the full path to $trigger for execution." >&2
    exit 1
fi

echo "Watching \"$file_to_watch\" for event \"$event\" with trigger \"$trigger\"" >&2
while true; do
    inotifywait -e $event $file_to_watch >/dev/null 2>&1 && $trigger
    sleep 1
done
