#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#|Author(s): Nestor Ouranitsas, Dakota Crouchelli                                    |#
#|This script scans lines in a GEDCOM file for validity then prints a table of the   |#
#|individuals and the families, along with other information found in the gedcom file|#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

import os
import sqlite3
import sys
from prettytable import PrettyTable

dbName = "GEDCOM.db"

tagRules =[
	(0, 'INDI'),
	(1, 'NAME'),
	(1, 'SEX'),
	(1, 'BIRT'),
	(1, 'DEAT'),
	(1, 'FAMC'),
	(1, 'FAMS'),
	(0, 'FAM'),
	(1, 'MARR'),
	(1, 'HUSB'),
	(1, 'WIFE'),
	(1, 'CHIL'),
	(1, 'DIV'),
	(2, 'DATE'),
	(0, 'HEAD'),
	(0, 'TRLR'),
	(0, 'NOTE')
]

def dbInit():

	try:
		os.remove(dbName);
	except FileNotFoundError:
		pass

	conn = sqlite3.connect(dbName)
	curs = conn.cursor()

	curs.execute('''CREATE TABLE individuals (
		id 			TEXT	NOT NULL	PRIMARY KEY,
		firstName	TEXT	NOT NULL,
		lastName 	TEXT	NOT NULL,
		gender 		TEXT	NOT NULL,
		birth 		DATE	NOT NULL,
		death 		DATE,

		CHECK (gender in ("M", "F"))
	)''')

	curs.execute('''CREATE TABLE families (
		id 			TEXT	NOT NULL	PRIMARY KEY,
		married		DATE	NOT NULL,
		divorced 	DATE,
		husbID 		TEXT	NOT NULL,
		wifeID 		TEXT	NOT NULL,

		FOREIGN KEY (husbID) REFERENCES individuals(id),
		FOREIGN KEY (wifeID) REFERENCES individuals(id)
	)''')

	curs.execute('''CREATE TABLE children (
		childID		TEXT	NOT NULL,
		famID		TEXT	NOT NULL,

		PRIMARY KEY (childID, famID),

		FOREIGN KEY (childID) REFERENCES individuals(id),
		FOREIGN KEY (famID) REFERENCES families(id)
	)''')

	conn.commit()

	return conn

def addIndividual (idStr, firstName, lastName, gender, birth, death):

	result = True

	try:
		conn.cursor().execute(
			'INSERT INTO individuals VALUES (?, ?, ?, ?, ?, ?)',
			(idStr, firstName, lastName, gender, birth, death)
		)

	except sqlite3.IntegrityError as err:
		print("Couldn't add individual " + str(idStr) + ": " + str(err))
		result = False

	conn.commit()

	return result



def addFamily (idStr, married, divorced, husbID, wifeID):

	result = True

	try:
		conn.cursor().execute(
			'INSERT INTO families VALUES (?, ?, ?, ?, ?)',
			(idStr, married, divorced, husbID, wifeID)
		)

	except sqlite3.IntegrityError as err:
		print("Couldn't add family " + str(idStr) + ": " + str(err))
		result = False

	conn.commit()

	return result



def addChild (childID, famID):

	result = True

	try:
		conn.cursor().execute(
			'INSERT INTO children VALUES (?, ?)',
			(childID, famID)
		)

	except sqlite3.IntegrityError as err:
		print("Couldn't add child " + str(childID) + ": " + str(err))
		result = False

	conn.commit()

	return result



def getIndividuals():

	return conn.cursor().execute('SELECT * FROM INDIVIDUALS ORDER BY id').fetchall()



def getIndividual(indID):

	return conn.cursor().execute(
		'SELECT * FROM INDIVIDUALS WHERE id=?',
		(indID,)
	).fetchone()



def getFamilies():

	return conn.cursor().execute('SELECT * FROM FAMILIES ORDER BY id').fetchall()



def getFamily(famID):

	return conn.cursor().execute(
		'SELECT * FROM FAMILIES WHERE id=?',
		(famID,)
	).fetchone()



def getChildren(famID):

	return conn.cursor().execute(
		'SELECT childID FROM CHILDREN WHERE famID=?',
		(famID,)
	).fetchall()


#Table for individuals
INDI_tbl = PrettyTable()
INDI_tbl.field_names = ["ID","First Name","Last Name","Sex","Birth","Death"]

#Table for families
FAM_tbl = PrettyTable()
FAM_tbl.field_names = ["Family ID","Married","Divorced","Husband ID","Husband First Name", "Husband Last Name", "Wife ID", "Wife First Name", "Wife Last Name", "Children"]

# if a file name was passed in
if len(sys.argv) > 1:

	conn = dbInit()

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

			#prints indiviual's info into table
			if (level == 0):

				if (lastName != None):
					addIndividual(indID, firstName, lastName, gender, birth, death)
					indID = None
					lastName = None
					firstName = None
					gender = None
					birth = None
					death = None

				elif (husband != None):
					addFamily(famID, married, divorced, husband, wife)

					for child in children:
						addChild(child, famID)

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

			lastTag = tag

#adding information from database into individual prettytable
for i in getIndividuals():
	INDI_tbl.add_row([x for x in i])

#prints table of individuals
print(INDI_tbl)

#adding information from database into family prettytable
for k in getFamilies():
	fam = [x for x in k]
	husb = getIndividual(fam[3])
	wife = getIndividual(fam[4])
	fam.insert(4, husb[1])
	fam.insert(5, husb[2])
	fam.insert(7, wife[1])
	fam.insert(8, wife[2])
	fam.insert(9, [x[0] for x in getChildren(fam[0])])

	FAM_tbl.add_row(fam)

#prints table of families
print(FAM_tbl)

conn.close()
