# -*- coding: utf-8 -*-=
"""
    test_session
"""

import unittest
from msiem.session import ESMSession
import os

class SessionTests(unittest.TestCase):
    """
    def test_WriteAuth(self):
        return #remove return statement to wirte authentication to file evrytime you run tests...

        s = ESMSession()
        s._config.setAuth()
        s._config.write()
    """

    def test_Login(self):
        s=ESMSession()
        s.login()
        self.assertEquals(s.logged, True)

    