

class Trasponder:

    _satName = None
    _tDown = None
    _tUp = None
    _mUp = None
    _mDown = None
    _tDirection = None
    _tType = None

    def __init__(self, sqf):
        if not sqf:
            print ("sqf not parsed")
        self.parseSqf(sqf)


    def upTodown(self, upF):
        self.check()
            
        if self.inverting:
            downF = int(self.k() - upF)
        else:
            downF = int(self.k() + upF)
        return downF

    def downToUp(self, downF):
        if self.inverting:
            upF = int(self.k() - downF)
        else:
            upF = int(self.k() + downF)
        return upF


    def parseSqf(self, sqf):
        sqfArr = sqf.split(',')
        self._satName = sqfArr[0]
        self.centerFDown = float(sqfArr[1])
        self.centerFUp = float(sqfArr[2])
        self._mUp = sqfArr[3]
        self._mDown = sqfArr[4]
        self._tDirection = sqfArr[5]
        self._tType = sqfArr[8]
        if self._tDirection == "REV":
            self.inverting = True
        else:
            self.inverting = False

    def k(self):
        if self.inverting:
            k = self.centerFDown+self.centerFUp
        else:
            k = self.centerFDown-self.centerFUp
        return k


    def check(self):
        if self.satName == None or self._tDown == None or self.tUp == None or self._mUp == None or self._mDown == None or self._tDirection == None or self._tType == None:
            raise Exception('Sqf file not parsed or missing value')
            return False
        else:
            return True



""" TEST CODE
"""
"""
t = Trasponder('FO-29,435850,145952.95,USB,LSB,REV,0,0,Transponder')

minUp = 145900
maxUp = 146000
minDown = 435800
maxDown = 435900

step = 5

print("-------------------")
print("UP\tDOWN")
print("-------------------")
for freq in range(minUp, maxUp+step, step):
    print("{0}\t{1}".format(freq, t.upTodown(freq)))
print("-------------------")
print("DOWN\tUP")
print("-------------------")
for freq in range(minDown, maxDown+step, step):
    print("{0}\t{1}".format(freq, t.downToUp(freq)))
"""