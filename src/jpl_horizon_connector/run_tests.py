import tests
import unittest

print 'Running Tests...'

suite = unittest.TestLoader().loadTestsFromTestCase(tests.TestHorizonInterface)
unittest.TextTestRunner(verbosity=2).run(suite)
