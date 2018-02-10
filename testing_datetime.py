#datetime testing for sprint 1
#set up a function to calculate age given birthday and death day1

import datetime
import math
from datetime import timedelta

#dictionary of months with numeric values as the keys
monthnums = {'JAN':1,'FEB':2,'MAR':3,'APR':4,
             'MAY':5,'JUN':6,'JUL':7,'AUG':8,
             'SEP':9,'OCT':10,'NOV':11,'DEC':12}

birth = '02 DEC 1934'
death = '15 AUG 1992'


def age(death,birth):
    #converts date1 to the GEDCOM date format into python timedate format
    d1 = death.split()
    day1 = int(d1[0])
    month1 = int(monthnums[d1[1]])
    year1 = int(d1[2])

    #converts date2 to the GEDCOM date format into python timedate format
    d2 = birth.split()
    day2 = int(d2[0])
    month2 = int(monthnums[d2[1]])
    year2 = int(d2[2])

    #calcualtes the age difference in days
    daydelta = datetime.date(year1, month1, day1) - datetime.date(year2, month2, day2)
    #defining a year
    year = timedelta(days = 365)
    #calcualtes age
    age = math.floor(daydelta/year)

    #checking input dates for extreme age and birth before death
    if age < 0:
        print('ERROR: death before birth.')
    elif age >= 150:
        print('ANOMALY EXTREME AGE: {} years old.'.format(age))
    else:
        print(age)


age(death,birth)
