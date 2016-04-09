#!/bin/bash

set -u

# The MIT License (MIT)
# 
# Copyright (c) 2015 Kirk Leon Guerrero
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Requires inotify-tools
# Example:
# $ file-watch-trigger -e <event> -f <file_to_watch> -tr ./<executable trigger>
# $ file-watch-trigger -e modify -f /tmp/data -t ./cat.sh

usage="
-f      File to watch
-e      Event to monitor
-t      Trigger when event occurs on file
-l      List inotify events
-h      Help
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
    inotifywait -e ${event} $file_to_watch >/dev/null 2>&1 && $trigger
    sleep 1
done
