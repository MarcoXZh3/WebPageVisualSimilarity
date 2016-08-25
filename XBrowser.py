'''
Created on Aug 23, 2016

@author: Marco
'''

import os, natsort, shutil
import inspect


def extractFullCases(basedir1, basedir2, paths, copy=True, debug=False):
    '''
    From the raw test cases, remove incomplete cases, and then rename the rest
    @param basedir1:    {String} the base source directory of all the different scenarios
    @param basedir2:    {String} the base target directory of all the different scenarios
    @param paths:       {List} a list of the directories of all the different scenarios
    @param copy:        {Boolean} True to copy the files to a new path; False move
    @param debug:       {Boolean} True to display debugging information; False not
    '''
    # Collect all cases
    if debug:
        s = inspect.stack()
        print "%s->%s: %s" % (inspect.getmodulename(s[1][1]), s[0][3], \
                "collecting all test cases ..."),
    pass # if debug
    records = set()
    for i, p in enumerate(paths):
        for f in os.listdir(os.path.join(basedir1, p)):
            if (p.startswith("C") and f.endswith("-BT.txt")) or (p.startswith("F") and f.endswith("-BT.xml")):
                records.add(f.split("-BT.")[0])
    pass # for - for - if
    if debug:
        print "done -- %d" % len(records)
    pass # if debug

    # Copy/move only the complete cases into the new path
    if debug:
        s = inspect.stack()
        print "%s->%s: %s" % (inspect.getmodulename(s[1][1]), s[0][3], \
                "collecting complete test cases ...")
    pass # if debug
    for p in paths:
        os.mkdir(os.path.join(basedir2, p))
    cnt = 0
    log = open(os.path.join(basedir2, "URLs.txt"), "w")
    log.close()
    for i, r in enumerate(natsort.natsorted(list(records))):
        complete = True
        for p in paths:
            if p.startswith("C"):
                if not os.path.isfile(os.path.join(basedir1, p, r + ".txt")) or \
                   not os.path.isfile(os.path.join(basedir1, p, r + "-BT.txt")) or \
                   not os.path.isfile(os.path.join(basedir1, p, r + "-DT.txt")) or \
                   not os.path.isfile(os.path.join(basedir1, p, r + "-VT.txt")):
                    complete = False
                    break
            elif p.startswith("F"):
                if not os.path.isfile(os.path.join(basedir1, p, r + "-brief.txt")) or \
                   not os.path.isfile(os.path.join(basedir1, p, r + "-BT.xml")) or \
                   not os.path.isfile(os.path.join(basedir1, p, r + "-DT.xml")) or \
                   not os.path.isfile(os.path.join(basedir1, p, r + "-VT.xml")):
                    complete = False
                    break
            pass # if - elif
        pass # for p in paths
        if complete:
            cnt += 1
            func = shutil.copy if copy else shutil.move
            for p in paths:
                func(os.path.join(basedir1, p, r + (".txt" if p.startswith("C") else "-brief.txt")), \
                     os.path.join(basedir2, p, "%04d-MR.txt" % cnt))
                func(os.path.join(basedir1, p, r + ("-BT.txt" if p.startswith("C") else "-BT.xml")), \
                     os.path.join(basedir2, p, "%04d-BT.xml" % cnt))
                func(os.path.join(basedir1, p, r + ("-DT.txt" if p.startswith("C") else "-DT.xml")), \
                     os.path.join(basedir2, p, "%04d-DT.xml" % cnt))
                func(os.path.join(basedir1, p, r + ("-VT.txt" if p.startswith("C") else "-VT.xml")), \
                     os.path.join(basedir2, p, "%04d-VT.xml" % cnt))
            pass # for p in paths:
            log = open(os.path.join(basedir2, "URLs.txt"), "a")
            log.write("%s\n" % (r.replace('%5C', '\\').replace('%2F', '/').replace('%3A', ':')\
                                 .replace('%2A', '*').replace('%3F', '?').replace('%22', '"')\
                                 .replace('%3C', '<').replace('%3E', '>').replace('%7C','|')))
            log.close()
            if debug:
                print "  %d/%d -- %d %s" % (i+1, len(records), cnt, r if len(r) < 50 else r[:47] + "...")
            pass # if debug
        pass # if complete
    pass # for i, r in enumerate(natsort.natsorted(list(records)))
    if debug:
        s = inspect.stack()
        print "%s->%s: %s" % (inspect.getmodulename(s[1][1]), s[0][3], \
                "collecting complete test cases ... done")
    pass # if debug
pass # def extractFullCases(basedir1, basedir2, paths, copy=True, debug=True)

