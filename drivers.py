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
  conn = None

  def getConnection(self, params):
    try:
      conn = MySQLdb.connect(params['host'], params['user'], params['pass'], params['base'])
      return conn
    except Exception as (errno, strerror):
      if errno == 1045 and 'progreso.pl' in params['host']:
        if attempt > 2:
          raise Exception('To many attempts (%d) to unlocking ports on progreso and reconnecting' % attempt)

        reader = urllib.urlopen('http://p25.progreso.pl/unlock-ports.pl')
        print 'Unlocking ports on progreso and try again, attempt: %d, response: %s' % (attempt, reader.read())
        self.getData(params, attempt + 1)
        return None

  def getData(self, params, attempt=1):
    result = []
    conn = self.getConnection(params)

    cursor = conn.cursor()
    cursor.execute("SELECT day, start, stop FROM entries WHERE month = %d AND year = %d" % (self.month, self.year))
    for row in cursor.fetchall():
      result.append({
        'day'  : int(row[0]),
        'start': str(row[1]),
        'stop' : str(row[2]),
      })
    return result

  def add(self, params, day, start, stop):
    conn = self.getConnection(params)
    conn.cursor().execute("INSERT INTO entries(day, month, year, start, stop) VALUES(%d, %d, %d, '%s:00', '%s:00')" % (day, self.month, self.year, start, stop))
    conn.commit()
    
