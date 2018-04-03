import sqlite3
from datetime import datetime
import os
import string

# Call this function to initialize the database tables
def dbInit(dbName):

	# Delete the database if it already exists
	try:
		os.remove(dbName)
	except FileNotFoundError:
		pass

	conn = sqlite3.connect(dbName)
	curs = conn.cursor()

	curs.execute("PRAGMA foreign_keys = ON")

	# Individuals table
	curs.execute('''CREATE TABLE individuals (
		id 			TEXT	PRIMARY KEY,
		firstName	TEXT,
		lastName 	TEXT,
		gender 		TEXT,
		birth 		DATE,
		death 		DATE
	)''')

	# Families table
	curs.execute('''CREATE TABLE families (
		id 			TEXT	PRIMARY KEY,
		married		DATE,
		divorced 	DATE,
		husbID 		TEXT,
		wifeID 		TEXT
	)''')

	# Children table (associates individuals with a family as a child
	curs.execute('''CREATE TABLE children (
		childID		TEXT,
		famID		TEXT,

		PRIMARY KEY (childID, famID)
	)''')

	conn.commit()

	return conn

# Add an individual to the DB
# Prints error and returns false if invalid
def addIndividual (conn, idStr, firstName, lastName, gender, birth, death):

	if conn is None:
		print("ERROR: INDIVIDUAL: Can't add individual, bad database paramter")
		return False
	if idStr is None:
		print("ERROR: INDIVIDUAL: Can't add individual, missing indiviudal ID")
		return False
	if firstName is None:
		print("ERROR: INDIVIDUAL: Can't add individual " + idStr + ", no first name")
		return False
	if lastName is None:
		print("ERROR: INDIVIDUAL: Can't add individual " + idStr + ", no last name")
		return False
	if gender is None:
		print("ERROR: INDIVIDUAL: Can't add individual " + idStr + ", gender missing gender")
		return False
	if gender.lower() != 'm' and gender.lower() != 'f':
		print("ERROR: INDIVIDUAL: Can't add individual " + idStr + ", bad gender tag")
		return False
	if birth is None:
		print("ERROR: INDIVIDUAL: Can't add individual " + idStr + ", no birthday")
		return False
	#US22 - Unique IDs
	if not (getIndividual(conn, idStr) is None):
		print("ERROR: US22: INDIVIDUAL: Can't add individual " + idStr + ", duplicate of existing individual ID")
		return False
	try:
		conn.cursor().execute(
			'INSERT INTO individuals VALUES (?, ?, ?, ?, ?, ?)',
			(idStr, firstName, lastName, gender, birth, death)
		)

	except sqlite3.IntegrityError as err:
		print("Couldn't add individual " + str(idStr) + ": " + str(err))
		return False

	conn.commit()

	return True


# Add an family to the DB (husband and wife must be already added)
# Prints error and returns false if invalid
def addFamily (conn, idStr, married, divorced, husbID, wifeID):

	if conn is None:
		print("ERROR: FAMILY: Can't add Family, bad database paramter")
		return False
	if idStr is None:
 		print("ERROR: FAMILY: Can't add Family, family ID missing")
 		return False
	if married is None:
 		print("ERROR: FAMILY: Can't add Family " + idStr + ", no marriage date")
 		return False
	if husbID is None:
 		print("ERROR: FAMILY: Can't add Family " + idStr + ", no individual ID for husband.")
 		return False
	if wifeID is None:
 		print("ERROR: FAMILY: Can't add Family " + idStr + ", no individual ID for wife.")
 		return False
	if (getIndividual(conn, wifeID) is None):
		print("ERROR: FAMILY: Can't add Family " + idStr + ", wife does not exist")
		return False
	if (getIndividual(conn, husbID) is None):
		print("ERROR: FAMILY: Can't add Family " + idStr + ", husband does not exist")
		return False
	#US22 - Unique IDs
	if not (getFamily(conn, idStr) is None):
		print("ERROR: US22: FAMILY: Can't add family " + idStr + ", duplicate of existing family ID")
		return False
	try:
		conn.cursor().execute(
			'INSERT INTO families VALUES (?, ?, ?, ?, ?)',
			(idStr, married, divorced, husbID, wifeID)
		)

	except sqlite3.IntegrityError as err:
		print("Couldn't add family " + str(idStr) + ": " + str(err))
		return False

	conn.commit()

	return True