def renameDiscontinuous(basedir, paths, cases, debug=True):
    '''
    Rename discontinuous test cases
    @param basedir:     {String} the base directory of all the different scenarios
    @param paths:       {List} a list of the directories of all the different scenarios
    @param cases:       {List} a list of the directories of test cases
    @param debug:       {Boolean} True to display debugging information; False not
    '''
    # Collect discontinuous cases
    if debug:
        s = inspect.stack()
        print "%s->%s: %s" % (inspect.getmodulename(s[1][1]), s[0][3],
                "collecting all discontinuous test cases ..."),
    pass # if debug
    fmap = []
    files = natsort.natsorted([f for f in os.listdir(os.path.join(basedir, paths[0])) if f.endswith("-MR.txt")])
    for i, f in enumerate(files):
        fmap.append(int(f.split("-MR.txt")[0]))
    if debug:
        for i, m in enumerate(files):
            assert i+1 <= m
        print "done"
    pass # if debug
 
    # rename cases
    if debug:
        s = inspect.stack()
        print "%s->%s: %s" % (inspect.getmodulename(s[1][1]), s[0][3], "renaming ...")
    pass # if debug
    for i, p in enumerate(paths):
        for j, m in enumerate(fmap):
            if j+1 < m:
                os.rename(os.path.join(basedir, p, "%04d-MR.txt" % m), os.path.join(basedir, p, "%04d-MR.txt" % (j+1)))
                os.rename(os.path.join(basedir, p, "%04d-BT.xml" % m), os.path.join(basedir, p, "%04d-BT.xml" % (j+1)))
                os.rename(os.path.join(basedir, p, "%04d-DT.xml" % m), os.path.join(basedir, p, "%04d-DT.xml" % (j+1)))
                os.rename(os.path.join(basedir, p, "%04d-VT.xml" % m), os.path.join(basedir, p, "%04d-VT.xml" % (j+1)))
            pass # if j+1 < m
        pass # for j, m in enumerate(fmap)
        if debug:
            print "  %d/%d: %s" % (i+1, len(paths), p)
        pass # if debug
    pass # for i, p in enumerate(paths)
    if debug:
        s = inspect.stack()
        print "%s->%s: %s" % (inspect.getmodulename(s[1][1]), s[0][3], "renaming ... done")
    pass # if debug

    # deal with EST records, if necessary
    if os.path.exists(os.path.join(basedir, "AD")) and os.path.exists(os.path.join(basedir, "NONAD")):
        if debug:
            s = inspect.stack()
            print "%s->%s: %s" % (inspect.getmodulename(s[1][1]), s[0][3], "renaming EST records ..."),
        pass # if debug
        for case in cases:
            for f in os.listdir(os.path.join(basedir, case)):
                lines = []
                txt = open(os.path.join(basedir, case, f), "r")
                for l in txt:
                    lines.append(l.strip().split("/"))
                txt.close()
                txt = open(os.path.join(basedir, case, f), "w")
                for l in lines:
                    txt.write("%s\n" %
                                 "/".join(l[:-1] + ["%04d-BT.xml" % (fmap.index(int(l[-1].split("-BT.xml")[0])) + 1)]))
                txt.close()
            pass # for f in os.listdir(os.path.join(basedir, case))
        pass # for case in cases
        if debug:
            print "done"
        pass # if debug
    pass # if os.path.exists(os.path.join(basedir, "AD")) and os.path.exists(os.path.join(basedir, "NONAD"))

    # deal with the URLs.txt, if necessary
    if os.path.exists(os.path.join(basedir, "URLs.txt")):
        allurls = []
        if debug:
            s = inspect.stack()
            print "%s->%s: %s" % (inspect.getmodulename(s[1][1]), s[0][3], "renaming URLs.txt ..."),
        pass # if debug
        txt = open(os.path.join(basedir, "URLs.txt"), "r")
        for l in txt:
            allurls.append(l)
        txt.close()
        txt = open(os.path.join(basedir, "URLs.txt"), "w")
        for m in fmap:
            txt.write(allurls[m])
        txt.close()
        if debug:
            print "done"
        pass # if debug
    pass # if os.path.exists(os.path.join(basedir, "URLs.txt"))
pass # def renameDiscontinuous(basedir, paths, debug=True)

