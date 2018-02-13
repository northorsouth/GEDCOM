#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#|Author(s): Nestor Ouranitsas, Dakota Crouchelli                                    |#
#|This script scans lines in a GEDCOM file for validity then prints a table of the   |#
#|individuals and the families, along with other information found in the gedcom file|#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import sys
from prettytable import PrettyTable

from GEDCOM_Database import *

database = None

# Which tags can be on which lines
tagRules =[
	(0, 'INDI'),(0, 'FAM'),(0, 'HEAD'),(0, 'TRLR'),(0, 'NOTE'),
	(1, 'NAME'),(1, 'SEX'),(1, 'BIRT'),(1, 'DEAT'),(1, 'FAMC'),(1, 'FAMS'),(1, 'MARR'),(1, 'HUSB'),(1, 'WIFE'),(1, 'CHIL'),(1, 'DIV'),
	(2, 'DATE')
]


# Table for individuals
INDI_tbl = PrettyTable()
INDI_tbl.field_names = ["ID","First Name","Last Name","Sex","Birth","Death"]

# Table for families
FAM_tbl = PrettyTable()
FAM_tbl.field_names = ["Family ID","Married","Divorced","Husband ID","Husband First Name", "Husband Last Name", "Wife ID", "Wife First Name", "Wife Last Name", "Children"]

# if a file name was passed in
if len(sys.argv) > 1:

	# Create tables
	database = dbInit("GEDCOM.db")

	# Zero out global variables
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
	for line in open(sys.argv[1]):

		valid = False
		level = -1
		tag = None
		args = None

		# make sure this line has at least a level and a tag
		words = line.split()
		if len(words) >= 2:

			# level is always first
			level = int(words[0])

			# If we're at level zero, we may have captured a person or family
			if (level == 0):

				# Add an individual to the database
				if (lastName != None):
					addIndividual(database, indID, firstName, lastName, gender, birth, death)
					indID = None
					lastName = None
					firstName = None
					gender = None
					birth = None
					death = None

				# Add a family to the database
				elif (husband != None):
					addFamily(database, famID, married, divorced, husband, wife)

					for child in children:
						addChild(database, child, famID)

					famID = None
					husband = None
					wife = None
					married = None
					divorced = None
					children = []

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

			# guilty until proven innocent
			valid = False

			# if we find a matching tag rule, and the level checks out
			# tag is valid
			if not badOrder:
				for tagRule in tagRules:
					if tagRule[1]==tag and tagRule[0]==level:
						valid = True

			# Assign attributes based on the tag parsed
			if(tag == 'INDI'):
				indID = args[0]
			elif (tag == 'NAME'):
				lastName = args[-1][1:-1]
				firstName = " ".join(args[0:-1])
			elif (tag == 'SEX'):
				gender = args[0]
			elif (lastTag == 'BIRT' and tag == 'DATE'):
				birth = " ".join(args)
			elif (lastTag == 'DEAT' and tag == 'DATE'):
				death = " ".join(args)

			if (tag == 'FAM'):
				famID = args[0]
			elif (tag == 'HUSB'):
				husband = args[0]
			elif (tag == 'WIFE'):
				wife = args[0]
			elif (tag == 'CHIL'):
				children.append(args[0])
			elif (lastTag == 'MARR' and tag == 'DATE'):
				married = " ".join(args)
			elif (lastTag == 'DIV' and tag == 'DATE'):
				divorced = " ".join(args)

			# Keep track of the tag before this one for birth and death dates
			lastTag = tag

#adding information from database into individual prettytable
for i in getIndividuals(database):
	INDI_tbl.add_row([x for x in i])

#prints table of individuals
print(INDI_tbl)

#adding information from database into family prettytable
for k in getFamilies(database):
	fam = [x for x in k]
	husb = getIndividual(database, fam[3])
	wife = getIndividual(database, fam[4])
	fam.insert(4, husb[1])
	fam.insert(5, husb[2])
	fam.insert(7, wife[1])
	fam.insert(8, wife[2])
	fam.insert(9, [x[0] for x in getChildren(database, fam[0])])

	FAM_tbl.add_row(fam)

#prints table of families
print(FAM_tbl)

database.close()
