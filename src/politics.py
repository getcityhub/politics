from consts import *
from credentials import get_credential
from politicians import get_politicians

import boto3
import mysql.connector
import sys

s3 = boto3.client(
    "s3",
    aws_access_key_id = get_credential("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = get_credential("AWS_SECRET_ACCESS_KEY")
)

api_key = get_credential("GOOGLE_API_KEY")
conn = mysql.connector.connect(user='root', password='cityhub', host='localhost', database='cityhub')

for zipcode in NYC_ZIPCODES:
    get_politicians(api_key, conn, s3, zipcode)
    print "Retrieving politicians from %d" % zipcode

conn.close()
