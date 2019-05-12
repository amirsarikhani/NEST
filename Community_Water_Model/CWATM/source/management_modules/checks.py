# -------------------------------------------------------------------------
# Name:        checks if inputs are valid
# Purpose:
#
# Author:      burekpe
#
# Created:     16/05/2016
# Copyright:   (c) burekpe 2016
# -------------------------------------------------------------------------


import xml.dom.minidom
import datetime
import time as xtime
import os


from globals import *



def counted(fn):
    """
    count number of times a subroutine is called

    :param fn:
    :return:
    """
    def wrapper(*args, **kwargs):
        wrapper.called+= 1
        return fn(*args, **kwargs)
    wrapper.called= 0
    wrapper.__name__= fn.__name__
    return wrapper

@counted
def checkmap(name, value, map, flagmap, find):
    """
    check maps if the fit to the mask map
    :param name:
    :param value:
    :param map:
    :param flagmap:
    :param find:
    :return:

    Todo:
        still to improve, this is work in progress!
    """

    s = [name, value]
    if flagmap:
        iii = 1
        """
        amap = scalar(defined(MMaskMap))
        try:
            smap = scalar(defined(map))
        except:
            msg = "Map: " + name + " in " + value + " does not fit"
            if name == "LZAvInflowMap":
                msg +="\nMaybe run initial run first"
            raise LisfloodError(msg)

        mvmap = maptotal(smap)
        mv = cellvalue(mvmap, 1, 1)[0]
        s.append(mv)

        less = maptotal(ifthenelse(defined(MMaskMap), amap - smap, scalar(0)))
        s.append(cellvalue(less, 1, 1)[0])
        less = mapminimum(scalar(map))
        s.append(cellvalue(less, 1, 1)[0])
        less = maptotal(scalar(map))
        if mv > 0:
            s.append(cellvalue(less, 1, 1)[0] / mv)
        else:
            s.append('0')
        less = mapmaximum(scalar(map))
        s.append(cellvalue(less, 1, 1)[0])
        if find > 0:
            if find == 2:
                s.append('last_Map_used')
            else:
                s.append('')
        """

    else:
        s.append(0)
        s.append(0)
        s.append(float(map))
        s.append(float(map))
        s.append(float(map))

    if checkmap.called == 1:
        print "%-25s%-40s%11s%11s%11s%11s%11s" %("Name","File/Value","nonMV","MV","min","mean","max")
    print "%-25s%-40s%11i%11i%11.2f%11.2f%11.2f" %(s[0],s[1][-39:],s[2],s[3],s[4],s[5],s[6])
    return



