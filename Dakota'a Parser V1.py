import sys

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

# if a file name was passed in
if len(sys.argv) > 1:

	indID = ""
	name = ""
	gender = ""
	birth = ""
	death = "None"

	lastTag = None

	# loop through lines
	for line in open(sys.argv[1]):

		valid = False
		level = -1
		tag = None
		args = None

		# make sure this line has at least a level and a tag
		words = line.split()
		if len(words)>=2:

			# level is always first
			level = int(words[0])

			# flag for INDI and FAM
			badOrder = False

			# order is switched for INDI and FAM
			if (len(words)>=3 and
				(words[2]=='INDI' or words[2]=='FAM')):

				tag = words[2]
				args = " ".join([words[1]] + words[3:])
			else:
				tag = words[1]
				args = " ".join(words[2:])

				# INDI and FAM should have been found in block above
				# if this trips, the order is wrong
				if tag=='INDI' or tag=='FAM':
					badOrder = True

			# guilty until proven innocent
			valid = False

			# if we find a matching tag rule, and the level checks out
			# tag is valid
			if not badOrder:
				for tagRule in tagRules:
					if tagRule[1]==tag and tagRule[0]==level:
						valid = True

			if (tag == 'NAME'):
				name = args
			elif (tag == "SEX"):
				gender = args[0]
			elif (lastTag=="BIRT" and tag == "DATE"):
				birth = args
			elif (lastTag=="DEAT" and tag == "DATE"):
				birth = args

			lastTag = tag

		if (valid and level==0):
			print("" + name + ", " + gender + ", " + birth + ", " + death)
