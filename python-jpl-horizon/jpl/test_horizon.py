#!/usr/bin/python
# Filename: python-jpl-horizon.py

# import sys
import unittest
import pytest

from horizon import Horizon


class TestHorizonInterface(unittest.TestCase):
    # print "Running Tests..."

    def setUp(self):
        self.horizon = Horizon()

    @pytest.mark.timeout(10)
    def test_connection(self):
        version = self.horizon.version()

        self.assertTrue(version)

    @pytest.mark.timeout(10)
    def test_minor_bodies(self):
        data = self.horizon.minor()

        self.assertTrue(len(data))

    @pytest.mark.timeout(10)
    def test_major_bodies(self):
        data = self.horizon.major()

        self.assertTrue(len(data))

    @pytest.mark.timeout(10)
    def test_get(self):
        data = self.horizon.get(100)

        self.assertTrue(data)
