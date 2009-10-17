import csv, os, MySQLdb

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

class MySQL(Driver):
  def getData(self, params):
    result = []
    conn = MySQLdb.connect(params['host'], params['user'], params['pass'], params['base'])
    c = conn.cursor()
    c.execute("SELECT day, start, stop FROM entries WHERE month = %d AND year = %d" % (params["month"], params["year"]))
    for row in c.fetchall():
      result.append({
        'day'  : int(row[0]),
        'start': str(row[1]),
        'stop' : str(row[2]),
      })
    return result
