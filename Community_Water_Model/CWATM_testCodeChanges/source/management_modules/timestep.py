# -------------------------------------------------------------------------
# Name:        Handling of timesteps and dates
# Purpose:
#
# Author:      P. Burek
#
# Created:     09/08/2016
# Copyright:   (c) burekpe 2016
# -------------------------------------------------------------------------


import os
import calendar
import datetime
import time as xtime
import numpy as np
from management_modules.data_handling import *
from management_modules.globals import *
from management_modules.messages import *

import difflib  # to check the closest word in settingsfile, if an error occurs

def date2str(date):
    return "%02d/%02d/%02d" % (date.day, date.month, date.year)


def ctbinding(inBinding):
    test = inBinding in binding
    if test:
        return binding[inBinding]
    else:
        closest = difflib.get_close_matches(inBinding, binding.keys())
        if not closest: closest = ["- no match -"]
        msg = "===== Timing in the section: [TIME-RELATED_CONSTANTS] is wrong! =====\n"
        msg += "No key with the name: \"" + inBinding + "\" in the settings file: \"" + sys.argv[1] + "\"\n"
        msg += "Closest key to the required one is: \""+ closest[0] + "\""
        raise CWATMError(msg)



def timemeasure(name,loops=0, update = False, sample = 1):
    """
    Measuring of the time for each subroutine

    :param name: name of the subroutine
    :param loops: if it it called several times this is added to the name
    :param update:
    :param sample:
    :return: add a string to the time measure string: timeMesString
    """
    timeMes.append(xtime.clock())
    if loops == 0:
        s = name
    else:
        s = name+"_%i" %(loops)
    timeMesString.append(s)
    return

# -----------------------------------------------------------------------
# Calendar routines
# -----------------------------------------------------------------------

def Calendar(input):
    """
    Get the date from CalendarDayStart in the settings xml
    Reformatting the date till it fits to datetime

    :param input: string from the settingsfile should be somehow a date
    :return: a datetime date
    """

    try:
        date = float(input)
    except ValueError:
        d = input.replace('.', '/')
        d = d.replace('-', '/')
        year = d.split('/')[-1:]
        if len(year[0]) == 4:
            formatstr = "%d/%m/%Y"
        else:
            formatstr = "%d/%m/%y"
        if len(year[0]) == 1:
            d = d.replace('/', '.', 1)
            d = d.replace('/', '/0')
            d = d.replace('.', '/')
            print d

        try:
            date = datetime.datetime.strptime(d, formatstr)
        except:
            msg = "Either date in StepStart is not a date or in SpinUp or StepEnd it is neither a number or a date!"
            raise CWATMError(msg)



    return date


def datetoInt(dateIn,begin,both=False):
    """
    Calculates the integer of a date from a reference date

    :param dateIn: date
    :param begin: reference date
    :param both: if set to True both the int and the string of the date are returned
    :return: interger value of a date, satarting from begin date
    """

    date1 = Calendar(dateIn)

    if type(date1) is datetime.datetime:
         #str1 = date1.strftime("%d/%m/%Y")
         # to cope with dates before 1990
         str1 = date2str(date1)

         int1 = (date1 - begin).days + 1
    else:
        int1 = int(date1)
        str1 = str(date1)
    if both: return int1,str1
    else: return int1




