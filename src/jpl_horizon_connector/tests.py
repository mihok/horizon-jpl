#!/usr/bin/python
# Filename: python-jpl-horizon.py

# import sys
import unittest
import pytest

from telnetlib import Telnet
from config import HORIZON_HOST, HORIZON_PORT, HORIZON_CLI


class TestHorizonInterface(unittest.TestCase):
    # print "Running Tests..."

    def setUp(self):
        self.telnet = Telnet()

    @pytest.mark.timeout(300)
    def test_connection(self):
        self.telnet.open(HORIZON_HOST, HORIZON_PORT, 10)
        self.telnet.read_until(HORIZON_CLI)
        self.telnet.write("quit\n")
        result = self.telnet.read_all()

        self.assertTrue(result)

    def test_search(self):
        pass

    def test_planet_search(self):
        pass
