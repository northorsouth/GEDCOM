#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#|Author(s): Nestor Ouranitsas, Dakota Crouchelli                                    |#
#|This script scans lines in a GEDCOM file for validity then prints a table of the   |#
#|individuals and the families, along with other information found in the gedcom file|#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys
import math
import datetime
from prettytable import PrettyTable

import GEDCOM_Database as db

# Which tags can be on which lines
tagRules = [
	(0, 'INDI'),
	(0, 'FAM'),
	(0, 'HEAD'),
	(0, 'TRLR'),
	(0, 'NOTE'),
	(1, 'NAME'),
	(1, 'SEX'),
	(1, 'BIRT'),
	(1, 'DEAT'),
	(1, 'FAMC'),
	(1, 'FAMS'),
	(1, 'MARR'),
	(1, 'HUSB'),
	(1, 'WIFE'),
	(1, 'CHIL'),
	(1, 'DIV'),
	(2, 'DATE')
]

#dictionary of months with numeric values as the keys
monthnums = {
	'JAN':1,
	'FEB':2,
	'MAR':3,
	'APR':4,
	'MAY':5,
	'JUN':6,
	'JUL':7,
	'AUG':8,
	'SEP':9,
	'OCT':10,
	'NOV':11,
	'DEC':12
}


#converts gedcom date sting into a python date time (yr, month, day)
def dateconvert(date):
    #converts date1 to the GEDCOM date format into python timedate format
    d = date.split()
    day = int(d[0])
    month = int(monthnums[d[1]])
    year = int(d[2])

    return datetime.date(year, month, day)



def parseLine(line):

	valid = False
	level = -1
	tag = None
	args = None

	# make sure this line has at least a level and a tag
	words = line.split()
	if len(words) >= 2:

		# level is always first
		level = int(words[0])

		# flag for INDI and FAM
		badOrder = False

		# order is switched for INDI and FAM
		if (len(words) >= 3 and
			(words[2] == 'INDI' or words[2] == 'FAM')):

			tag = words[2]
			args = [words[1]] + words[3:]

		else:
			tag = words[1]
			args = words[2:]

			# INDI and FAM should have been found in block above
			# if this trips, the order is wrong
			if tag == 'INDI' or tag == 'FAM':
				badOrder = True

		# if we find a matching tag rule, and the level checks out
		# tag is valid
		valid = (not badOrder) and ((level, tag) in tagRules)

	return (valid, level, tag, args)



def parseText(database, gedText):

	noErrors = True

	# Zero out variables
	indID = None
	firstName = None
	lastName = None
	gender = None
	birth = None
	death = None

	famID = None
	husband = None
	wife = None
	children = []
	married = None
	divorced = None

	lastTag = None

	# loop through lines
	for line in gedText.splitlines():

		valid = False
		level = -1
		newTag = None
		args = None

		(valid, level, newTag, args) = parseLine(line)

		# Make sure this line is valid before we do anything
		if (valid):

			# If we're at level zero, we may have captured a person or family
			if (level == 0):

				# Add an individual to the database
				if (lastName != None):

					noErrors = db.addIndividual(database, indID, firstName, lastName, gender, birth, death) and noErrors

					indID = None
					lastName = None
					firstName = None
					gender = None
					birth = None
					death = None

				# Add a family to the database
				elif (husband != None):

					noErrors  = db.addFamily(database, famID, married, divorced, husband, wife) and noErrors

					for child in children:
						noErrors  = db.addChild(database, child, famID) and noErrors

					famID = None
					husband = None
					wife = None
					married = None
					divorced = None
					children = []

			# Assign attributes based on the tag parsed
			if(newTag == 'INDI'):
				indID = args[0]
			elif (newTag == 'NAME'):
				lastName = args[-1][1:-1]
				firstName = " ".join(args[0:-1])
			elif (newTag == 'SEX'):
				gender = args[0]
			elif (lastTag == 'BIRT' and newTag == 'DATE'):
				birth = dateconvert(" ".join(args))
			elif (lastTag == 'DEAT' and newTag == 'DATE'):
				death = dateconvert(" ".join(args))

			if (newTag == 'FAM'):
				famID = args[0]
			elif (newTag == 'HUSB'):
				husband = args[0]
			elif (newTag == 'WIFE'):
				wife = args[0]
			elif (newTag == 'CHIL'):
				children.append(args[0])
			elif (lastTag == 'MARR' and newTag == 'DATE'):
				married = dateconvert(" ".join(args))
			elif (lastTag == 'DIV' and newTag == 'DATE'):
				divorced = dateconvert(" ".join(args))

			# Keep track of the tag before this one for birth and death dates
			lastTag = newTag
	
	valid = db.validateDatabase(database)

	return (noErrors and valid)

def parseFile(database, filePath):

	with open(filePath) as file:
		return parseText(database, file.read())

def printDatabase(database):
	
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

	#adding information from database into individual prettytable
	for i in db.getIndividuals(database):
		INDI_tbl.add_row([x for x in i])

	#prints table of individuals
	print(INDI_tbl)

	#adding information from database into family prettytable
	for k in db.getFamilies(database):
		fam = [x for x in k]
		husb = db.getIndividual(database, fam[3])
		wife = db.getIndividual(database, fam[4])
		fam.insert(4, husb[1])
		fam.insert(5, husb[2])
		fam.insert(7, wife[1])
		fam.insert(8, wife[2])
		fam.insert(9, [x[0] for x in db.getChildren(database, fam[0])])

		FAM_tbl.add_row(fam)

	#prints table of families
	print(FAM_tbl)

if len(sys.argv) > 1:

	database = db.dbInit("GEDCOM.db")

	for filepath in sys.argv[1:]:
		parseFile(database, filepath)
	
	printDatabase(database)