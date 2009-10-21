import csv, os, MySQLdb, urllib

class Driver:
  year   = 0
  month  = 0

  def __init__(self, month = 0, year = 0):
    self.month = month
    self.year  = year

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
  def getData(self, params, attempt=1):
    result = []
    try:
      conn = MySQLdb.connect(params['host'], params['user'], params['pass'], params['base'])
    except Exception as (errno, strerror):
      if errno == 1045 and 'progreso.pl' in params['host']:
        if attempt > 2:
          raise Exception('To many attempts (%d) to unlocking ports on progreso and reconnecting' % attempt)

        reader = urllib.urlopen('http://p25.progreso.pl/unlock-ports.pl')
        print 'Unlocking ports on progreso and try again, attempt: %d, response: %s' % (attempt, reader.read())
        self.getData(params, attempt + 1)
        return []

    c = conn.cursor()
    c.execute("SELECT day, start, stop FROM entries WHERE month = %d AND year = %d" % (self.month, self.year))
    for row in c.fetchall():
      result.append({
        'day'  : int(row[0]),
        'start': str(row[1]),
        'stop' : str(row[2]),
      })
    return result
