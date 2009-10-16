#!/usr/bin/env python
import csv, os
from datetime import date, datetime, timedelta

class Timesheet:
  path = ''
  year = 0
  month = 0

  def __init__(self, path = '', month = 0, year = 0):
    if month == 0:
      self.month = date.today().month
    if year == 0:
      self.year = date.today().year
    if not len(path):
      self.autoDiscover()

    if not os.path.exists(self.path):
      raise Exception("Path %s not found" % self.path)
  
  def autoDiscover(self):
    paths = (
      "timesheet.%d.%d.csv" % (self.month, self.year),
      "sheets/timesheet.%d.%d.csv" % (self.month, self.year),
    )
      
    for proposal in paths:
      if (os.path.exists(proposal)):
        self.path = proposal
        print "Autodiscover: found path: %s" % proposal
        return True
    return False

  def calculate(self):
    csvReader = csv.reader(open(self.path), delimiter=';')
    result = {'days': {}, 'weeks' :{}}
    #days  = {}
    #weeks = {}
    for row in csvReader:
      start = datetime.strptime('.'.join([row[0], str(self.month), str(self.year)]) + ' ' + row[1], '%d.%m.%Y %H:%M')
      stop  = datetime.strptime('.'.join([row[0], str(self.month), str(self.year)]) + ' ' + row[2], '%d.%m.%Y %H:%M')
      delta = stop - start

      #days
      if start.day in result['days']:
        result['days'][start.day] += delta.seconds / 3600.0
      else:
        result['days'][start.day] = delta.seconds / 3600.0

      #days
      week = int(start.strftime('%W'))
      if week in result['weeks']:
        result['weeks'][week] += delta.seconds / 3600.0
      else: 
        result['weeks'][week] = delta.seconds / 3600.0

    return result

  def show(self):
    result = self.calculate()
    self.showDays(result)
    self.showWeeks(result)
    self.showSummary(result)

  def showDays(self, result):
    print "\n* days:"
    for k,v in result['days'].iteritems():
      print "%02d - %.2f - delta: %.2f" % (k, v, v - 8.0)

  def showWeeks(self, result):
    keys = result['weeks'].keys()
    keys.sort()

    print "\n* weeks:"
    for k in keys:
      print "%02d - %.2f - delta: %.2f" % (k, result['weeks'][k], result['weeks'][k] - 40.0)

  def showSummary(self, result):
    print """
    -----------------------
    Working hours:   %.2f  
    Average per day: %.2f  
    Missing hours:   %.2f""" % (sum(result['days'].values()), (float(sum(result['days'].values())) / len(result['days'].values())) , (8.0 * len(result['days'].keys()) - sum(result['days'].values())))


#Program call
try: 
  timesheet = Timesheet()
  timesheet.show()
except Exception as e:
  print "An error occured, message: %s" % e
