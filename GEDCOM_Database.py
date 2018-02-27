import sqlite3
from datetime import datetime
import os

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
 		print("ERROR: FAMILY: Can't add Family, no marriage date")
 		return False
	if husbID is None:
 		print("ERROR: FAMILY: Can't add Family, no individual ID for husband.")
 		return False
	if wifeID is None:
 		print("ERROR: FAMILY: Can't add Family, no individual ID for wife.")
 		return False
	if (getIndividual(conn, wifeID) is None):
		print("ERROR: FAMILY: Can't add Family, wife does not exist")
		return False
	if (getIndividual(conn, husbID) is None):
		print("ERROR: FAMILY: Can't add Family, husband does not exist")
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

def validateDatabase(conn):

	noerrors = True

	#US01 - dates before current date
	# future births
	futurebirths = [
		indi[0] for indi in
		filter(
			lambda indi: indi[4] > str(datetime.now()),
			getIndividuals(conn)
		)
	]

	if (len(futurebirths) > 0):
		for s in futurebirths:
			print("ERROR: US01: Dates Before Current Date: Individual " + s + " was born after today.")
		noerrors = False

	# future deaths
	futuredeaths = [
		indi[0] for indi in
		filter(
			lambda indi: indi[5] != None and indi[5] > str(datetime.now()),
			getIndividuals(conn)
		)
	]

	if (len(futuredeaths) > 0):
		for s in futuredeaths:
			print("ERROR: US01: Dates Before Current Date: Individual " + s + " died after today.")
		noerrors = False

	# future marriages
	furturemarriages = [
		fam[0] for fam in
		filter(
			lambda fam: fam[1] > str(datetime.now()),
			getFamilies(conn)
		)
	]

	if (len(furturemarriages) > 0):
		for s in furturemarriages:
			print("ERROR: US01 Dates Before Current Date: Family " + s + " was married after today.")
		noerrors = False

	#future divorces
	futuredivorces = [
		fam[0] for fam in
		filter(
			lambda fam: fam[2] != None and fam[2] > str(datetime.now()),
			getFamilies(conn)
		)
	]

	if (len(futuredivorces) > 0):
		for s in futuredivorces:
			print("ERROR: US01: Dates Before Current Date: Family " + s + " was divorced after today.")
		noerrors = False

	#US02 - birth before marriage
	impossibleSpouses = [row[0] for row in conn.cursor().execute('''
		SELECT individuals.id
		FROM
			individuals INNER JOIN families
			ON (individuals.id=families.husbID) OR (individuals.id=families.wifeID)
		WHERE individuals.birth >= families.married'''
	).fetchall()]

	if (len(impossibleSpouses) > 0):
		for s in impossibleSpouses:
			print("ERROR: US02: Birth Before Marriage: Individual " + s + " was born on or before his/her wedding day.")
		noerrors = False

	#US03 - death before birth
	backwardsbirths = [row[0] for row in conn.cursor().execute('''
		SELECT individuals.id
		FROM individuals
		WHERE (individuals.death NOT NULL) AND (individuals.birth > individuals.death) '''
	).fetchall()]

	if (len(backwardsbirths) > 0):
		for s in backwardsbirths:
			print("ERROR: US03: Death before Birth: Individual " + s + " is born after their death.")
		noerrors = False

	#US04 - marriage before divorce
	futuremarriage = [row[0] for row in conn.cursor().execute('''
		SELECT families.id
		FROM families
		WHERE (families.divorced NOT NULL) AND (families.divorced <= families.married) '''
	).fetchall()]

	if (len(futuremarriage) > 0):
		for s in futuremarriage:
			print("ERROR: US04: Marriage Before Divorce: Family " + s + " was divorced before their marriage")
		noerrors = False
	
	#US05 - marriage before death
	corpsebrides = [row[0] for row in conn.cursor().execute('''
		SELECT individuals.id
		FROM
			individuals INNER JOIN families
			ON (individuals.id=families.husbID) OR (individuals.id=families.wifeID)
		WHERE families.married > individuals.death'''
	).fetchall()]

	if (len(corpsebrides) > 0):
		for s in corpsebrides:
			print("ERROR: US05: Marriage Before Death: Individual " + s + " was married after their death")
		noerrors = False

	return noerrors
