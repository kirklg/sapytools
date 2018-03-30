"""
Log event counter, every line (event) appended to a log file will increment the
global counter, and display the current count per sleep count.

Where this is useful:
* For very active log files where `tail -F` is futile.
* When you have a service-specific event log and you don't care
about what the data looks like but want to know how active the log is.

Example:

# Count events every second
python ./benchlog.py -f /var/log/syslog -s 1
"""


from __future__ import absolute_import, division, print_function

import argparse
import select
import time
from multiprocessing import Process, Value


def log_counter(log, count):
    poll = select.poll()
    with open(log, 'r') as fd:
        poll.register(fd, select.POLLIN)
        # end-of-file
        fd.seek(0, 2)
        while True:
            if poll.poll(1):
                for _ in fd:
                    count.value += 1


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', dest='logfile', required=True)
    arg_parser.add_argument('-t', dest='sleep', type=int, default=1)

    args = arg_parser.parse_args()

    # Test if file exists and is readable
    # It is easier to do this here instead from within the child process, so the
    # tradeoff is we open the file twice, but with the benefit that we fail early!
    f = open(args.logfile, 'r')
    f.close()

    count = Value('i', 0)
    p = Process(target=log_counter, args=(args.logfile, count,))
    p.start()

    while True:
        time.sleep(args.sleep)
        print('{0} events/{1}s'.format(count.value, args.sleep))
        count.value = 0

    p.join()


if __name__ == '__main__':
    main()
