import os
import sqlite3
import sys

dbName = "GEDCOM.db"

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
		
		FOREIGN KEY (husbID) REFERENCES individuals(id)
		FOREIGN KEY (wifeID) REFERENCES individuals(id)
	)''')
	
	curs.execute('''CREATE TABLE children (
		indID		TEXT	NOT NULL,
		famID		TEXT	NOT NULL,
		
		PRIMARY KEY (indID, famID),
		
		FOREIGN KEY (indID) REFERENCES individuals(id),
		FOREIGN KEY (famID) REFERENCES families(id)
	)''')
	
	conn.commit()
	
	return conn

def addIndividual (idStr, firstName, lastName, gender, birth, death):
	
	conn.cursor().execute(
		'INSERT INTO individuals VALUES (?, ?, ?, ?, ?, ?)',
		(idStr, firstName, lastName, gender, birth, death)
	)
	
	conn.commit()

def addFamily (idStr, married, divorced, husbID, wifeID):
	
	conn.cursor().execute(
		'INSERT INTO families VALUES (?, ?, ?, ?, ?)',
		(idStr, married, divorced, husbID, wifeID)
	)
	
	conn.commit()

def addChild (childID, famID):
	
	conn.cursor().execute(
		'INSERT INTO children VALUES (?, ?)',
		(childID, famID)
	)
	
	conn.commit()

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
	).fetchall()

conn = dbInit()

addIndividual("I1", "Bob", "Dyalan", "M", "5-24-1941", None)
addIndividual("I2", "Hillary", "Clinton", "F", "10-26-1947", None)
addIndividual("I3", "Miranda", "Cosgrove", "F", "5-14-1993", None)
addFamily("F1", "6-15-1972", None, "I1", "I2")
addChild("I3", "F1")

print(getFamily("F1"))

conn.close()
