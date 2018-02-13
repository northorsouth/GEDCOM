import sqlite3
import os

# Call this function to initialize the database tables
def dbInit(dbName):

	# Delete the database if it already exists
	try:
		os.remove(dbName);
	except FileNotFoundError:
		pass

	conn = sqlite3.connect(dbName)
	curs = conn.cursor()

	# Individuals table
	curs.execute('''CREATE TABLE individuals (
		id 			TEXT	NOT NULL	PRIMARY KEY,
		firstName	TEXT	NOT NULL,
		lastName 	TEXT	NOT NULL,
		gender 		TEXT	NOT NULL,
		birth 		DATE	NOT NULL,
		death 		DATE,

		CHECK (gender in ("M", "F")),
		CHECK (birth < DATE('now')),
		CHECK (death IS NULL OR death < DATE('now'))
	)''')

	# Families table
	curs.execute('''CREATE TABLE families (
		id 			TEXT	NOT NULL	PRIMARY KEY,
		married		DATE	NOT NULL,
		divorced 	DATE,
		husbID 		TEXT	NOT NULL,
		wifeID 		TEXT	NOT NULL,

		FOREIGN KEY (husbID) REFERENCES individuals(id),
		FOREIGN KEY (wifeID) REFERENCES individuals(id),
		CHECK (married < DATE('now')),
		CHECK (divorced IS NULL OR divorced < DATE('now'))
	)''')

	# Children table (associates individuals with a family as a child
	curs.execute('''CREATE TABLE children (
		childID		TEXT	NOT NULL,
		famID		TEXT	NOT NULL,

		PRIMARY KEY (childID, famID),

		FOREIGN KEY (childID) REFERENCES individuals(id),
		FOREIGN KEY (famID) REFERENCES families(id)
	)''')

	conn.commit()
	
	return conn

# Add an individual to the DB
# Prints error and returns false if invalid
def addIndividual (conn, idStr, firstName, lastName, gender, birth, death):

	try:
		conn.cursor().execute(
			'INSERT INTO individuals VALUES (?, ?, ?, ?, ?, ?)',
			(idStr, firstName, lastName, gender, birth, death)
		)

	except sqlite3.IntegrityError as err:
		print("Couldn't add individual " + str(idStr) + ": " + str(err))
		return False

	conn.commit()



# Add an family to the DB (husband and wife must be already added)
# Prints error and returns false if invalid
def addFamily (conn, idStr, married, divorced, husbID, wifeID):

	try:
		conn.cursor().execute(
			'INSERT INTO families VALUES (?, ?, ?, ?, ?)',
			(idStr, married, divorced, husbID, wifeID)
		)

	except sqlite3.IntegrityError as err:
		print("Couldn't add family " + str(idStr) + ": " + str(err))
		return False

	conn.commit()



# Add a child t a family (family must already exist)
# Prints error and returns false if invalid
def addChild (conn, childID, famID):

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
