'''
Created on Jan 20, 2016

@author: MarcoXZh
'''
import os, random, shutil

def cleanTestCases(oDir, dDir, groupSize=50, debug=False):
    '''
    Clean the raw test cases
    @param oDir:      {String} the path of the raw test case folder
    @param dDir:      {String} the path of the clean test case folder
    @param groupSize: {Integer} number of test cases per subset
    @param debug:     {Boolean} print out debugging information if true; otherwise not print
    '''
    # Get all positive test cases
    if debug:
        print '%s -- %-50s' % ('VisualSimilarity.cleanTestCases', 'Collecting positive test cases...'),
    pass # if debug
    files = os.listdir(oDir)
    URLs = set()
    for f in files:
        if f.endswith('.png') and f[:-4] + '-brief.txt' in files and \
           f[:-4] + '-DT.xml' in files and f[:-4] + '-VT.xml' in files and f[:-4] + '-BT.xml' in files:
            URLs.add(f[:-4])
    pass # for - if

    # Remove long URLs
    if debug:
        print 'done'
        print '%s -- %-50s' % ('VisualSimilarity.cleanTestCases', 'Removing long URLs...'),
    pass # if debug
    URLs = sorted(list(URLs), key=lambda x: len(x))[:groupSize*int(len(URLs)/groupSize)]
    maxLength = max([len(url) for url in URLs])
    while maxLength > 190:
        URLs = URLs[:100*int(len(URLs[:-1])/100)]
        maxLength = max([len(url) for url in URLs])
    pass # while maxLength > 190
    if debug:
        print 'done'
        print '%s -- %-50s' % ('VisualSimilarity.cleanTestCases', 'Dropping negative test cases...'),
    pass # if debug
    for f in files:
        if (f.endswith('.png') and f[:-4] not in URLs) or \
           (f.endswith('.txt') and f[:-10] not in URLs) or \
           (f.endswith('.xml') and f[:-7] not in URLs):
            os.remove(os.path.join(oDir, f))
    pass # for f in files

    # Shuffle and split the rest URLs into subsets
    records = {}
    URLs.sort()
    for i in range(len(URLs)):
        URLs[i] = (i+1, URLs[i])
        records[i+1] = URLs[i]
    pass # for i in range(len(URLs))
    groupIdx, groups = 1, int(len(URLs) / groupSize)
    if debug:
        print 'done'
        print '%s -- %-50s' % ('VisualSimilarity.cleanTestCases', 'Splitting test cases...')
    pass # if debug
    while len(URLs) >= groupSize:
        random.shuffle(URLs)
        subset = URLs[:groupSize]
        subPath = os.path.join(dDir, 'Subset%02d' % groupIdx)
        if os.path.exists(subPath):
            shutil.rmtree(subPath)
        os.mkdir(subPath)
        for num, url in enumerate(subset):
            if debug:
                print '%s -- %-50s' % ('VisualSimilarity.cleanTestCases',
                      '  Splitting: group=%02d/%02d, url=%02d/%02d %s' % (groupIdx, groups, num+1, len(subset), url))
            pass # if debug
            shutil.copyfile(os.path.join(oDir, '%s.png' % url[1]), \
                            os.path.join(subPath, '%03d.png' % url[0]))
            shutil.copyfile(os.path.join(oDir, '%s-brief.txt' % url[1]), \
                            os.path.join(subPath, '%03d-brief.txt' % url[0]))
            shutil.copyfile(os.path.join(oDir, '%s-DT.xml' % url[1]), \
                            os.path.join(subPath, '%03d-DT.xml' % url[0]))
            shutil.copyfile(os.path.join(oDir, '%s-VT.xml' % url[1]), \
                            os.path.join(subPath, '%03d-VT.xml' % url[0]))
            shutil.copyfile(os.path.join(oDir, '%s-BT.xml' % url[1]), \
                            os.path.join(subPath, '%03d-BT.xml' % url[0]))
            records[url[0]] = (groupIdx, url[1])
        pass # for num, url in enumerate(subset)
        groupIdx += 1
        URLs = URLs[groupSize:]
    pass # while len(URLs) >= groupSize

    # Save the splitting records
    if debug:
        print '%s -- %-50s' % ('VisualSimilarity.cleanTestCases', 'Saving splitting results...'),
    pass # if debug
    f = open(os.path.join(dDir, 'TestCases.log'), 'w')
    f.write('Index\tSubset\tURL\n')
    keys = sorted(records.keys())
    digitURLs = 0 if len(keys) == 0 else len(str(max(keys)))
    digitGroups = 0 if groupIdx == 0 else len(str(groupIdx))
    for key in keys:
        f.write(('%%0%dd\t%%0%dd\t%%s\n' % (digitURLs, digitGroups)) % (key, records[key][0], records[key][1]))
    pass # for key in keys
    f.close()
    if debug:
        print 'done'
    pass # if debug
pass # def cleanTestCases(oDir, dDir, groupSize=50, debug=False)


if __name__ == '__main__':
    # Clean the raw pages crawled by GestaltVS
    cleanTestCases(os.path.join('D:\\', 'Crawling'), os.path.join('D:\\', 'TestCases\\'), groupSize=100, debug=True)
pass # if __name__ == '__main__'
