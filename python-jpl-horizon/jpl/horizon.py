# python-jpl-horizon
#
# Written by: Matthew Mihok (@mattmattmatt)
#
# The MIT License (MIT)
# Copyright (c) 2013 
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the 
# "Software"), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, 
# distribute, sublicense, and/or sell copies of the Software, and to permit 
# persons to whom the Software is furnished to do so, subject to the 
# following conditions:
#
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import re
from telnetlib import Telnet

from config import (
    HORIZON_HOST,
    HORIZON_PORT,
    HORIZON_PROMPT,
    HORIZON_QUERY_PROMPT,
    DEBUG,
)


class Horizon():
    telnet = Telnet()
    re_version = re.compile("version|v\s?(\d+\.\d+)")
    re_list = re.compile("^\s+-?(\d+)\s\s(\w+)", flags=re.MULTILINE)
    re_meta = re.compile("(\w+)\s+([\d\/\s]+)$", flags=re.MULTILINE)
    re_meta_dictA = re.compile("^\s{2}([A-Z].{0,21})=\s{1,2}(.{015})\s[A-Z]", flags=re.MULTILINE)
    re_meta_dictB = re.compile("\s([A-Z].{0,21})=\s{1,2}(.{0,16})\s?$", flags=re.MULTILINE)
    re_meta_fail = re.compile("No such object record found\: \d+")
    re_cartesian = re.compile(".+")

    def __open(self):
        self.telnet.open(HORIZON_HOST, HORIZON_PORT)
        self.telnet.read_until(HORIZON_PROMPT)
        # self.telnet.read_until(HORIZON_PROMPT)

    def __close(self, send_quit=False):
        if send_quit:
            self.telnet.write("\rquit\n")

        self.telnet.close()

    def __parse_list(self, data):
        matches = self.re_list.findall(data)
        # import pdb; pdb.set_trace()
        if len(matches) is 0:
            return []

        # flip the results
        matches = list((m[1].lower(), m[0]) for m in matches)

        return dict(matches)

    def __parse_meta(self, data):

        if self.re_meta_fail.match(data):
            return {'error': 'No such object record found'}

        matches = []
        matches += self.re_meta_dictA.findall(data)
        matches += self.re_meta_dictB.findall(data)
        meta = self.re_meta.search(data).groups()
        matches = list(tuple(v.strip() for v in m) for m in matches)

        # import pdb; pdb.set_trace()

        name = meta[0]
        id = meta[1].strip().split(' / ')[0]

        # include name and id along with detailed data
        matches += [('ID', id)]
        matches += [('Name', name)]

        return dict(matches)

    def __parse_cartesian(self, data):
        pass

    def __parse_version(self, data):
        matches = self.re_version.search(data)

        if matches is None:
            return 0
        # fail if cant find
        return matches.groups()[0]

    def major(self):
        self.__open()
        self.telnet.write("MB\n")
        # import pdb;pdb.set_trace()

        result = self.telnet.read_until(HORIZON_QUERY_PROMPT)

        if DEBUG:
            print result

        self.__close(send_quit=True)

        return self.__parse_list(result)

    def minor(self):
        self.__open()
        self.telnet.write("SB\n")

        result = self.telnet.read_until(HORIZON_QUERY_PROMPT)

        if DEBUG:
            print result

        self.__close(send_quit=True)

        return self.__parse_list(result)

    def get(self, id):
        self.__open()

        self.telnet.write("{0}\n".format(id))

        result = self.telnet.read_until(HORIZON_QUERY_PROMPT)

        if DEBUG:
            print result

        self.__close(send_quit=True)

        return self.__parse_meta(result)

    def version(self):
        self.__open()

        self.telnet.write("quit\n")
        result = self.telnet.read_until(HORIZON_QUERY_PROMPT)

        if DEBUG:
            print result

        self.__close()

        return self.__parse_version(result)
