#!/usr/bin/env python
# -*- coding: utf-8 -*-


from libs.tinydb import TinyDB, Query
import re

db = TinyDB('./db/easysat.json', sort_keys=True, indent=4)
dryrun = True


def initDb():
    db = TinyDB('./db/easysat.json', sort_keys=True, indent=4)


def cleanArrElements(element):
    element = element.strip('[]"')
    return element


def stripHtml(htmlString):
    return re.sub('<[^<]+?>', '', htmlString)


def importSats():
    with open("./db/importFiles/satellites.txt", "r") as f:
        for line in f:
            if line[0] != '/':
                elements = line.split(',')
                #print (elements)
                catalogId = cleanArrElements(elements[0])
                satName = cleanArrElements(elements[1])
                f1 = cleanArrElements(elements[2])
                f2 = cleanArrElements(elements[3])
                f3 = cleanArrElements(elements[4])
                m1 = cleanArrElements(elements[5])
                m2 = cleanArrElements(elements[6])
                m3 = cleanArrElements(elements[7])
                dir = cleanArrElements(elements[8])
                s1 = cleanArrElements(elements[9])
                s2 = cleanArrElements(elements[10])
                desc1 = cleanArrElements(elements[11])
                desc2 = cleanArrElements(elements[12])
                print("C:{} N:{} F:{} F:{} F:{} M:{} M:{} M:{} D:{} S:{} S:{} D:{} D:{}".format(
                    catalogId,
                    satName,
                    f1,
                    f2,
                    f3,
                    m1,
                    m2,
                    m3,
                    dir,
                    s1,
                    s2,
                    stripHtml(desc1),
                    stripHtml(desc2)
                ))

                if not dryrun:
                    table = db.table('satellites')
                    satellites = Query()
                    table.insert({
                        'catlogId': catalogId,
                        'satName': satName,
                        'satAlias': satName,
                        'f1': f1,
                        'f2': f2,
                        'f3': f3,
                        'm1': m1,
                        'm2': m2,
                        'm3': m3,
                        'dir': dir,
                        'u0': 0,
                        'u1': 0,
                        'd0': 0,
                        'd1': 0,
                        'tone': 0,
                        'satMode': 'B',
                        'desc1': stripHtml(desc1),
                        'desc2': stripHtml(desc2)
                    })


def convFreq():
    print(oper)
    satTable = db.table('satellites')
    satellites = satTable.all()
    sateQuery = Query()
    for satellite in satellites:
        
        f1 = satellite['f1']
        if len(f1) > 0:
            f1Num = float(f1)
        else:
            f1Num = 0

        f2 = satellite['f2']
        if len(f2) > 0:
            f2Num = float(f2)
        else:
            f2Num = 0

        f3 = satellite['f3']
        if len(f3) > 0:
            f3Num = float(f3)
        else:
            f3Num = 0

        print(satellite.doc_id,f1Num, f2Num, f3Num)

        satTable.update(
            {
                'f1': f1Num,
                'f2': f2Num,
                'f3': f3Num
            },
            doc_ids=[satellite.doc_id]            
        )


if __name__ == "__main__":
    initDb()

    """
    IMPORTANT
    Set dryrun to True to write on the database
    Set oper to one action a time

    """

    dryrun = True

    #oper = "IMPORTSATS"
    oper = "CONVFREQ"

    if oper == "IMPORTSATS":
        importSats()

    if oper == "CONVFREQ":
        convFreq()