# Add a child t a family (family must already exist)
# Prints error and returns false if invalid
def addChild (conn, childID, famID):

	if conn is None:
		print("ERROR: CHILD: Can't add Child, bad database paramter")
		return False
	if childID is None:
		print("ERROR: CHILD: Can't add Child, missing Child ID")
		return False
	if famID is None:
		print("ERROR: CHILD: Can't add Child, missing Family ID")
		return False

	try:
		conn.cursor().execute(
			'INSERT INTO children VALUES (?, ?)',
			(childID, famID)
		)

	except sqlite3.IntegrityError as err:
		print("Couldn't add child " + str(childID) + ": " + str(err))
		return False

	conn.commit()

	return True


# Get a list of all invdividuals as tuples
def getIndividuals(conn):

	return conn.cursor().execute(
		'''SELECT * FROM INDIVIDUALS ORDER BY birth'''
	).fetchall()



# Get a certain individual by his ID
def getIndividual(conn, indID):

	return conn.cursor().execute(
		'SELECT * FROM INDIVIDUALS WHERE id=?',
		(indID,)
	).fetchone()



# Get a list of all families as tuples
def getFamilies(conn):

	return conn.cursor().execute('SELECT * FROM FAMILIES ORDER BY id').fetchall()



# Get a certain family by their ID
def getFamily(conn, famID):

	return conn.cursor().execute(
		'SELECT * FROM FAMILIES WHERE id=?',
		(famID,)
	).fetchone()


# Get all children in a given family as an array of IDs
def getChildren(conn, famID):

	return conn.cursor().execute('''
		SELECT children.childID
		FROM children
		WHERE famID=?
	''', (famID,)
	).fetchall()

# Apply a given SQL query to the database that should return a list of results
# Print out the given string for each row returned
# The string should be a valid format string with flags for each column of the SQL query
# returns the raw rows
def printQuery (conn, sql, msg):

	rows = conn.cursor().execute(sql).fetchall()
	formatter = string.Formatter()

	for row in rows:
		print(formatter.vformat(msg, row, None))

	return rows

