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
import datetime
from telnetlib import Telnet

from horizon.config import (
    HORIZON_HOST,
    HORIZON_PORT,
    HORIZON_PROMPT,
    HORIZON_QUERY_PROMPT,
    HORIZON_OPTION_PROMPT,
    HORIZON_MISC_PROMPT,
    HORIZON_CARTESIAN_PROMPT,
    DEBUG,
)

HORIZON_OBSERVE = 0
HORIZON_ELEMENTS = 1
HORIZON_VECTORS = 2

HORIZON_MAJOR_ALL = 0
HORIZON_MAJOR_PLANET = 1
HORIZON_MAJOR_MOON = 2
HORIZON_MAJOR_ARTIFICAL = 3


class Interface():
    telnet = Telnet()
    re_version = re.compile("version|v\s?(\d+\.\d+)")
    re_major = re.compile("^\s+(-?\d+)\s\s(\w+)", flags=re.MULTILINE)
    re_minor = re.compile("^\s+(-?\d+)\s+(-?\d+)\s+[\w\-\(\)\/]+\s?\w*\s+([\w\-]+\s?\d*[\w]*)\s+([\d\.]+)$", flags=re.MULTILINE)
    re_meta = re.compile("(\w+)\s+([\d\/\s]+)$", flags=re.MULTILINE)
    re_meta_dictA = re.compile("^\s{2}([A-Z].{0,21})=\s{1,2}(.{015})\s[A-Z]", flags=re.MULTILINE)
    re_meta_dictB = re.compile("\s([A-Z].{0,21})=\s{1,2}(.{0,16})\s?$", flags=re.MULTILINE)
    re_meta_fail = re.compile("No such object record found\: \d+")
    re_cartesian = re.compile("\$\$SOE(.*)\$\$EOE", flags=re.DOTALL)

    def __open(self):
        self.telnet.open(HORIZON_HOST, HORIZON_PORT)
        self.telnet.read_until(HORIZON_PROMPT)
        # self.telnet.read_until(HORIZON_PROMPT)

    def __close(self, send_quit=False):
        if send_quit:
            self.telnet.write("\rquit\n")

        self.telnet.close()

    def __parse_major(self, data, major_type=HORIZON_MAJOR_ALL):
        matches = self.re_major.findall(data)
        # import pdb; pdb.set_trace()
        if len(matches) is 0:
            return []

        if major_type == HORIZON_MAJOR_ALL:
            matches = list((match[1].lower(), match[0]) for match in matches)
        else:
            buff = list()

            for match in matches:
                # import pdb; pdb.set_trace()
                if major_type is HORIZON_MAJOR_ARTIFICAL and int(match[0]) < 0:
                    print "SATILLITE {0}".format(match[0])
                    buff.append((match[1].lower(), match[0]))

                elif major_type is HORIZON_MAJOR_PLANET and int(match[0]) % 10 == 0:
                    print "PLANET {0}".format(match[0])
                    buff.append((match[1].lower(), match[0]))

                elif major_type is HORIZON_MAJOR_MOON and int(match[0]) % 10 == 0 and int(match[0]) > 0:
                    print "MOON {0}".format(match[0])
                    buff.append((match[1].lower(), match[0]))
                else:
                    continue
            matches = buff

        return dict(matches)

    def __parse_minor(self, data):
        matches = self.re_minor.findall(data)

        if len(matches) is 0:
            return []

        # flip the results
        matches = list((m[2].lower(), m[0], m[1], m[3]) for m in matches)

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
        matches = self.re_cartesian.search(data).groups()
        matches = [m.strip().split("\r\n") for m in matches][0]
        result = []

        for i in range(len(matches)):
            vector = dict()
            key = ""
            if (i / 4) % 4 == 0:
                key = "time"
            elif (i / 4) % 4 == 3:
                key = "ltrgrr"
            elif (i / 4) % 4 == 2:
                key = "vxvyvz"
            elif (i / 4) % 4 == 1:
                key = "xyz"
            else:
                break
                raise Exception()
            vector[key] = matches[i]
            result.append(vector)
        return result

    def __parse_version(self, data):
        matches = self.re_version.search(data)

        if matches is None:
            return 0
        # fail if cant find
        return matches.groups()[0]

    def get_major(self, type=HORIZON_MAJOR_ALL):
        """
        =================
        get_major ( self, type ) : returns {}
        =================

        type: horizon.interface.HORIZON_MAJOR_ALL (default)
              horizon.interface.HORIZON_MAJOR_ARTIFICAL
              horizon.interface.HORIZON_MAJOR_MOON
              horizon.interface.HORIZON_MAJOR_PLANET

        Returns a list of major bodies and corresponding IDs
        """
        self.__open()
        self.telnet.write("MB\n")
        # import pdb;pdb.set_trace()

        result = self.telnet.read_until(HORIZON_QUERY_PROMPT)

        if DEBUG:
            print result

        self.__close(send_quit=True)

        return self.__parse_major(result, type)

    def get_minor(self, page=0, page_size=-1):
        """
        =================
        get_minor ( self, page ) : returns {}
        =================

        page: (default: 0) integer to specify page in pagination

        page_size (default: -1): integer to specify how many
            results per page

        Returns a list of minor bodies and corresponding IDs
        """
        self.__open()
        self.telnet.write("RAD > 0\n")

        buff = self.telnet.read_until(HORIZON_MISC_PROMPT)
        print buff

        self.telnet.write("\r\n")
        result = self.telnet.read_until(HORIZON_QUERY_PROMPT)
        print result

        self.__close(send_quit=True)

        if DEBUG:
            print result

        return self.__parse_minor(result)

    def get_cartesian(self, id, start, end, ref="500@10", type=HORIZON_VECTORS, frequency="1h"):

        # make sure start / end are valid or throw error

        self.__open()
        self.telnet.write("{0}\n".format(id))

        buff = self.telnet.read_until(HORIZON_QUERY_PROMPT)
        print buff

        self.telnet.write("E\n")
        buff = self.telnet.read_until(HORIZON_MISC_PROMPT)
        print buff

        # select cartesian data type
        if type is HORIZON_OBSERVE:
            self.telnet.write("o\n")
        elif type is HORIZON_ELEMENTS:
            self.telnet.write("e\n")
        else:
            self.telnet.write("v\n")

        print self.telnet.read_until(HORIZON_MISC_PROMPT)

        # select reference point ID, coord, geo
        self.telnet.write("{0}\n".format(ref))
        print self.telnet.read_until(HORIZON_OPTION_PROMPT)
        self.telnet.write("y\n")

        # select reference plane: body, eclip, frame
        print self.telnet.read_until(HORIZON_MISC_PROMPT)
        self.telnet.write("body\n")

        print self.telnet.read_until(HORIZON_MISC_PROMPT)
        self.telnet.write("{0}\n".format(start))
        print self.telnet.read_until(HORIZON_MISC_PROMPT)
        self.telnet.write("{0}\n".format(end))

        # frequency: 1d, 1h, 1m
        print self.telnet.read_until(HORIZON_MISC_PROMPT)
        self.telnet.write("{0}\n".format(frequency))

        # accept output
        print self.telnet.read_until(HORIZON_MISC_PROMPT)
        self.telnet.write("\r\n")

        result = self.telnet.read_until(HORIZON_CARTESIAN_PROMPT)

        # Cartesian queries have a weird exit
        self.telnet.write("N\n")
        self.__close(send_quit=True)

        if DEBUG:
            print result

        return self.__parse_cartesian(result)

    def query(self, query):
        self.__open()
        self.telnet.write("{0}\n".format(query))

        result = self.telnet.read_until(HORIZON_QUERY_PROMPT)

        self.__close(send_quit=True)

        if "Number of matches" in result:
            return self.__parse_list(result)

        # if query returns single result, use meta parser
        return self.__parse_meta(result)

    def get(self, id):
        self.__open()
        self.telnet.write("{0}\n".format(id))

        result = self.telnet.read_until(HORIZON_QUERY_PROMPT)

        self.__close(send_quit=True)

        if DEBUG:
            print result

        return self.__parse_meta(result)

    def get_version(self):
        self.__open()
        self.telnet.write("quit\n")

        result = self.telnet.read_until(HORIZON_QUERY_PROMPT)

        self.__close()

        if DEBUG:
            print result

        return self.__parse_version(result)
