'''
Created on Dec 14, 2015

@author: MarcoXZh
'''

import os, json


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

def calcCentroidDist(rect1, rect2):
    assert type(rect1) is Rectangle and type(rect2) is Rectangle
    cx1, cy1 = rect1.getCentroid()
    cx2, cy2 = rect2.getCentroid()
    return ((cx1 - cx2) ** 2.0 + (cy1 - cy2) ** 2.0) ** 0.5
pass # def calcCentroidDist(rect1, rect2)

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

def mergeExperimentResults(rounds):
    records = []
    for i in range(rounds):
        f = open(os.path.join('TestCases', 'DistResults%d.txt' % (i+1)), 'r')
        idx = 0
        for line in f:
            obj = json.loads(line.strip())
            if i == 0:
                records.append(obj['cd'] + obj['gd'] + obj['hd'] + obj['nd'])
            else:
                records[idx] += obj['cd'] + obj['gd'] + obj['hd'] + obj['nd']
            idx += 1
        f.close()
    pass # for i in range(rounds)
    f = open(os.path.join('TestCases', 'DistComparison.log'), 'w')
    header = []
    for i in range(rounds):
        header += ['CD1-%d' % (i+1), 'CD2-%d' % (i+1), 'GD1-%d' % (i+1), 'GD2-%d' % (i+1), 
                   'HD1-%d' % (i+1), 'HD2-%d' % (i+1), 'ND1-%d' % (i+1), 'ND2-%d' % (i+1)]
    f.write('\t'.join(header) + '\n')
    for r in records:
        f.write('\t'.join(['%.4f' % x for x in r]) + '\n')
    f.close()
pass # def mergeExperimentResults(rounds)


if __name__ == '__main__':
    rounds = 5
    mergeExperimentResults(rounds)

    deltas = []
    f = open(os.path.join('TestCases', 'DistComparison.log'), 'r')
    idx = 0
    for line in f:
        idx += 1
        if idx == 1:
            continue
        cols = line.strip().split('\t')
        assert len(cols) == rounds * 8
        row = []
        for i in range(len(cols)/2):
            row.append(float(cols[i*2+1]) - float(cols[i*2]))
        deltas.append(row)
    pass # for line in f
    f.close()
    for d in deltas:
        for x in d:
            print '%.4f\t' % x,
        print
    pass # for d in deltas

pass # if __name__ == '__main__'