def validateDatabase(conn):

	noerrors = True

	#US01 - dates before current date
	# future births
	noerrors &= len(printQuery(conn,
		'''
		SELECT individuals.id
		FROM individuals
		WHERE individuals.birth > DATE('now')
		''',

		"ANOMALY: US01: Dates Before Current Date: Individual {} was born after today."
	)) == 0

	# future deaths
	noerrors &= len(printQuery(conn,
		'''
		SELECT individuals.id
		FROM individuals
		WHERE individuals.death > DATE('now')
		''',

		"ANOMALY: US01: Dates Before Current Date: Individual {} died after today."
	)) == 0

	# future marriages
	noerrors &= len(printQuery(conn,
		'''
		SELECT families.id
		FROM families
		WHERE families.married > DATE('now')
		''',

		"ANOMALY: US01 Dates Before Current Date: Family {} was married after today."
	)) == 0

	#future divorces
	noerrors &= len(printQuery(conn,
		'''
		SELECT families.id
		FROM families
		WHERE families.divorced > DATE('now')
		''',

		"ANOMALY: US01: Dates Before Current Date: Family {} was divorced after today."
	)) == 0

	#US02 - birth before marriage
	noerrors &= len(printQuery(conn,
		'''
		SELECT individuals.id
		FROM
			individuals INNER JOIN families
			ON (individuals.id=families.husbID) OR (individuals.id=families.wifeID)
		WHERE individuals.birth >= families.married
		''',

		"ANOMALY: US02: Birth Before Marriage: Individual {} was born on or before his/her wedding day."
	)) == 0

	#US03 - death before birth
	noerrors &= len(printQuery(conn,
		'''
		SELECT individuals.id
		FROM individuals
		WHERE (individuals.death NOT NULL) AND (individuals.birth > individuals.death)
		''',

		"ANOMALY: US03: Death before Birth: Individual {} is born after their death."
	)) == 0

	#US04 - marriage before divorce
	noerrors &= len(printQuery(conn,
		'''
		SELECT families.id
		FROM families
		WHERE (families.divorced NOT NULL) AND (families.divorced <= families.married)
		''',

		"ANOMALY: US04: Marriage Before Divorce: Family {} was divorced before their marriage"
	)) == 0

	#US05 - marriage before death
	noerrors &= len(printQuery(conn,
		'''
		SELECT individuals.id
		FROM
			individuals INNER JOIN families
			ON (individuals.id=families.husbID) OR (individuals.id=families.wifeID)
		WHERE families.married > individuals.death
		''',

		"ANOMALY: US05: Marriage Before Death: Individual {} was married after their death"
	)) == 0

	#US16 - male last names
	noerrors &= len(printQuery(conn,
		'''
		SELECT i1.id
		FROM
			individuals AS i1 INNER JOIN children AS c
			ON (i1.ID = c.childID)
			INNER JOIN families AS f
			ON (c.famID = f.id)
			INNER JOIN individuals AS i2
			ON (f.husbID = i2.id)
		WHERE i1.gender == "M" AND i2.lastName != i1.lastName
		''',

		"ANOMALY: US16: Male Last Names: Individual {} does not have the same last name as their father."
	)) == 0

	#US18 - siblings should not marry
	noerrors &= len(printQuery(conn,
		'''
		SELECT f.id
		FROM
			families as f
			INNER JOIN children as husbFam
			ON f.husbID == husbFam.childID
			INNER JOIN children as wifeFam
			ON f.wifeID == wifeFam.childID
		WHERE husbFam.famID == wifeFam.famID
		''',

		"ANOMALY: US18: Siblings should not marry: The spouses in family {} are siblings."
	)) == 0

	#US21 - correct gender for roll
	noerrors &= len(printQuery(conn,
		'''
		SELECT individuals.id
		FROM
			individuals INNER JOIN families
			ON
				(individuals.id == families.husbID AND individuals.gender == "F") OR
				(individuals.id == families.wifeID AND individuals.gender == "M")
		''',

		"ANOMALY: US21: Correct Gender For Role: Individual {} has the wrong gender for their family role."
	)) == 0

	#US23 - Unique Name and Births
	noerrors &= len(printQuery(conn,
		'''
		SELECT ind1.id, ind2.id
		FROM
			individuals as ind1 INNER JOIN
			individuals as ind2 ON
			ind1.id != ind2.id AND
			ind1.birth == ind2.birth AND ind1.firstname==ind2.firstname AND ind1.lastname==ind2.lastname
		''',

		"ANOMALY: US23: Unique Name and Birth: Individual {} has the same Name and Birthday as {}."
	)) == 0

	return noerrors


#US29 - List Deceased
def printDeceased(conn):
	return printQuery(conn,
		'''
		SELECT individuals.id
		FROM individuals
		WHERE individuals.death NOT NULL AND individuals.death < DATE('now')
		''',

		"LIST: US29: List Deceased: Individual {} is no longer alive."
	)

#US30 - List living Married
def printLivingMarried(conn):
	return printQuery(conn,
		'''
		SELECT husband.id
		FROM
			individuals as husband INNER JOIN families
			ON (husband.id=families.husbID)
			INNER JOIN individuals as wife
			ON (wife.id=families.wifeID)
		WHERE families.divorced IS NULL AND husband.death IS NULL AND wife.death IS NULL
		UNION
		SELECT wife.id
		FROM
			individuals as wife INNER JOIN families
			ON (wife.id=families.wifeID)
			INNER JOIN individuals as husband
			ON (husband.id=families.husbID)
		WHERE families.divorced IS NULL AND husband.death IS NULL AND wife.death IS NULL

		''',

		"LIST: US30: List Living Married: Individual {} is married and alive."
	)

#US32 - Multiple Births
def printMultipleBirths(conn):
	return printQuery(conn,
		'''
		SELECT DISTINCT child1.id, child1Link.famID, child1.birth
		FROM
			individuals as child1
			INNER JOIN individuals as child2
			ON child1.id != child2.id
			INNER JOIN children as child1Link ON
			child1.id == child1Link.childID
			INNER JOIN children as child2Link ON
			child2.id == child2Link.childID
		WHERE child1Link.famID == child2Link.famID AND child1.birth == child2.birth
		ORDER BY child1.birth, child1Link.famID
		''',

		"LIST: US32: List Multiple Births: Individual {} was part of a multiple birth in family {} on {}."
	)
