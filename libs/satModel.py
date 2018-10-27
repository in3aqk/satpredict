#!/usr/bin/env python
# -*- coding: utf-8 -*-


from libs.tinydb import TinyDB, Query




class SatModel:
    _db = None

    def __init__(self):
        self._db = TinyDB('./db/easysat.json', sort_keys=True, indent=4)
        self._satTable = self._db.table('satellites')

    def getSats(self,preferred = False):

        with open("./config/preferred.txt", "r") as f:
            preferredArr = []
            for prefSat in f:
                preferredArr.append(prefSat.strip())



        satellites = self._satTable.all()
        satArr = []
        satList = []
        for satellite in satellites:
            append = False
            if not preferred:
                append = True
            else:
                if satellite['satName'] in preferredArr:
                    append = True


            if append:
                satName = "{} Mode {}".format(satellite['satName'],satellite['satMode'])
                satArr.append("{}-{} {}".format(satellite['catlogId'],satellite['satName'],satellite['desc1']))
                satList.append({"value":satellite.doc_id,"label":satName})


        return satArr,satList




    def getSatById(self,id):          
        
        result=self._satTable.get(doc_id=id)
        return result
