import os, time
from PIL import Image
from selenium import webdriver
import xml.etree.ElementTree as ET
from Variables import *
from GestaltLaws import MergeNodeByGestaltLaws


def fullpage_screenshot(driver, imgFile, debug=False):
    '''
    http://seleniumpythonqa.blogspot.ca/2015/08/generate-full-page-screenshot-in-chrome.html
    @param driver:         {Selenium.webdriver} the driver of the current browser, containing all page information
    @param imgFile:        {String} the name of the target image file
    @param debug:          {Boolean} (Optional) True to display debugging information; False not
    '''
    if debug:
        print("Starting full page screenshot workaround ...")
    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    if debug:
        print("Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height,viewport_width,viewport_height))
    rectangles = []
    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height
        if top_height > total_height:
            top_height = total_height
        while ii < total_width:
            top_width = ii + viewport_width
            if top_width > total_width:
                top_width = total_width
            if debug:
                print("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
            rectangles.append((ii, i, top_width,top_height))
            ii = ii + viewport_width
        pass # while ii < total_width
        i = i + viewport_height
    pass # while i < total_height
    stitched_image = Image.new("RGB", (total_width, total_height))
    previous = None
    part = 0
    for rectangle in rectangles:
        if not previous is None:
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            if debug:
                print("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
            time.sleep(1)
        pass # if not previous is None
        file_name = "part_{0}.png".format(part)
        if debug:
            print("Capturing {0} ...".format(file_name))
        driver.get_screenshot_as_file(file_name)
        screenshot = Image.open(file_name)
        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])
        pass # else - if rectangle[1] + viewport_height > total_height
        if debug:
            print("Adding to stitched image with offset ({0}, {1})".format(offset[0],offset[1]))
        stitched_image.paste(screenshot, offset)
        del screenshot
        os.remove(file_name)
        part = part + 1
        previous = rectangle
    pass # for rectangle in rectangles
    stitched_image.save(imgFile)
    if debug:
        print("Finishing full page screenshot workaround...")
pass # def fullpage_screenshot(driver, url, imgFile)

def BuildTrees(driver, parent, treeParents, CSS, mr, debug=False):
    '''
    @param driver:         {Selenium.webdriver} the driver of the current browser, containing all page information
    @param parent:         {Dict} contains the ET element as "element" and its DOM XPath as "dom_xapth"
    @param treeParents:    {Dict} contains the corresponding parent nodes as "DT", "VT" and "BT", respectively
    @param CSS:            {List} contains all the names of the supported CSS properties
    @param mr:             {List} contains the merging results, where each line is a string representing a VT node
    @param debug:          {Boolean} (Optional) True to display debugging information; False not
    '''
    # Create BT nodes from all child nodes
    btNodesMapList = []
    if "BT" in treeParents:
        btNodesMapList, btNodes = MergeNodeByGestaltLaws(driver.find_elements_by_xpath(parent["dom_xpath"] +"/*"), \
                                                         treeParents["BT"], CSS, debug)
        if debug:
            assert len(btNodes) == len(btNodesMapList)
    pass # if "BT" in treeParents

    children = driver.find_elements_by_xpath(parent["dom_xpath"] + "/*")
    if debug:
        print parent["dom_xpath"], len(children)
    if len(children) == 0:
        return
    for i in range(len(children)):
        chDomXpath = "%s/*[%d]" % (parent["dom_xpath"], i+1)
        child = driver.find_element_by_xpath(chDomXpath)
        if debug:
            print "Retrieving node: \"%s\" -- %s" % (chDomXpath, child.tag_name)
        nextParent, styles = {}, {}
        for style in CSS:
            styles[style] = child.value_of_css_property(style)

        # Create a DT node
        if "DT" in treeParents:
            if debug:
                print "Creating DT node: %s" % child.tag_name
            dtNode = ET.SubElement(treeParents["DT"], "DIV")
            dtNode.set("node_name", child.tag_name)
            dtNode.set("left", "%d" % int(child.location["x"]))
            dtNode.set("top", "%d" % int(child.location["y"]))
            dtNode.set("right", "%d" % (int(child.location["x"]) + int(child.size["width"])))
            dtNode.set("bottom", "%d" % (int(child.location["y"]) + int(child.size["height"])))
            dtNode.set("xpath", "%s/*[%d]" % (chDomXpath, i+1))
            for style in CSS:
                dtNode.set("css_" + style, styles[style])
            nextParent["DT"] = dtNode
        pass # if "DT" in treeParents

        # Create a VT node
        if "VT" in treeParents:
            if child.is_displayed() and int(child.size["height"]) != 0 and int(child.size["width"]) != 0:
                if debug:
                    print "Creating VT node: %s" % child.tag_name
                vtNode = ET.SubElement(treeParents["VT"], "DIV")
                vtNode.set("node_name", child.tag_name)
                vtNode.set("left", "%d" % int(child.location["x"]))
                vtNode.set("top", "%d" % int(child.location["y"]))
                vtNode.set("right", "%d" % (int(child.location["x"]) + int(child.size["width"])))
                vtNode.set("bottom", "%d" % (int(child.location["y"]) + int(child.size["height"])))
                vtNode.set("xpath", "%s/*[%d]" % (chDomXpath, i+1))
                for style in CSS:
                    vtNode.set("css_" + style, styles[style])
                nextParent["VT"] = vtNode
            else:
                if debug:
                    print "Creating VT node - skipping invisible node: %s" % child.tag_name
                nextParent["VT"] = treeParents["VT"]
            pass # else - if child.is_displayed()
        pass # if "VT" in treeParents and child.is_displayed()

        if "BT" in treeParents:
            btNode = None
            for j, nodeMap in enumerate(btNodesMapList):
                if i in nodeMap:
                    btNode = btNodes[j]
                    break
            pass # for - if
            nextParent["BT"] = btNode if btNode is not None else treeParents["BT"]
        pass # if "BT" in treeParents

        # Build the sub tree from this child node
        BuildTrees(driver, {"element":child, "dom_xpath":chDomXpath}, nextParent, CSS, mr, debug)
    pass # for i, ch in enumerate(children)
pass # def BuildTrees(driver, parent, treeParents, CSS, mr, debug=False)

def printSubTree(root, level, treeName, treeType, debug=False):
    '''
    @param root:           {ET.Element} the root of the sub tree
    @param level:          {Integer} the depth of the sub tree root in the whole tree
    @param treeName:       {String} the name of the tree
    @param treeType:       {String} the type of the tree, either "DT", "VT" or "BT"
    @param debug:          {Boolean} (Optional) True to display debugging information; False not
    @return :              {List} the output string list, where each line is a node
    '''
    output = []
    if level == 0:
        output.append("==== %s: %s ====" % (treeName, treeType))
    line, idx = "  ", 0
    while idx < level:
        line += "| "
        idx += 1
    atrs = root.attrib
    line += "+ %s: left=%s,top=%s,right=%s,bottom=%s; xpath=\"%s\"" % \
            (atrs["node_name"], atrs["left"], atrs["right"], atrs["right"], atrs["bottom"], atrs["xpath"])
    output.append(line)

    for child in root:
        output += printSubTree(child, level+1, treeName, treeType, debug)

    if level == 0:
        output.append("==== %s: %s ====" % (treeName, treeType))
    return output
pass # def printSubTree(root, level, treeName, treeType, debug=False)

def analyzePage(url, browser, treeTypes=("DT", "VT", "BT"), debug=False):
    '''
    @param url:            {String} the URL of the page
    @param browser:        {String} the short name of the browser, such as "FF", "CH"
    @param trreTypes:      {Tuple} (Optional) the target tree types, including "DT", "VT" or "BT"
    @param debug:          {Boolean} (Optional) True to display debugging information; False not
    @return :              {Boolean} True if successfully analyzed the page; False otherwise
    '''
    # Initialize the driver
    driver, flag = None, False
    if browser == "FF":
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities["marionette"] = True
        driver = webdriver.Firefox(capabilities=firefox_capabilities)
    elif browser == "CH":
        driver = webdriver.Chrome()
    elif browser == "PH":
        driver = webdriver.PhantomJS()
    elif browser == "EG":
        driver = webdriver.Edge('C:\\Program Files (x86)\\Microsoft Web Driver\\MicrosoftWebDriver.exe')
    pass # elif - if

    try:
        # Get ready the browser window and then retrieve the page
        driver.set_window_size(1024, 768)
        driver.get(url)

        # Take full page screenshot
        imgFile = "/run/media/marco/0002A8780009A3C6/TestCases/%s-%s.png" % \
                    (url.replace("/", "%E2").replace(":", "%3A").replace("?", "%3F"), browser)
        fullpage_screenshot(driver, imgFile)

        # Parse and save: DOM tree, Visual tree and block tree
        xpath = "/html/body"
        body = driver.find_element_by_xpath(xpath)
        trees, treeRoots = {}, {}
        if "DT" in treeTypes:
            dtRoot = ET.Element("BODY")
            dtRoot.set("tree_name", url)
            dtRoot.set("tree_type", "DT")
            dtRoot.set("node_name", body.tag_name)
            dtRoot.set("xpath", xpath)
            trees["DT"] = ET.ElementTree(dtRoot)
            treeRoots["DT"] = dtRoot
        pass # if "DT" in treeTypes
        if "VT" in treeTypes:
            vtRoot = ET.Element("BODY")
            vtRoot.set("tree_name", url)
            vtRoot.set("tree_type", "VT")
            vtRoot.set("node_name", body.tag_name)
            vtRoot.set("xpath", xpath)
            trees["VT"] = ET.ElementTree(vtRoot)
            treeRoots["VT"] = vtRoot
        pass # if "VT" in treeTypes
        if "BT" in treeTypes:
            btRoot = ET.Element("BODY")
            btRoot.set("tree_name", url)
            btRoot.set("tree_type", "BT")
            btRoot.set("node_name", body.tag_name)
            btRoot.set("xpath", "/html/[2]")                 # "/html/*[1]" is HEAD
            trees["BT"] = ET.ElementTree(btRoot)
            treeRoots["BT"] = btRoot
        pass # if "BT" in treeTypes
        theCSS = None
        if browser == "FF":
            theCSS = cssFF
        else:#if browser == "CH" or browser == "PH":
            theCSS = cssCH
        if debug:
            assert theCSS is not None
        for root in treeRoots.values():         # Using body.rect will raise exception for Google Chrome!!!
            root.set("left", "%d" % int(body.location["x"]))
            root.set("top", "%d" % int(body.location["y"]))
            root.set("right", "%d" % (int(body.location["x"]) + int(body.size["width"])))
            root.set("bottom", "%d" % (int(body.location["y"]) + int(body.size["height"])))
            for style in theCSS:
                v = body.value_of_css_property(style)
                for root in treeRoots.values():
                    root.set("css_" + style, v)
            pass # for style in theCSS
        pass # for root in treeRoots.values()
        mr = []
        BuildTrees(driver, {"element":body, "dom_xpath":xpath}, treeRoots, theCSS, mr, debug=not True)
        xmlFile = "/run/media/marco/0002A8780009A3C6/TestCases/%s-%s" % \
                    (url.replace("/", "%E2").replace(":", "%3A").replace("?", "%3F"), browser)
        if "DT" in treeTypes:
            trees["DT"].write(xmlFile + "-DT.xml")
            mr.append("\n")
            mr += printSubTree(treeRoots["DT"], 0, url, "DT", debug)
        pass # if "DT" in treeTypes
        if "VT" in treeTypes:
            trees["VT"].write(xmlFile + "-VT.xml")
            mr.append("\n")
            mr += printSubTree(treeRoots["VT"], 0, url, "VT", debug)
        pass # if "VT" in treeTypes
        if "BT" in treeTypes:
            trees["BT"].write(xmlFile + "-BT.xml")
            mr.append("\n")
            mr += printSubTree(treeRoots["BT"], 0, url, "BT", debug)
        pass # if "BT" in treeTypes
        f = open("/run/media/marco/0002A8780009A3C6/TestCases/%s-%s.txt" % \
                    (url.replace("/", "%E2").replace(":", "%3A").replace("?", "%3F"), browser), "w")
        for line in mr:
            f.write(line + "\n")
        f.close()
        flag = True
    except Exception as inst:
        print type(inst), inst
        errFile = open("/run/media/marco/0002A8780009A3C6/TestCases/err.txt", "a")
        errFile.write("%s - %s\n" % (browser, url))
        errFile.close()
    finally:
        driver.quit()
        return flag
    pass # try - except - finally
pass # def analyzePage(url, browser, treeTypes=("DT", "VT", "BT"), debug=False)


if __name__ == "__main__":
#     urls = ["https://www.google.ca/"]
    browsers = ["FF", "CH", "PH"]
    logFile = open("/run/media/marco/0002A8780009A3C6/TestCases/log.txt", "w")
    logFile.close()
    errFile = open("/run/media/marco/0002A8780009A3C6/TestCases/err.txt", "w")
    errFile.close()
    for i, url in enumerate(urls):
        for j, browser in enumerate(browsers):
            print "%4d-%d(%s) -- %s" % (i+1, j+1, browser, url)
            t1 = time.time()
            flag = analyzePage(url, browser)
            t2 = time.time()
            if flag:
                print "%4d-%d(%s) -- %ds" % (i+1, j+1, browser, t2 - t1)
                logFile = open("/run/media/marco/0002A8780009A3C6/TestCases/log.txt", "a")
                logFile.write("%4d-%d(%s): %ds -- %s\n" % (i+1, j+1, browser, t2 - t1, url))
                logFile.close()
            else:
                print "ERROR! %4d-%d(%s) -- %ds" % (i+1, j+1, browser, t2 - t1)
            pass # else - if flag
        pass # for j, browser in enumerate(browsers)
    pass # for i, url in enumerate(urls)
pass # if __name__ == "__main__"
