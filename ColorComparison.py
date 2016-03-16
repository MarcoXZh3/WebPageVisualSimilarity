'''
Created on Jan 25, 2016

@author: MarcoXZh
'''
import os, json, natsort, re

def readData(debug=False):
    '''
    Read color test results from data files
    @param debug:     {Boolean} print out debugging information if true; otherwise not print
    @return:          {Matrix} [groups X (10 X numbers)], each element holds a tuple of deltaE and eucDist
    '''
    # Detect the result files to find out number of groups and number per group
    if debug:
        print '%s -- %-50s' % ('ColorComparison.readData', 'Detecting files...'),
    pass # if debug
    files = natsort.natsorted(os.listdir(os.path.join('TestCases', 'ColorComparison')))
    groups, numbers = set(), set()
    for f in files:
        cols = re.split('\\D+', f)
        if debug:
            assert len(cols) == 4 and cols[0] == '' and cols[1] != '' and cols[2] != '' and cols[3] == ''
        pass # if debug
        groups.add(cols[1])
        numbers.add(cols[2])
    pass # for f in files
    groups, numbers = len(groups), len(numbers)
    if debug:
        print 'done'
    pass # if debug

    # Read each data file to build up the result matrices
    results = []
    for i in range(groups):
        row = []
        for j in range(numbers):
            if debug:
                print '%s -- %-50s' % ('ColorComparison.readData', 'Reading file: (%d,%d)' % (i+1, j+1))
            pass # if debug
            f = open(os.path.join('TestCases', 'ColorComparison', 'results%d-%d.txt' % (i+1, j+1)))
            idx, cache = 0, 0.0
            for line in f:
                x = json.loads(line)
                if debug:
                    assert len(x) == 6 and x[-1]['isRGB'] is False if idx % 2 == 0 else True
                pass # if debug
                if idx % 2 == 0:
                    cache = sum([y['deltaE'] for y in x[:-1]]) / (len(x) - 1.0)
                else:
                    # Weighted Euclidean Distance for RGB: http://www.compuphase.com/cmetric.htm
                    for y in x[:-1]:
                        rgb1 = [int(y['color1'][1:3], 16), int(y['color1'][3:5], 16), int(y['color1'][5:], 16)]
                        rgb2 = [int(y['color2'][1:3], 16), int(y['color2'][3:5], 16), int(y['color2'][5:], 16)]
                        avgR = 0.5 * (rgb1[0] + rgb2[0])
                        y['eucDist'] = (((rgb1[0] - rgb2[0]) ** 2.0) * (2.0 + avgR / 256.0) +
                                        ((rgb1[1] - rgb2[1]) ** 2.0) * 4.0 +
                                        ((rgb1[2] - rgb2[2]) ** 2.0) * (2.0 + (255 - avgR) / 256.0)) ** 0.5
                    pass # for y in x[:-1]
                    row.append((cache, sum([y['eucDist'] for y in x[:-1]]) / (len(x) - 1.0)))
                pass # else - if idx % 2 == 0
                idx += 1
            pass # for line in f
            f.close()
        pass #for j in range(numbers)
        if debug:
            assert len(row) == numbers * 10
        pass # if debug
        results.append(row)
    pass # for i in range(groups)
    return results
pass # def readData(debug=False)


if __name__ == '__main__':
    # Read data from files
    results = readData()
#     for i, group in enumerate(results):
#         for j, v in enumerate(group):
#             print 'Group=%d, Number=%2d:\t DeltaE=%.4f, EucDist=%.4f' %  (i+1, j+1, v[0], v[1])
#     pass # for - for

    # Export results
    f = open(os.path.join('TestCases', 'ColorComparison.log'), 'w')
    f.write('\t'.join(natsort.natsorted(['DeltaE_%d' % (i+1) for i in range(len(results))] + \
                                        ['EucDist_%d' % (i+1) for i in range(len(results))])) + '\n')
    for i in range(len(results[0])):
        f.write('\t'.join(['%.6f' % group[i][0] for group in results] + \
                          ['%.6f' % group[i][1] for group in results]) + '\n')
    f.close()

pass # if __name__ == '__main__'