def checkifDate(start,end,spinup):
    """
    Checks if start date is earlier than end date etc
    And set some date variables

    :param start: start date
    :param end: end date
    :param spinup: date till no output is generated = warming up time
    :return: a list of date variable in: dateVar
    """

    #begin = Calendar(ctbinding('CalendarDayStart'))
    startdate = Calendar(ctbinding('StepStart'))
    if type(startdate) is datetime.datetime:
        begin = startdate
    else:
        msg = "\"StepStart = " + ctbinding('StepStart') + "\"\n"
        msg += "StepStart has to be a valid date!"
        raise CWATMError(msg)



    # spinup date = date from which maps are written
    if ctbinding(spinup).lower() == "none" or ctbinding(spinup) == "0":  spinup = start

    dateVar['intStart'],strStart = datetoInt(ctbinding(start),begin,True)
    dateVar['intEnd'],strEnd = datetoInt(ctbinding(end),begin,True)
    dateVar['intSpin'], strSpin = datetoInt(ctbinding(spinup), begin, True)


    # test if start and end > begin
    if (dateVar['intStart']<0) or (dateVar['intEnd']<0) or ((dateVar['intEnd']-dateVar['intStart'])<0):
        #strBegin = begin.strftime("%d/%m/%Y")
        strBegin = date2str(begin)
        msg="Start Date: "+strStart+" and/or end date: "+ strEnd + " are wrong!\n or smaller than the first time step date: "+strBegin
        raise CWATMError(msg)

    if (dateVar['intSpin'] < dateVar['intStart']) or (dateVar['intSpin'] > dateVar['intEnd']):
        #strBegin = begin.strftime("%d/%m/%Y")
        strBegin = date2str(begin)
        msg="Spin Date: "+strSpin + " is wrong!\n or smaller/bigger than the first/last time step date: "+strBegin+ " - "+ strEnd
        raise CWATMError(msg)

    dateVar['currDate'] = begin
    dateVar['dateBegin'] = begin
    dateVar['dateStart'] = begin + datetime.timedelta(days=dateVar['intSpin']-1)
    #dateVar['diffdays'] = dateVar['intEnd'] - dateVar['intStart'] + 1
    #dateVar['dateEnd'] = begin + datetime.timedelta(days=dateVar['diffdays']-1)
    dateVar['diffdays'] = dateVar['intEnd'] - dateVar['intSpin'] + 1
    dateVar['dateEnd'] = dateVar['dateStart'] + datetime.timedelta(days=dateVar['diffdays']-1)

    dateVar['curr'] = 0
    dateVar['currwrite'] = 0

    dateVar['datelastmonth'] = datetime.datetime(year=dateVar['dateEnd'].year, month= dateVar['dateEnd'].month, day=1) - datetime.timedelta(days=1)
    dateVar['datelastyear'] = datetime.datetime(year=dateVar['dateEnd'].year, month= 1, day=1) - datetime.timedelta(days=1)

    dateVar['checked'] = []
    dates = np.arange(dateVar['dateStart'], dateVar['dateEnd']+ datetime.timedelta(days=1), datetime.timedelta(days = 1)).astype(datetime.datetime)
    for d in dates:
        if d.day == calendar.monthrange(d.year, d.month)[1]:
            if d.month == 12:
                dateVar['checked'].append(2)
            else:
                dateVar['checked'].append(1)
        else:
            dateVar['checked'].append(0)

    dateVar['diffMonth'] = dateVar['checked'].count(1) + dateVar['checked'].count(2)
    dateVar['diffYear'] = dateVar['checked'].count(2)
    dateVar['leapYear'] = 0




def timestep_dynamic():
    """
    Dynamic part of setting the date
    Current date is increasing, checking if beginning of month, year

    :return: a list of date variable in: dateVar
    """



    #print "leap:", globals.leap_flag[0]
    dateVar['currDate'] = dateVar['dateBegin'] + datetime.timedelta(days=dateVar['curr'])


    if dateVar['leapYear']>0:   # 365 days per year
        if dateVar['currDate'].month==2 and dateVar['currDate'].day==29:
             dateVar['curr'] += 1
             dateVar['currDate'] = dateVar['dateBegin'] + datetime.timedelta(days=dateVar['curr'])
    if dateVar['leapYear']==2:   # 360 days per year
        if  dateVar['currDate'].month < 9 and dateVar['currDate'].day==31:
             dateVar['curr'] += 1
             dateVar['currDate'] = dateVar['dateBegin'] + datetime.timedelta(days=dateVar['curr'])


    #dateVar['currDatestr'] = dateVar['currDate'].strftime("%d/%m/%Y")
    dateVar['currDatestr'] = date2str(dateVar['currDate'])

    #dateVar['doy'] = int(dateVar['currDate'].strftime('%j'))
    # replacing this because date less than 1900 is not used
    firstdoy = datetime.datetime(dateVar['currDate'].year,1,1)
    dateVar['doy'] = (dateVar['currDate'] - firstdoy).days + 1

    dateVar['10day'] = int((dateVar['doy']-1)/10)

    dateVar['laststep'] = False
    if (dateVar['intStart'] + dateVar['curr']) == dateVar['intEnd']: dateVar['laststep'] = True

    dateVar['currStart'] = dateVar['curr'] + 1

    dateVar['curr'] += 1
    # count currwrite only after spin time
    if dateVar['curr'] >= dateVar['intSpin']:
        dateVar['currwrite'] += 1

    dateVar['currMonth'] = dateVar['checked'][:dateVar['currwrite']].count(1) + dateVar['checked'][:dateVar['currwrite']].count(2)
    dateVar['currYear'] = dateVar['checked'][:dateVar['currwrite']].count(2)

    # first timestep
    dateVar['newStart'] = dateVar['curr'] == 1
    dateVar['newMonth'] = dateVar['currDate'].day == 1
    dateVar['newYear'] = (dateVar['currDate'].day == 1) and (dateVar['currDate'].month == 1)
    dateVar['new10day'] = ((dateVar['doy'] - 1) / 10.0) == dateVar['10day']

    #dateVar['daysInMonth'] = float(calendar.monthrange(int(dateVar['currDate'].strftime('%Y')),int(dateVar['currDate'].strftime('%m')))[1])
    dateVar['daysInMonth'] = float(calendar.monthrange(dateVar['currDate'].year,dateVar['currDate'].month)[1])

    dateVar['daysInYear'] = 365.0
    if calendar.isleap(dateVar['currDate'].year): dateVar['daysInYear'] = 366.0
    if dateVar['leapYear'] > 0:
        dateVar['daysInYear'] = 365.0
    if dateVar['leapYear'] == 2:
        dateVar['daysInYear'] = 365.0
        dateVar['daysInMonth'] = 30.0











