'''
Created on Dec 14, 2015

@author: MarcoXZh
'''

import random
from __builtin__ import True


class Rectangle(object):
    '''
    The rectangle class
    '''

    def __init__(self, left, top, width, height):
        assert type(left) is int and type(top) is int and type(width) is int and type(height) is int
        self.left = left
        self.top = top
        self.height = height
        self.width = width
    pass # def __init__(self, left, top, width, height)

    def getLeft(self):          return self.left
    def getTop(self):           return self.top
    def getRight(self):         return self.left + self.width
    def getBottom(self):        return self.top + self.height
    def getWidth(self):         return self.width
    def getHeight(self):        return self.height
    def getCentroid(self):      return (self.left + 0.5 * self.width, self.top + 0.5 * self.height)

    def __str__(self):
        return 'Rectangle[left=%d, top=%d, width=%d, height=%d]' % (self.left, self.top, self.width, self.height)
    pass # def __str__(self)

    @staticmethod
    def overlaps(rect1, rect2):
        assert type(rect1) is Rectangle and type(rect2) is Rectangle
        cx1, cy1 = rect1.getCentroid()
        cx2, cy2 = rect2.getCentroid()
        width1, height1 = rect1.getWidth(), rect1.getHeight()
        width2, height2 = rect2.getWidth(), rect2.getHeight()
        if abs(cx1 - cx2) < 0.5 * (width1 + width2) and \
           abs(cy1 - cy2) < 0.5 * (height1 + height2):
            return True
        return False
    pass # def overlaps(rect1, rect2)

pass # class Rectangle(object)

def calcGapDist(rect1, rect2):
    assert type(rect1) is Rectangle and type(rect2) is Rectangle

    l1, t1, r1, b1 = rect1.getLeft(), rect1.getTop(), rect1.getRight(), rect1.getBottom()
    l2, t2, r2, b2 = rect2.getLeft(), rect2.getTop(), rect2.getRight(), rect2.getBottom()
    cx1, cy1 = rect1.getCentroid()
    cx2, cy2 = rect2.getCentroid()
    hGapDist = min([abs(l1 - l2), abs(l1 - r2), abs(r1 - l2), abs(r1 - r2)])
    vGapDist = min([abs(t1 - t2), abs(t1 - b2), abs(b1 - t2), abs(b1 - b2)])

    sgn = -1.0 if Rectangle.overlaps(rect1, rect2) else 1.0
    return (sgn * hGapDist) if abs(cx1 - cx2) > abs(cy1 - cy2) else (sgn * vGapDist)
pass # def calcGapDist(rect1, rect2)

def calcRelativeGapDist(rect1, rect2):
    assert type(rect1) is Rectangle and type(rect2) is Rectangle

    l1, t1, r1, b1 = rect1.getLeft(), rect1.getTop(), rect1.getRight(), rect1.getBottom()
    l2, t2, r2, b2 = rect2.getLeft(), rect2.getTop(), rect2.getRight(), rect2.getBottom()
    cx1, cy1 = rect1.getCentroid()
    cx2, cy2 = rect2.getCentroid()
    hGapDist = min([abs(l1 - l2), abs(l1 - r2), abs(r1 - l2), abs(r1 - r2)])
    vGapDist = min([abs(t1 - t2), abs(t1 - b2), abs(b1 - t2), abs(b1 - b2)])

    sgn = -1.0 if Rectangle.overlaps(rect1, rect2) else 1.0
    return (sgn * hGapDist / (0.5 * ((r1 - l1) + (r2 - l2)))) if abs(cx1 - cx2) > abs(cy1 - cy2) else \
           (sgn * vGapDist / (0.5 * ((b1 - t1) + (b2 - t2))))
pass # def calcRelativeGapDist(rect1, rect2)