def refineChromeMRs(basedir, paths, debug=True):
    '''
    Edit the Chrome merging results -- replace all "<br/>" to "\n"
    @param basedir:     {String} the base directory of all the different scenarios
    @param paths:       {List} a list of the directories of all the different scenarios
    @param debug:       {Boolean} True to display debugging information; False not
    '''
    if debug:
        s = inspect.stack()
        print "%s->%s:" % (inspect.getmodulename(s[1][1]), s[0][3])
    pass # if debug
    pidx, cnt = 0, len([p for p in paths if p.startswith("C")])
    for p in paths:
        if not p.startswith("C"):
            continue
        files = natsort.natsorted([f for f in os.listdir(os.path.join(basedir, p)) if f.endswith("-MR.txt")])
        for j, f in enumerate(files):
            if debug:
                print "  %d/%d(%s) -- %d/%d: %s" % (pidx+1, cnt, p, j+1, len(files), f),
            pass # if debug
            lines = []
            txt = open(os.path.join(basedir, p, f), "r")
            for l in txt:
                lines.append(l)
            txt.close()
            if debug:
                print "...",
            pass # if debug
            line = lines[0] if len(lines) == 1 else "".join(lines)
            lines = line.split("<br/>")
            txt = open(os.path.join(basedir, p, f), "w")
            for l in lines:
                txt.write(l + "\n")
            txt.close()
            if debug:
                print "... done"
            pass # if debug
        pass # for j, f in enumerate(files)
        pidx += 1
    pass # for p in paths
    if debug:
        s = inspect.stack()
        print "%s->%s: done" % (inspect.getmodulename(s[1][1]), s[0][3])
    pass # if debug
pass # def refineChromeMRs(basedir, paths, debug=True)

def dataCollection(basedir, cases, debug=True):
    '''
    Collect the test results and host names of the results
    @param basedir:     {String} the base directory of all the different scenarios
    @param cases:       {List} a list of the directories of all test cases
    @param debug:       {Boolean} True to display debugging information; False not
    '''
    if debug:
        assert os.path.exists(os.path.join(basedir, "URLs.txt"))
        s = inspect.stack()
        print "%s->%s:" % (inspect.getmodulename(s[1][1]), s[0][3]),
    pass # if debug

    # Retrieve URLs
    URLs = []
    txt = open(os.path.join(basedir, "URLs.txt"), "r")
    for l in txt:
        URLs.append(l.strip().split()[-1])
    txt.close()
    URLs = URLs[1:]
    if debug:
        print "...",
    pass # if debug

    # Determine host names
    hosts = []
    prefix = ["www", "bbs", "blog"]
    keywords = ["google", "amazon", "yahoo", "ebay", "yelp", "360", "craigslist", "rutracker"]
    postfix = [
        "39.net",           "51.la",                "ask.fm",           "ce.cn",
        "china.org.cn",     "chip.de",              "cntv.cn",          "csdn.net",
        "ettoday.net",      "focus.cn",             "gmw.cn",           "goo.ne.jp",
        "hatena.ne.jp",     "independent.co.uk",    "kaskus.co.id",     "libero.it",
        "mail.ru",          "mama.cn",              "news.cn",          "nicovideo.jp",
        "nih.gov",          "onet.pl",              "pixnet.net",       "rakuten.co.jp",
        "rambler.ru",       "rbc.ru",               "spiegel.de",       "web.de",
        "wp.pl",            "xuite.net",            "yandex.ru",        "youth.cn"
    ] # postfix = [ ... ]
    for url in URLs:
        host = url.split("//")[1].split("/")[0]
        words = host.split(".")
        if words[0] in prefix and len(words) > 2:
            words = words[1:]
        if words[-1] == "com":
            words = words[-2:]
        elif len(words) > 2 and words[-2] == "com":
            words = words[-3:]
        for kw in keywords:
            if kw in words:
                words = [kw]
        pass # for - if
        for p in postfix:
            if ".".join(words).endswith(p):
                words = [p]
        pass # for - if
        hosts.append(".".join(words))
    pass # for url in URLs
    if debug:
        print "...",
    pass # if debug

    # Collect EST values
    caseMap = [("CLvsCW", "EST-BT-0vs1.txt"), ("FLvsFW", "EST-BT-2vs3.txt"),
               ("CLvsFL", "EST-BT-0vs2.txt"), ("CWvsFW", "EST-BT-1vs3.txt"),
#                ("CLvsFW", "EST-BT-0vs3.txt"), ("CWvsFL", "EST-BT-1vs2.txt")
    ] # caseMap = [ ... ]
    keys, values = [], []
    for case in cases:
        for m, f in caseMap:
            ests = []
            txt = open(os.path.join(basedir, case, f), "r")
            for l in txt:
                ests.append(l.split("EST=")[-1].split(",")[0])
            txt.close()
            keys.append("%s-%s" % (m, case))
            values.append(ests)
    pass # for - for
    if debug:
        print "...",
    pass # if debug

    # Save results
    txt = open(os.path.join(basedir, "URLs.txt"), "w")
    txt.write("%s\n" % "\t".join(keys + ["HostName", "URL"]))
    for i in range(len(values[0])):
        txt.write("%s\n" % "\t".join([vs[i] for vs in values] + [hosts[i], URLs[i]]))
    txt.close()
    if debug:
        print "done"
    pass # if debug
