#!/usr/bin/env python
import csv
from datetime import datetime, timedelta

class Timesheet:
  path = ''

  def __init__(self, path):
    self.path = path

  def show(self):
    csvReader = csv.reader(open(self.path), delimiter=';')
    days  = {}
    weeks = {}
    for row in csvReader:
      start = datetime.strptime(row[0] + ' ' + row[1], '%d.%m.%Y %H:%M')
      stop  = datetime.strptime(row[0] + ' ' + row[2], '%d.%m.%Y %H:%M')
      delta = stop - start
      #days
      if start.day in days:
        days[start.day] = days[start.day] + delta.seconds / 3600.0
      else:
        days[start.day] = delta.seconds / 3600.0

      #weeks
      week = int(start.strftime('%W'))
      if week in weeks:
        weeks[week] = weeks[week] + delta.seconds / 3600.0
      else: 
        weeks[week] = delta.seconds / 3600.0

    print "\n* days:"
    for k,v in days.iteritems():
      print "%02d - %.2f - delta: %.2f" % (k, v, v - 8.0)

    keys = weeks.keys()
    keys.sort()

    print "\n* weeks:"
    for k in keys:
      print "%02d - %.2f - delta: %.2f" % (k, weeks[k], weeks[k] - 40.0)

    print """
    -----------------------
    Working hours:   %.2f  
    Average per day: %.2f  
    Missing hours:   %.2f""" % (sum(days.values()), (float(sum(days.values())) / len(days.values())) , (8.0 * len(days.keys()) - sum(days.values())))

timesheet = Timesheet('/home/wsznapka/Dokumenty/timesheet.csv')
timesheet.show()
