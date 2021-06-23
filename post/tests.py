from django.test import TestCase
import pymysql

AWS_HOST = 'silah.cogvaeokj5vm.us-east-2.rds.amazonaws.com'
AWS_PORT = 3306
AWS_DB = 'silah'
AWS_USER = 'silah'
AWS_PASSWORD = '!SilahReport123$'

conn = pymysql.connect(host=AWS_HOST, port=AWS_PORT, user=AWS_USER, passwd=AWS_PASSWORD, db=AWS_DB)

cur = conn.cursor()

cur.execute("SELECT * FROM media LIMIT 0, 5")

print(cur.description)
print()

for row in cur:
    print(row)

cur.close()
conn.close()