pass # def dataCollection(basedir, cases, debug=True)

def topRecords(filename1, filename2, number, basedir, paths, debug=True):
    '''
    Retrieve and save the top records
    @param filename1:   {String} the source file
    @param filename1:   {String} the target file storing only the top records
    @param number:      {Integer} number of records to be kept
    @param basedir:     {String} the base directory of all the different scenarios
    @param paths:       {List} a list of the directories of all the different scenarios
    @param debug:       {Boolean} True to display debugging information; False not
    '''
    if debug:
        assert os.path.exists(filename1)
        s = inspect.stack()
        print "%s->%s: ..." % (inspect.getmodulename(s[1][1]), s[0][3]),
    pass # if debug
    txt = open(filename1, "r")
    values, lines = [], []
    for l in txt:
        if l.startswith("C"):
            header = l
            continue
        pass # if l.startswith("C")
        values.append([float(x) for x in l.split()[:8]])
        lines.append(l)
    pass # for l in txt
    txt.close()
    idxes = []
    while len(idxes) < len(values) - number:
        idx, lowest = -1, 100.0
        for i, vs in enumerate(values):
            if i in idxes:
                continue
            low = min(vs)
            if lowest > low:
                idx, lowest = i, low
        pass # for i, vs in enumerate(values)
        if debug:
            assert idx != -1
        pass # if debug
        idxes.append(idx)
        for p in paths:
            fs = [os.path.join(basedir, p, "%04d-MR.txt" % (idx+1)),
                  os.path.join(basedir, p, "%04d-BT.xml" % (idx+1)),
                  os.path.join(basedir, p, "%04d-DT.xml" % (idx+1)),
                  os.path.join(basedir, p, "%04d-VT.xml" % (idx+1))]
            for f in fs:
                if os.path.exists(f):
                    os.remove(f)
            pass # for - if
        pass # for p in paths
    pass # while len(values) > number
    txt = open(filename2, "w")
    txt.write(header)
    for i, l in enumerate(lines):
        if i not in idxes:
            txt.write(l)
    pass # for - if
    txt.close()
    if debug:
        print "done"
    pass # if debug
pass # def topRecords(filename1, filename2, number, debug=True)


if __name__ == '__main__':
    basedir1 = "D:\\"
    paths = ["CL-AD", "CL-NONAD", "CW-AD", "CW-NONAD", "FL-AD", "FL-NONAD", "FW-AD", "FW-NONAD"]
    cases = ["AD", "NONAD"]

    # Step 1: prepare the target path -- basedir2; create a new one if necessary
#     import datetime, re
#     assert os.path.exists(basedir1)
#     today = "".join(str(datetime.date.today()).split("-"))
#     basedir2 = os.path.join(basedir1, "XBrowser_%s" % today)
#     while os.path.exists(basedir2) and os.listdir(basedir2) != []:
#         xs = basedir2.split("_")
#         assert len(xs) == 2 or len(xs) == 3
#         if len(xs) == 3:
#             assert re.match(r'\d+', xs[-1])
#         idx = 2 if len(xs) == 2 else int(xs[-1]) + 1
#         basedir2 = os.path.join(basedir1, "_".join([xs[0], xs[1], str(idx)]))
#     pass # while os.path.exists(target)
#     if not os.path.exists(basedir2):
#         os.mkdir(basedir2)
    basedir2 = "D:\\XBrowser_20160823"

#     # Step 2: rename files of the raw
#     extractFullCases(basedir1, basedir2, paths)
#     # !!! Backup this step before moving on !!!

    # Step 3A: remove cases with non-well-formatted XMLs
    # this is done in the ExtendedSubtree model

    # Step 3B: rename discontinuous case names
#     renameDiscontinuous(basedir2, paths, cases)

    # Step 3C: clean Chrome results: replace "<br/>" to "\n"
#     refineChromeMRs(basedir2, paths)
    # !!! Backup this step before moving on !!!

    # Step 4: collect data
#     dataCollection(basedir2, cases)
    # !!! Backup this step before moving on !!!

    # Retrieve the best records
    th = 1000
    topRecords(os.path.join(basedir2, "URLs.txt"), os.path.join(basedir2, "URLs-%d.txt" % th), th, basedir2, paths)

pass # if __name__ == '__main__'
