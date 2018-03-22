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
	if not (getIndividual(conn, idStr) is None):
		print("ERROR: INDIVIDUAL: Can't add individual " + idStr + ", duplicate of existing individual ID")
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
	if not (getFamily(conn, idStr) is None):
		print("ERROR: FAMILY: Can't add family " + idStr + ", duplicate of existing family ID")
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

	return conn.cursor().execute('SELECT * FROM INDIVIDUALS ORDER BY id').fetchall()



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

	return conn.cursor().execute(
		'SELECT childID FROM CHILDREN WHERE famID=?',
		(famID,)
	).fetchall()

# Apply a given SQL query to the database that should return a list of anomolies
# Print out the given error message for each row returned
# The error message should be a valid format string with flags for each column of the SQL query
# returns true if there are no anomolies, or false if there are
def checkAnomoly (conn, sql, msg):

	anomolies = conn.cursor().execute(sql).fetchall()
	formatter = string.Formatter()

	for a in anomolies:
		print(formatter.vformat(msg, a, None))

	return len(anomolies) == 0

def validateDatabase(conn):

	noerrors = True

	#US01 - dates before current date
	# future births
	noerrors &= checkAnomoly(conn,
		'''
		SELECT individuals.id
		FROM individuals
		WHERE individuals.birth > DATE('now')
		''',

		"ANOMALY: US01: Dates Before Current Date: Individual {} was born after today."
	)

	# future deaths
	noerrors &= checkAnomoly(conn,
		'''
		SELECT individuals.id
		FROM individuals
		WHERE individuals.death > DATE('now')
		''',

		"ANOMALY: US01: Dates Before Current Date: Individual {} died after today."
	)

	# future marriages
	noerrors &= checkAnomoly(conn,
		'''
		SELECT families.id
		FROM families
		WHERE families.married > DATE('now')
		''',

		"ANOMALY: US01 Dates Before Current Date: Family {} was married after today."
	)

	#future divorces
	noerrors &= checkAnomoly(conn,
		'''
		SELECT families.id
		FROM families
		WHERE families.divorced > DATE('now')
		''',

		"ANOMALY: US01: Dates Before Current Date: Family {} was divorced after today."
	)

	#US02 - birth before marriage
	noerrors &= checkAnomoly(conn,
		'''
		SELECT individuals.id
		FROM
			individuals INNER JOIN families
			ON (individuals.id=families.husbID) OR (individuals.id=families.wifeID)
		WHERE individuals.birth >= families.married
		''',

		"ANOMALY: US02: Birth Before Marriage: Individual {} was born on or before his/her wedding day."
	)

	#US03 - death before birth
	noerrors &= checkAnomoly(conn,
		'''
		SELECT individuals.id
		FROM individuals
		WHERE (individuals.death NOT NULL) AND (individuals.birth > individuals.death)
		''',

		"ANOMALY: US03: Death before Birth: Individual {} is born after their death."
	)

	#US04 - marriage before divorce
	noerrors &= checkAnomoly(conn,
		'''
		SELECT families.id
		FROM families
		WHERE (families.divorced NOT NULL) AND (families.divorced <= families.married)
		''',

		"ANOMALY: US04: Marriage Before Divorce: Family {} was divorced before their marriage"
	)

	#US05 - marriage before death
	noerrors &= checkAnomoly(conn,
		'''
		SELECT individuals.id
		FROM
			individuals INNER JOIN families
			ON (individuals.id=families.husbID) OR (individuals.id=families.wifeID)
		WHERE families.married > individuals.death
		''',

		"ANOMALY: US05: Marriage Before Death: Individual {} was married after their death"
	)

	#US16 - male last names
	noerrors &= checkAnomoly(conn,
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
	)

	#US18 - siblings should not marry
	noerrors &= checkAnomoly(conn,
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
	)

	#US21 - correct gender for roll
	noerrors &= checkAnomoly(conn,
		'''
		SELECT individuals.id
		FROM
			individuals INNER JOIN families
			ON
				(individuals.id == families.husbID AND individuals.gender == "F") OR
				(individuals.id == families.wifeID AND individuals.gender == "M")
		''',

		"ANOMALY: US21: Correct Gender For Role: Individual {} has the wrong gender for their family role."
	)

	return noerrors

def generateList(conn):

	#US29 - List Deceased
	checkAnomoly(conn,
		'''
		SELECT individuals.id
		FROM individuals
		WHERE individuals.death NOT NULL AND individuals.death < DATE('now')
		''',

		"LIST: US29: List Deceased: Individual {} is no longer alive."
	)

	#US30 - List living Married
	checkAnomoly(conn,
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

	#US32 - List living Married (not working)
	checkAnomoly(conn,
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
