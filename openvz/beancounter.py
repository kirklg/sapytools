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


Needs root :(
Set and Get functions to provide better error handling/reporting to
applications executing in an OpenVZ environment.

"""

from collections import namedtuple


class BeancounterNotFound(Exception):
    """ raise when counter is invalid """
    pass


class BeanCounter(object):
    """ openvz.BeanCounter interface """
    def __init__(self):
        self.beancounter = '/proc/user_beancounters'
        self.ubc = dict()
        self.limits = ('held', 'maxheld', 'barrier', 'limit', 'failcnt')
        self.counters = (
            'kmemsize', 'lockedpages', 'privvmpages', 'shmpages', 'numproc',
            'physpages', 'vmguarpages', 'oomguarpages', 'numtcpsock', 'numflock',
            'numpty', 'numsiginfo', 'tcpsndbuf', 'tcprcvbuf', 'othersockbuf',
            'dgramrcvbuf', 'numothersock', 'dcachesize', 'numfile', 'numiptent',)
        self.counter_base = {fld: namedtuple(fld, list(self.limits)) for fld in self.counters}

        with open(self.beancounter, 'r') as bc_fd:
            for line in bc_fd:
                line = line.split()
                if line[0] not in ('Version:', 'uid'):
                    # veid identifier
                    if ':' in line[0]:
                        veid = int(line[0].replace(':', ''))
                        counter = line[1]
                        self.ubc.setdefault(veid, dict())
                        if counter in self.counters:
                            self.ubc[veid][counter] = self.counter_base[counter]._make(line[2:])
                    else:
                        counter = line[0]
                        if counter in self.counters:
                            self.ubc[veid][counter] = self.counter_base[counter]._make(line[1:])

    def set(self, veid, counter, min_limit, max_limit):
        """ Run vzctl set command and save beancounter for veid """
        try:
            from sh import vzctl, ErrorReturnCode
        except ImportError:
            raise
        if counter not in self.counters:
            raise BeancounterNotFound(counter)
        else:
            try:
                vzctl.set('{veid} --{counter}={min_limit}:{max_limit} --save'.format(**locals()))
            except ErrorReturnCode:
                raise

    def get(self, counter=None, veid=None, _all=False):
        """ Return beancounters """
        if veid and not counter:
            return self.ubc[veid]
        elif veid and counter:
            try:
                return self.ubc[veid][counter]
            except KeyError:
                BeancounterNotFound(counter)

        if _all:
            return self.ubc
