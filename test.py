import os
import datetime

def file_date(filename):
    unixTime = os.path.getctime(filename)
    regularTime = datetime.datetime.fromtimestamp(unixTime)

    

    return regularTime.year, type(regularTime)

print(file_date("app.py"))

