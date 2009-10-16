import csv, os

class Driver:
  def getData(self):
    "gets data from source"

class CSV(Driver):
  def getData(self, params):
    result = []
    for row in csv.reader(open(params['path']), delimiter=';'):
      result.append({
        'day'  : row[0],
        'start': row[1],
        'stop' : row[2],
      })
    return result
