#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Oct 6, 2016

@author: MarcoXZh
Alpuente, María, and Daniel Romero. "A visual technique for web pages comparison."
Electronic Notes in Theoretical Computer Science 235 (2009): 3-18.
http://www.sciencedirect.com/science/article/pii/S1571066109000814
http://users.dsic.upv.es/~dromero/web-cmp/web-cmp.html
'''

import os, sys, natsort, re, datetime
from zss import Node, simple_distance


def parseTreeFromStrings(tree, debug=False):
    """
    Create the tree from a list of strings
    @param tree:       {List} string format of the tree, one element per string
    @param debug:       {Boolean} True to display debugging information; False not
    @return:            {Dictionary} the three types of trees in the dictionary
    """
    if tree is None:
        return None

    root = None
    rightMosts, cur = [], 0
    for line in tree:
        header = line.split(": ")[0]
        level, tag = (0, header) if "|-" not in header else header.split("- ")
        tag = tag.strip()
        if "|-" in header:
            level = 1 + int(len(level) / 2)
        xs = [int(x) for x in re.split("\\D+", line) if x != ""]
        cur = Node("%s[x=%04d,y=%04d]" % (tag, xs[2]-xs[0], xs[3]-xs[1]))
        if level == len(rightMosts):
            rightMosts.append(cur)
        else:
            assert level < len(rightMosts)
            rightMosts[level] = cur
        pass # else - if level == len(rightMosts)
        if level == 0:
            root = cur
        else:
            rightMosts[level-1].addkid(cur)
        pass # else - if level == 0
    pass # for line in tree

    return root
pass # def parseTreeFromStrings(tree, debug=False)

def parseTrees(filename, treeTypes=["DT", "VT", "BT"], debug=False):
    """
    Parse the three types of trees from the record file
    @param filename:    {String} name of the file
    @param treeTypes:   {List} a list of supported tree types
    @param debug:       {Boolean} True to display debugging information; False not
    @return:            {Dictionary} the three types of trees in the dictionary
    """
    trees = {}
    for t in treeTypes:
        trees[t] = ["", []]
    bStarted, lines = False, []
    txt = open(filename, "r")
    for line in txt:
        line = line.strip()
        if line.startswith("===="):
            bStarted = not bStarted
            if bStarted:
                continue
            xs = line.split(": ")
            if xs[0][-2:] in treeTypes:
                trees[xs[0][-2:]][0] = xs[1].split("\"")[1]
                for l in lines:
                    trees[xs[0][-2:]][1].append(l)
            pass # if xs[0][-2:] in treeTypes
            lines = []
        elif bStarted:
            lines.append(line.strip())
        pass # else - if line.startswith("====")
    pass # for line in txt
    txt.close()

    for k, tree in trees.items():
        if debug:
            print k, len(tree[1]), tree[0]
        pass # if debug
        trees[k] = (tree[0], parseTreeFromStrings(tree[1], debug))
    pass # for k, tree in trees.items()
    return trees
pass # def parseTrees(filename, treeTypes=["DT", "VT", "BT"], debug=False)

def automation(treeTypes=["DT", "VT", "BT"], idx=-1, debug=False):
    """
    Automation of the experimental test cases
    @param treeTypes:   {List} a list of supported tree types
    @param idx:         {Integer} the index of the scenarios to be run. Default being -1 means run all scenarios
    @param debug:       {Boolean} True to display debugging information; False not
    """
    basedir = "D:\\"
    scenarios = [("CL-AD", "CW-AD"), ("FL-AD", "FW-AD"), ("CL-AD", "FL-AD"), ("CW-AD", "FW-AD"),
                 ("CL-NONAD", "CW-NONAD"), ("FL-NONAD", "FW-NONAD"), ("CL-NONAD", "FL-NONAD"), ("CW-NONAD", "FW-NONAD")]
    files = natsort.natsorted([f for f in os.listdir(os.path.join(basedir, scenarios[0][0])) if f.endswith("txt")])
    for i, case in enumerate(scenarios):
        if i != idx:
            continue
        logFile = open(os.path.join(basedir, "%d.log" % (i+1)), "w")
        logFile.close()
        for j, f in enumerate(files):
            url = ""
            try:
                t0 = datetime.datetime.now()
                f1, f2 = os.path.join(basedir, case[0], f), os.path.join(basedir, case[1], f)
                for tt in treeTypes:
                    url, tree1 = parseTrees(f1, treeTypes, debug)[tt]
                    len1 = len(str(tree1).split())
                    url2, tree2 = parseTrees(f2, treeTypes, debug)[tt]
                    len2 = len(str(tree2).split())
                pass # for tt in treeTypes
                assert url == url2
                # the last update of tt is "VT"
                log = "%s - %s: sim=%.4f. time=%s" % (f1, f2, 1.0 * simple_distance(tree1, tree2) / (len1 + len2), \
                                                      datetime.datetime.now() - t0)
                print j+1, log
                logFile = open(os.path.join(basedir, "%d.log" % (i+1)), "a")
                logFile.write(log + "\n")
                logFile.close()
            except:
                print "Error:", j+1, f, url
            pass # try - except
        pass # for j, file in enumerate(files)
    pass # for i, case in enumerate(scenarios)
pass # def automation(treeTypes=["DT", "VT", "BT"], idx=-1, debug=False)

def caseStudy(case, treeTypes=["DT", "VT", "BT"], debug=False):
    """
    Case study
    @param case:        {String} name of the case, also name of the directory
    @param treeTypes:   {List} a list of supported tree types
    @param debug:       {Boolean} True to display debugging information; False not
    """
    basedir = "D:\\"
    scenarios = [("CL", "CW"), ("FL", "FW"), ("CL", "FL"), ("CW", "FW")]
    print case
    for i, scenario in enumerate(scenarios):
        for tt in treeTypes:
            try:
                for j, ver in enumerate(["AD", "NONAD"]):
                    f1 = os.path.join(basedir, case, "%s-MR-%s.txt" % (scenario[0], ver))
                    f2 = os.path.join(basedir, case, "%s-MR-%s.txt" % (scenario[1], ver))
                    if not os.path.exists(f1) or not os.path.exists(f2):
                        if j != 0:
                            break
                        f1 = os.path.join(basedir, case, "%s-MR.txt" % scenario[0])
                        f2 = os.path.join(basedir, case, "%s-MR.txt" % scenario[1])
                    pass # if not os.path.exists(f1) or not os.path.exists(f2)
                    url1, tree1 = parseTrees(f1, treeTypes, debug)[tt]
                    len1 = len(str(tree1).split())
                    url2, tree2 = parseTrees(f2, treeTypes, debug)[tt]
                    len2 = len(str(tree2).split())
                    assert url1 == url2
                    print "\t", scenario, ver, 1.0 - 1.0 * simple_distance(tree1, tree2) / (len1 + len2)
                pass # for j, ver in enumerate(["AD", "NONAD"])
            except:
                print "Error: ", i+1, case, scenario
            pass # try - except
        pass # for tt in treeTypes
    pass # for i, scenario in enumerate(scenarios)
pass # def caseStudy(case, treeTypes=["DT", "VT", "BT"], debug=False)


if __name__ == '__main__':
    treeTypes = ["VT"]

    # Run case studies
#     caseStudy("Amazon.ca", treeTypes)
#     caseStudy("Google.ca", treeTypes)
#     caseStudy("w3schools-json", treeTypes)

    # Automation on the 1000 test cases
    idx = int(sys.argv[-1]) if len(sys.argv) == 2 else -1
#     automation(treeTypes, idx)
pass # if __name__ == '__main__'
