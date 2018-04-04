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

    # US01 - validates birthdays are before the current date
    def test_dateBFORcurrent_1(self):

        badBday = '''
            0 @I1@ INDI
            1 NAME Bad /Birthday/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 2030
            0 TRLR
        '''

        self.assertFalse(parser.parseText(self.database, badBday))

    # US01 - validates death dates are before the current date
    def test_dateBFORcurrent_2(self):

        badDday = '''
            0 @I2@ INDI
            1 NAME Bad /Deathday/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 1985
            1 DEAT
            2 DATE 13 SEP 2030
            0 TRLR
        '''

        self.assertFalse(parser.parseText(self.database, badDday))

    # US01 - validates all marriages are before the current date
    def test_dateBFORcurrent_3(self):

        goodGuy = '''
            0 @I3@ INDI
            1 NAME Good /Guy1/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 1919
            1 FAMS @F1@
            0 TRLR
        '''

        goodGirl = '''
            0 @I4@ INDI
            1 NAME Good /Girl1/
            1 SEX F
            1 BIRT
            2 DATE 25 APR 1920
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

        self.assertTrue(parser.parseText(self.database, goodGuy))

        self.assertTrue(parser.parseText(self.database, goodGirl))

        self.assertFalse(parser.parseText(self.database, badMar))

    # US01 - validates all divorce dates are before the current date
    def test_dateBFORcurrent_4(self):

        goodGuy = '''
            0 @I3@ INDI
            1 NAME Good /Guy1/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 1919
            1 FAMS @F1@
            0 TRLR
        '''

        goodGirl = '''
            0 @I4@ INDI
            1 NAME Good /Girl1/
            1 SEX F
            1 BIRT
            2 DATE 25 APR 1920
            1 FAMS @F1@
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

        self.assertTrue(parser.parseText(self.database, goodGuy))

        self.assertTrue(parser.parseText(self.database, goodGirl))

        self.assertFalse(parser.parseText(self.database, badDiv))

    # US02 - Wife was born after wedding
    def test_birtBFORmarr_1(self):

        # Wife was born after wedding
        guy1 = '''
            0 @I3@ INDI
            1 NAME Woody /Allen/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 192
            1 FAMS @F1@
            0 TRLR
            '''

        girl1 = '''
            0 @I4@ INDI
            1 NAME Soon Yi /Previn/
            1 SEX F
            1 BIRT
            2 DATE 25 APR 1950
            1 FAMS @F1@
            0 TRLR
        '''

        fam1 = '''
            0 @F1@ FAM
            1 HUSB @I3@
            1 WIFE @I4@
            1 MARR
            2 DATE 19 APR 1940
            0 TRLR
        '''

        self.assertTrue(parser.parseText(self.database, guy1))

        self.assertTrue(parser.parseText(self.database, girl1))

        self.assertFalse(parser.parseText(self.database, fam1))

    # US02 - husband was born after wedding
    def test_birtBFORmarr_2(self):
        guy2 = '''
            0 @I5@ INDI
            1 NAME Woody /Allen/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 1950
            1 FAMS @F2@
            0 TRLR
            '''

        girl2 = '''
            0 @I6@ INDI
            1 NAME Soon Yi /Previn/
            1 SEX F
            1 BIRT
            2 DATE 25 APR 1920
            1 FAMS @F2@
            0 TRLR
        '''

        fam2 = '''
            0 @F2@ FAM
            1 HUSB @I5@
            1 WIFE @I6@
            1 MARR
            2 DATE 19 APR 1940
            0 TRLR
        '''

        self.assertTrue(parser.parseText(self.database, guy2))

        self.assertTrue(parser.parseText(self.database, girl2))

        self.assertFalse(parser.parseText(self.database, fam2))

    # US03 - validates the individual is born before their death date
    def test_birtBFORdeat(self):
        self.assertFalse(parser.parseFile(self.database, "input/US03test.ged"))

    # US04 - validates that a couple was married before they got divorced
    def test_marrBFORdiv(self):
        self.assertFalse(parser.parseFile(self.database, "input/US04test.ged"))

    # US05 - validates that a marriage is before a death
    def test_marrBFORdeath(self):
        self.assertFalse(parser.parseFile(self.database, "input/US05test.ged"))

    # US29 - asserts that printDeceased prints all dead people
    def test_deceased(self):
        self.assertTrue(parser.parseFile(self.database, "input/project03test.ged"))

        dead = db.printDeceased(self.database)

        self.assertEqual(len(dead), 4)
        self.assertIn(("I01",), dead)
        self.assertIn(("I02",), dead)
        self.assertIn(("I06",), dead)
        self.assertIn(("I08",), dead)

    # US34 - asserts that printLargeAgeDifferences includes the correct individuals
    def test_largeagedifferences(self):
        self.assertTrue(parser.parseFile(self.database, "input/US34test.ged"))

        LargeAgeDifference = db.printLargeAgeDifferences(self.database)
        print(LargeAgeDifference)

        self.assertEqual(len(LargeAgeDifference), 2)
        self.assertIn(("I01", "I02"), LargeAgeDifference) #husband age 2x wife age
        self.assertIn(("I04", "I03"), LargeAgeDifference) #wife age 2x husband age