def calcHausdorffDist(rect1, rect2):
    assert type(rect1) is Rectangle and type(rect2) is Rectangle

    def HausdorffDist(a, b):
        l1, t1, r1, b1 = a.getLeft(), a.getTop(), a.getRight(), a.getBottom()
        l2, t2, r2, b2 = b.getLeft(), b.getTop(), b.getRight(), b.getBottom()
        cx1, cy1 = a.getCentroid()
        cx2, cy2 = b.getCentroid()

        if l1 >= l2 and r1 <= r2 and t1 >= t2 and b1 <= b2:             # inside
            return 0.0
        deltaX = l2 - l1 if cx1 < cx2 else r2 - r1
        deltaY = t2 - t1 if cy1 < cy2 else b2 - b1
        if l1 >= l2 and r1 <= r2:                                       # north/south
            return 1.0 * abs(deltaY)
        if t1 >= t2 and b1 <= b2:                                       # west/east
            return 1.0 * abs(deltaX)
        return (deltaX ** 2.0 + deltaY ** 2.0) ** 0.5                   # corners
    pass # def hausdorffDist(rect1, rect2)

    return max(HausdorffDist(rect1, rect2), HausdorffDist(rect2, rect1))
pass # def calcHausdorffDist(rect1, rect2)

def calcRelativeHausdorffDist(rect1, rect2):
    assert type(rect1) is Rectangle and type(rect2) is Rectangle

    def relativeHausdorffDist(a, b):
        l1, t1, r1, b1 = a.getLeft(), a.getTop(), a.getRight(), a.getBottom()
        l2, t2, r2, b2 = b.getLeft(), b.getTop(), b.getRight(), b.getBottom()
        cx1, cy1 = a.getCentroid()
        cx2, cy2 = b.getCentroid()

        if l1 >= l2 and r1 <= r2 and t1 >= t2 and b1 <= b2:             # inside
            return 0.0
        deltaX = l2 - l1 if cx1 < cx2 else r2 - r1
        deltaY = t2 - t1 if cy1 < cy2 else b2 - b1
        if l1 >= l2 and r1 <= r2:                                       # north/south
            return 1.0 * abs(deltaY) / a.getHeight()
        if t1 >= t2 and b1 <= b2:                                       # west/east
            return 1.0 * abs(deltaX) / a.getWidth()
        diagonal = (a.getWidth() ** 2.0 + a.getHeight() ** 2.0) ** 0.5
        return (deltaX ** 2.0 + deltaY ** 2.0) ** 0.5 / diagonal        # corners
    pass # def relativeHausdorffDist(a, b)

    return max(relativeHausdorffDist(rect1, rect2), relativeHausdorffDist(rect2, rect1))
pass # def calcRelativeHausdorffDist(rect1, rect2)

def calcCentroidDist(rect1, rect2):
    assert type(rect1) is Rectangle and type(rect2) is Rectangle
    cx1, cy1 = rect1.getCentroid()
    cx2, cy2 = rect2.getCentroid()
    return ((cx1 - cx2) ** 2.0 + (cy1 - cy2) ** 2.0) ** 0.5
pass # def calcCentroidDist(rect1, rect2)

def calcRelativeCentroidDist(rect1, rect2):
    assert type(rect1) is Rectangle and type(rect2) is Rectangle
    cx1, cy1 = rect1.getCentroid()
    cx2, cy2 = rect2.getCentroid()

    relevantLength = (0.5 * (rect1.getWidth() + rect2.getWidth())) if abs(cx1 - cx2) > abs(cy1 - cy2) \
                else (0.5 * (rect1.getHeight() + rect2.getHeight()))
    return ((cx1 - cx2) ** 2.0 + (cy1 - cy2) ** 2.0) ** 0.5 / relevantLength
pass # def calcRelativeCentroidDist(rect1, rect2)

