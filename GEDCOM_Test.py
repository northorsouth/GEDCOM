#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#|Author(s): Nestor Ouranitsas, Dakota Crouchelli                                    |#
#|This file runs automated tests on the GEDCOM_Parser.py file                        |#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import unittest

import GEDCOM_Database as db
import GEDCOM_Parser as parser
from prettytable import PrettyTable

#all tests dealing with dates
class datesTest(unittest.TestCase):

    def setUp(self):
        print("\n\ntesting: " + self._testMethodName)
        self.database = db.dbInit("GEDCOM.db")
    
    def tearDown(self):
        self.database.close()
    
    def testSunnyDay(self):
        
        # Table for individuals
        INDI_tbl = PrettyTable(field_names = [
            "ID",
            "First Name",
            "Last Name",
            "Sex",
            "Birth",
            "Death"
        ])

        # Table for families
        FAM_tbl = PrettyTable(field_names = [
            "Family ID",
            "Married",
            "Divorced",
            "Husband ID",
            "Husband First Name",
            "Husband Last Name",
            "Wife ID",
            "Wife First Name",
            "Wife Last Name",
            "Children"
        ])

        parser.parseFile(self.database, "input/project03test.ged")

        #adding information from database into individual prettytable
        for i in db.getIndividuals(self.database):
            INDI_tbl.add_row([x for x in i])

        #prints table of individuals
        print(INDI_tbl)

        #adding information from database into family prettytable
        for k in db.getFamilies(self.database):
            fam = [x for x in k]
            husb = db.getIndividual(self.database, fam[3])
            wife = db.getIndividual(self.database, fam[4])
            fam.insert(4, husb[1])
            fam.insert(5, husb[2])
            fam.insert(7, wife[1])
            fam.insert(8, wife[2])
            fam.insert(9, [x[0] for x in db.getChildren(self.database, fam[0])])

            FAM_tbl.add_row(fam)

        #prints table of families
        print(FAM_tbl)

    # validates all dates are before the current date
    def test_dateBFORcurrent(self):

        badBday = '''
            0 @I01@ INDI
            1 NAME Bad /Birthday/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 2030
            0 TRLR
        '''

        badDday = '''
            0 @I02@ INDI
            1 NAME Bad /Deathday/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 1985
            1 DEAT
            2 DATE 13 SEP 2030
            0 TRLR
        '''

        goodGuy = '''
            0 @I03@ INDI
            1 NAME Good /Guy1/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 1919
            1 DEAT
            2 DATE 13 SEP 1939
            1 FAMS @F1@
            0 TRLR
        '''

        goodGirl = '''
            0 @I04@ INDI
            1 NAME Good /Girl1/
            1 SEX F
            1 BIRT
            2 DATE 25 APR 1920
            1 DEAT
            2 DATE 13 SEP 1940
            1 FAMS @F1@
            0 TRLR
        '''

        badMar = '''
            0 @F1@ FAM
            1 HUSB @I3@
            1 WIFE @I4@
            1 MARR
            2 DATE 19 APR 2030
            0 TRLR
        '''

        badDiv = '''
            0 @F1@ FAM
            1 HUSB @I3@
            1 WIFE @I4@
            1 MARR
            2 DATE 19 APR 1960
            1 DIV
            2 DATE 14 NOV 2030
            0 TRLR
        '''

        self.assertFalse(parser.parseText(self.database, badBday))

        self.assertFalse(parser.parseText(self.database, badDday))

        self.assertTrue(parser.parseText(self.database, goodGuy))

        self.assertTrue(parser.parseText(self.database, goodGirl))

        self.assertFalse(parser.parseText(self.database, badMar))

        self.assertFalse(parser.parseText(self.database, badDiv))

    # validates the individual is born before marriage
    def test_birtBFORmarr(self):
        return

    # validates the individual is born before their death date
    def test_birtBFORdeat(self):
        return

    # validates that a couple was married before they got divorced
    def test_marrBFORdiv(self):
        return

unittest.main()