#tests all user stories dealing with family relationships
class familyTest(unittest.TestCase):

    def setUp(self):
        print("\n\ntesting: " + self._testMethodName)
        self.database = db.dbInit("GEDCOM.db")

    def tearDown(self):
        self.database.close()

    # US16 - validates that no male children have a different last name than their father (US16)
    def test_maleLastNames(self):
        self.assertFalse(parser.parseFile(self.database, "input/US16test.ged"))

    # US18 - validates that no siblings are married
    def test_siblingsShouldNotMarry(self):
        self.assertFalse(parser.parseFile(self.database, "input/US18test.ged"))

    # Validates that the spouses must already exist for a family to be created
    def test_spousesExist_1(self):

        goodGuy = '''
            0 @I3@ INDI
            1 NAME Good /Guy1/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 1919
            1 DEAT
            2 DATE 13 SEP 1939
            1 FAMS @F1@
            0 TRLR
        '''

        fam1 = '''
            0 @F1@ FAM
            1 HUSB @I3@
            1 WIFE @I4@
            1 MARR
            2 DATE 19 APR 1960
            0 TRLR
        '''

        self.assertTrue(parser.parseText(self.database, goodGuy))

        self.assertFalse(parser.parseText(self.database, fam1))

    # Validates that the spouses must already exist for a family to be created
    def test_spousesExist_2(self):
        goodGirl = '''
            0 @I5@ INDI
            1 NAME Good /Girl1/
            1 SEX F
            1 BIRT
            2 DATE 25 APR 1920
            1 DEAT
            2 DATE 13 SEP 1940
            1 FAMS @F2@
            0 TRLR
        '''

        fam2 = '''
            0 @F2@ FAM
            1 HUSB @I6@
            1 WIFE @I5@
            1 MARR
            2 DATE 19 APR 1960
            0 TRLR
        '''

        self.assertTrue(parser.parseText(self.database, goodGirl))

        self.assertFalse(parser.parseText(self.database, fam2))

    # US32 - Asserts that printMultipleBirths prints the triplets in the test file
    def test_multipleBirths(self):
        self.assertTrue(parser.parseFile(self.database, "input/US32test.ged"))

        multBirths = db.printMultipleBirths(self.database)

        self.assertEqual(len(multBirths), 3)
        self.assertIn(("I03", "F01", "1962-08-29"), multBirths)
        self.assertIn(("I04", "F01", "1962-08-29"), multBirths)
        self.assertIn(("I05", "F01", "1962-08-29"), multBirths)

    # US30 - asserts that printLivingMarried prints all the living married people
    def test_livingMarried(self):
        self.assertTrue(parser.parseFile(self.database, "input/project03test.ged"))

        livingMarried = db.printLivingMarried(self.database)

        self.assertEqual(len(livingMarried), 2)
        self.assertIn(("I05",), livingMarried)
        self.assertIn(("I11", ), livingMarried)

    # US28 - asserts that siblings in the output table are sorted by birthday
    def test_sortedSiblings(self):
        self.assertTrue(parser.parseFile(self.database, "input/US28test.ged"))

        indies = db.getIndividuals(self.database)

        for i in range(1, len(indies)-1):
            self.assertGreaterEqual(indies[i][4], indies[i-1][4])

        for fam in db.getFamilies(self.database):
            children = db.getChildren(self.database, fam[0])

            for i in range(1, len(children)-1):
                self.assertGreaterEqual(
                    db.getIndividual(self.database, children[i][0])[4],
                    db.getIndividual(self.database, children[i-1][0])[4])

    # US33 - Asserts that printOrphans finds all the orphans it should
    def test_orphans(self):
        self.assertTrue(parser.parseFile(self.database, "input/US33test.ged"))

        orphans = db.printOrphans(self.database)

        self.assertEqual(len(orphans), 1)
        self.assertIn(("I03",), orphans)

#tests miscellaneous user stories
class miscTest(unittest.TestCase):

    def setUp(self):
        print("\n\ntesting: " + self._testMethodName)
        self.database = db.dbInit("GEDCOM.db")

    def tearDown(self):
        self.database.close()

    # US21 - validates that individuals have the correct family role for their Gender
    def test_roleswap(self):
        self.assertFalse(parser.parseFile(self.database, "input/US21test.ged"))

    # Sunny day test, nothing should go wrong here
    def test_sunnyday(self):
        self.assertTrue(parser.parseFile(self.database, "input/project03test.ged"))

        parser.printDatabase(self.database)

    # US22 - validates that no two individuals have the same individual ID
    def test_duplicateIndIDs(self):
        self.assertFalse(parser.parseFile(self.database, "input/US22test_1.ged"))

    # US22 - validates that no two families have the same family ID
    def test_duplicateFamIDs(self):
        self.assertFalse(parser.parseFile(self.database, "input/US22test_2.ged"))

    # US23 - validates that no two individuals have the same name and birthday
    def test_samePerson(self):

        guy1 = '''
            0 @I3@ INDI
            1 NAME Good /Guy1/
            1 SEX M
            1 BIRT
            2 DATE 25 APR 1919
            1 DEAT
            2 DATE 13 SEP 1939
            0 TRLR
        '''

        guy2 = '''
            0 @I4@ INDI
            1 NAME Good /Guy1/
            1 SEX F
            1 BIRT
            2 DATE 25 APR 1919
            0 TRLR
        '''

        self.assertTrue(parser.parseText(self.database, guy1))
        self.assertFalse(parser.parseText(self.database, guy2))



unittest.main()