def showDefect_GD_RGD(groups, numPerGroup):
    '''
    Generate rectangle pairs that can reflect the defect of gap distance
    Fix both sizes and the fist position, and move the second horizontally/vertically near the first
    @param groups:      {Integer} number of test groups
    @param numPerGroup: {Integer} number of test case per group
    '''
    cases = []
    num = 0
    while num < groups:
        curCases = []
        width1, height1 = random.randint(200, 600), random.randint(100, 200)
        width2, height2 = random.randint(100, 300), random.randint(80, 100)
        x1, y1 = random.randint(200, 700), random.randint(20, 70)
        x2 = x1 - int(round(width2 * (1 + random.random())))
        y2 = y1 + height1 + random.randint(0, round(0.1 * height1))
        while len(curCases) < numPerGroup:
            curCases.append([x1, y1, width1, height1, x2, y2, width2, height2])
            x2 += random.randint(5, round((2.2 * width2 + width1) / numPerGroup))
        pass # while len(curCases) < numPerGroup
        num += 1
        cases += curCases
    pass # while num < groups

    f = open('TestCases/DistComp-GDRGD.txt', 'w')
    f.write('L1\tT1\tW1\tH1\tL2\tT2\tW2\tH2\tCD\tRCD\tGD\tRGD\tHD\tRHD\n')
    for x1, y1, width1, height1, x2, y2, width2, height2 in cases:
        rect1, rect2 = Rectangle(x1, y1, width1, height1), Rectangle(x2, y2, width2, height2)
        cd = calcCentroidDist(rect1, rect2)
        rcd = calcRelativeCentroidDist(rect1, rect2)
        gd = calcGapDist(rect1, rect2)
        rgd = calcRelativeGapDist(rect1, rect2)
        hd = calcHausdorffDist(rect1, rect2)
        rhd = calcRelativeHausdorffDist(rect1, rect2)
        f.write('%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\n' % \
                (x1, y1, width1, height1, x2, y2, width2, height2, cd, rcd, gd, rgd, hd, rhd ))
    pass # for x1, y1, width1, height1, x2, y2, width2, height2 in cases
pass # def showDefect_GD_RGD(groups, numPerGroup)

def showDefect_CD_RCD(groups, numPerGroup):
    '''
    Generate rectangle pairs that can reflect the defect of centroid distance
    Fix centroids, and change the sizes
    @param groups:      {Integer} number of test groups
    @param numPerGroup: {Integer} number of test case per group
    '''
    cases = []
    num = 0
    while num < groups:
        curCases = []
        width1, height1 = 2 * random.randint(10, 100), 2 * random.randint(10, 100)
        width2, height2 = 2 * random.randint(10, 20), 2 * random.randint(10, 20)
        cx1, cy1 = random.randint(100, 200), random.randint(100, 200)
        cx2, cy2 = random.randint(100, 200), random.randint(600, 700)
        while len(curCases) < numPerGroup:
            curCases.append([cx1 - int(width1/2), cy1 - int(height1/2), width1, height1, \
                             cx2 - int(width2/2), cy2 - int(height2/2), width2, height2])
            yGap = round(0.5 * (abs(cy1 - cy2) - 0.5 * (height1 + height2)))
            width1 += 2 * random.randint(0, 10)
            height1 += 2 * random.randint(0, round(yGap/numPerGroup))
            width2 += 2 * random.randint(0, 10)
            height2 += 2 * random.randint(0, round(yGap/numPerGroup))
        pass # while len(curCases) < numPerGroup
        num += 1
        cases += curCases
    pass # while num < groups

    f = open('TestCases/DistComp-CDRCD.txt', 'w')
    f.write('L1\tT1\tW1\tH1\tL2\tT2\tW2\tH2\tCD\tRCD\tGD\tRGD\tHD\tRHD\n')
    for x1, y1, width1, height1, x2, y2, width2, height2 in cases:
        rect1, rect2 = Rectangle(x1, y1, width1, height1), Rectangle(x2, y2, width2, height2)
        cd = calcCentroidDist(rect1, rect2)
        rcd = calcRelativeCentroidDist(rect1, rect2)
        gd = calcGapDist(rect1, rect2)
        rgd = calcRelativeGapDist(rect1, rect2)
        hd = calcHausdorffDist(rect1, rect2)
        rhd = calcRelativeHausdorffDist(rect1, rect2)
        f.write('%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\n' % \
                (x1, y1, width1, height1, x2, y2, width2, height2, cd, rcd, gd, rgd, hd, rhd ))
    pass # for x1, y1, width1, height1, x2, y2, width2, height2 in cases
pass # def showDefect_CD_RCD(groups, numPerGroup)


if __name__ == '__main__':
    numPerGroup = 20
    groups = 2

    showDefect_GD_RGD(groups, numPerGroup)
    showDefect_CD_RCD(groups, numPerGroup)
pass # if __name__ == '__main__'
