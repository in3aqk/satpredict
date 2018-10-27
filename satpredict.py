#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
from sat import Sat


if __name__ == "__main__":
    sat = Sat()
    
    parser = argparse.ArgumentParser(
        prog='Sat predict',
        description='Hamradio satellite orbit prediction and tracking software',
        epilog = 'By Paolo Mattiolo IN3AQK Bolzano Dolomiti (c)2018'
    )

    parser.add_argument("-u","--updtle", help="Update the tle file",action="store_true")
    parser.add_argument("-p","--predict", help="Predict a sat",action="store_true")
    parser.add_argument("-pa","--predictall", help="Predict all sat",action="store_true")
    parser.add_argument("-s","--satname", help="Satellite name")
    parser.add_argument("-wt","--writetxt", help="Write predict as txt",action="store_true")
    parser.add_argument("-d","--delete", help="Delete output folder content",action="store_true")
    parser.add_argument("-sd","--startdate", help="Start date in format DD/MM/YYYY",action="store_true")
    parser.add_argument("-ed","--enddate", help="End date in format DD/MM/YYYY",action="store_true")

    args = parser.parse_args()
    
    if not args:
        print ("usage: satpredict.py [-h]")

    if args.delete:
        sat.deleteOutput()

    if args.updtle:
        sat.updateTleDb()

    if args.predictall:
        if args.writetxt:
            sat.predictAll('txt')
        else:
            sat.predictAll('none')
    
    if args.predict:
        if (args.satname):
            sat.predictSat(args.satname)
        else:
            print ("-satname argument missing")

