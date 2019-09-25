import math
class BezierLine:
    def __init__(self,startCoordinates,endCoordinates,PointNum):
        self.startCoordinates = startCoordinates
        self.endCoordinates = endCoordinates
        self.PointNum = PointNum

    def getBezierPoints(self):
        thirdPoint = BezierLine.getThirdPoint(self.startCoordinates,self.endCoordinates)
        line = self.startCoordinates
        line.extend(thirdPoint)
        line.extend(self.endCoordinates)
        t = self.PointNum
        bezierPoints = []
        #bezierPoints.append(self.startCoordinates)
        i = 0
        while i <= 1:
            bezierPoints.append(BezierLine.getBezierPoint(line,i))
            i = i + 1/t
        bezierPoints.append(self.endCoordinates)
        return bezierPoints
    @staticmethod
    def getBezierPoint(line,t):
        points = line
        AB = points[0:4]
        D = BezierLine.calculatePoint(AB,t)
        BC = points[2:]
        E = BezierLine.calculatePoint(BC,t)
        DE = D
        DE.extend(E)
        F = BezierLine.calculatePoint(DE,t)
        return F

    @staticmethod
    def getThirdPoint(startPoint,endPoint):
        x1 = startPoint[0]
        y1 = startPoint[1]
        x2 = endPoint[0]
        y2 = endPoint[1]
        n = 0.5
        m = 0.2
        xm = 0
        ym = 0

        xa = x1 + x2
        ya = y1 + y2
        xb = abs(x2 - x1)
        yb = abs(y2 - y1)

        k = n
        if x1 < x2:
            k = -1 * n


        a = yb/xb
        if a > 0:
            xm = xa/2 + k*yb/2
            ym = ya/2 - k*xb/2
        else :
            xm = xa/2 - k*yb/2
            ym = ya/2 - k*xb/2
        return [xm,ym]

    @staticmethod
    def calculatePoint(points,fraction):
        Lengths = [0]
        x1 = points[0]
        y1 = points[1]
        length = 0
        i = 2
        z = len(points)
        while i < z:
            x2 = points[i]
            y2 = points[i + 1]
            length = length + math.sqrt((x2 - x1)*(x2 - x1)+(y2 - y1)*(y2 - y1))
            Lengths.append(length)
            x1 = x2
            y1 = y2
            i = i + 2
        targetLength = fraction * length
        targetIndex = 0
        m = 1
        n = len(Lengths)
        while m < n:
            if targetLength < Lengths[m]:
                targetIndex = m
                break
            m = m + 1
		
        occupyLength = (targetLength - Lengths[targetIndex - 1])/(Lengths[targetIndex] - Lengths[targetIndex - 1])
        c = targetIndex *2
        def getTarget(a,b,occupyLength):
            return a + (b - a) * occupyLength
        pointX = getTarget(points[c - 2],points[c], occupyLength)
        pointY = getTarget(points[c - 1],points[c + 1],occupyLength)
        return [pointX,pointY]
