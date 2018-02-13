#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#|Author(s): Nestor Ouranitsas, Dakota Crouchelli                                    |#
#|This file runs automated tests on the GEDCOM_Parser.py file                        |#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import unittest

#all tests dealing with dates
class datesTest(unittest.TestCase):

    # validates all dates are before the current date
    def test_dateBFORcurrent(self):

    # validates the individual is born before marriage
    def test_birtBFORmarr(self):

    # validates the individual is born before their death date
    def test_birtBFORdeat(self):

    # validates that a couple was married before they got divorced
    def test_marrBFORdiv(self):
