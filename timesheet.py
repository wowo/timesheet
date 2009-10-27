#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re, calendar
from datetime import date, datetime, timedelta
from drivers import CSV, MySQL

class Timesheet:
  year   = 0
  month  = 0
  path   = ''
  params = {}
  driverName = 'mysql'
  driver = None
  monthInfo = {}

  def __init__(self, month = 0, year = 0):
    if month == 0:
      self.month = date.today().month
    if year == 0:
      self.year = date.today().year

    if self.driverName == 'mysql':
      self.driver = MySQL(self.month, self.year)
      self.params = {
        'host': 'p25a.progreso.pl', 
        'user': 'wowo86_timesheet', 
        'base': 'wowo86_timesheet', 
        'pass': 'timeszit12'
      }
      #self.params = {'host': 'localhost', 'user': 'timesheet', 'base': 'timesheet', 'pass': 'timeszit12', 'month': self.month, 'year': self.year}
    elif self.driverName == 'csv':
      self.autoDiscover()
      if not os.path.exists(self.path):
        raise Exception("Path %s not found" % self.path)

      self.driver = CSV(self.month, self.year)
      self.params = {'path' : self.path}
    else:
      raise Exception("No such driver %s" % self.driverName)

  def add(self, day, start, stop):
    self.driver.add(self.params, int(day), start,stop)

  def autoDiscover(self):
    paths = (
      "timesheet.%d.%d.csv" % (self.month, self.year),
      "sheets/timesheet.%d.%d.csv" % (self.month, self.year),
    )
      
    for proposal in paths:
      if (os.path.exists(proposal)):
        self.path = proposal
        print "Automatyczne wykreywanie: znaleziona ścieżka: %s" % proposal
        return True
    return False

  def calculate(self):
    result = {'days': {}, 'weeks' :{}}

    data = self.driver.getData(self.params)
    for row in data:
      start = datetime.strptime('.'.join([str(row['day']), str(self.month), str(self.year)]) + ' ' + row['start'], '%d.%m.%Y %H:%M:%S')
      stop  = datetime.strptime('.'.join([str(row['day']), str(self.month), str(self.year)]) + ' ' + row['stop' ], '%d.%m.%Y %H:%M:%S')
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

  def getMonthInfo(self):
    if self.monthInfo == {}:
      self.info = {'days': 0, 'weeks': {}, 'workingHours': 0}
      cal = calendar.Calendar()
      for day in cal.itermonthdays2(self.year, self.month):
        if day[0] > 0 and day[1] in range(0,5):
          self.info['days'] += 1
          week = int(datetime.strptime('.'.join([str(day[0]), str(self.month), str(self.year)]), '%d.%m.%Y').strftime('%W')) + 1
          if week in self.info['weeks']:
            self.info['weeks'][week] += 8.0
          else: 
            self.info['weeks'][week] = 8.0

      self.info['workingHours'] = self.info['days'] * 8.00
    return self.info

  def show(self):
    result = self.calculate()
    self.showDays(result)
    self.showWeeks(result)
    self.showSummary(result)

  def showDays(self, result):
    print "\n* dni:"
    for k,v in result['days'].iteritems():
      print "%2d - %5.2f - delta: %+.2f" % (k, v, v - 8.0)

  def showWeeks(self, result):
    keys = result['weeks'].keys()
    keys.sort()

    print "\n* tygodnie:"
    for k in keys:
      #check how much working hours has this week
      hours = 0
      for day in range(1, 6):
        today = datetime.strptime('%d %d %s' % (day, k,  self.year), '%w %W %Y')
        if today > datetime.today():
          break
        if today.month == self.month:
          hours += 8.0
      print "%02d - %5.2f - delta: %+6.2f" % (k, result['weeks'][k], result['weeks'][k] - hours)

  def showSummary(self, result):
    info    = self.getMonthInfo()
    hours   = sum(result['days'].values())
    missing = 8.0 * len(result['days'].keys()) - hours
    print """
* podsumowanie:
Godzin roboczych:      %6.2f
Godziny przepracowane: %6.2f  
Miesięczny %% godzin:   %5.f%%
Współczynnik:          %5.f%%
Średnia na dzień:      %6.2f  
Brakujące godziny:     %6.2f """ % (
                                    info['workingHours'],
                                    hours,
                                    (hours / info['workingHours']) * 100,
                                    (hours / (hours + missing)) * 100,
                                    float(hours) / len(result['days'].values()),
                                    missing,
                                   )

#Program call
try: 
  timesheet = Timesheet()
  #Dodawanie nowych wierszy
  if '-i' in sys.argv: 
    print "Podaj dzien [%d] " % date.today().day
    day = sys.stdin.readline().strip()
    if not len(day):
      day = date.today().day

    start = ''
    stop  = ''
    while not re.match('\d{1,2}:\d{2}', start):
      print "Podaj godzinę początkową w formacie 00:00"
      start = sys.stdin.readline().strip()

    while not re.match('\d{1,2}:\d{2}', stop):
      print "Podaj godzinę końcową w formacie 00:00"
      stop = sys.stdin.readline().strip()

    print """
Dodaje wpis:
  Dzień: %s
  Godzina początkowa: %s
  Godzina końcowa: %s
""" % (day, start, stop)
    timesheet.add(day, start, stop)

  #Wyswietlanie timesheeta
  timesheet.show()
except Exception as e:
  print "Wystąpił błąd, wiadomość: %s" % e
  raise
