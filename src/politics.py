from consts import *
from politicians import get_politicians

import mysql.connector
import sys

if len(sys.argv) == 2:
    api_key = sys.argv[1]
    conn = mysql.connector.connect(user='root', password='cityhub', host='localhost', database='cityhub')

    for zipcode in NYC_ZIPCODES:
        get_politicians(api_key, conn, zipcode)
        print "Retrieving politicians from %d" % zipcode

    conn.close()
else:
    print "A key for the Google Civic Information API must be passed as an argument in order to retrieve politician data."
