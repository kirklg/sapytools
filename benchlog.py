"""
The MIT License (MIT)

Copyright (c) 2015 Kirk Leon Guerrero

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import time
import select
import argparse
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

    try:
        with open(args.logfile, 'r'):
            pass
    except PermissionError:
        raise
    except FileNotFoundError:
        raise

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
