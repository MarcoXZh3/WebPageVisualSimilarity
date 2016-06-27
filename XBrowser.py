from selenium import webdriver
import xml.etree.ElementTree as ET
from XBrowserGestaltVars import *
from XBrowserGestalt import MergeNodeByGestaltLaws


def fullpage_screenshot(driver, imgFile, debug=False):
    '''
    http://seleniumpythonqa.blogspot.ca/2015/08/generate-full-page-screenshot-in-chrome.html
    @param driver:         {Selenium.webdriver} the driver of the current browser, containing all page information
    @param imgFile:        {String} the name of the target image file
    @param debug:          {Boolean} (Optional) True to display debugging information; False not
    '''
    import os, time
    from PIL import Image
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
                                                         CSS, debug)
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
            dtNode.set("left", int(child.location["x"]))
            dtNode.set("top", int(child.location["y"]))
            dtNode.set("right", int(child.location["x"]) + int(child.size["width"]))
            dtNode.set("bottom", int(child.location["y"]) + int(child.size["height"]))
            dtNode.set("xpath", "%s/*[%d]" % (chDomXpath, i+1))
            for style in CSS:
                dtNode.set("css_" + style, styles[style])
            nextParent["DT"] = dtNode
        pass # if "DT" in treeParents

        # Create a VT node
        if "VT" in treeParents:
            if child.is_displayed() or child.size["height"] == 0.0 or child.size["width"] == 0.0:
                if debug:
                    print "Creating VT node: %s" % child.tag_name
                vtNode = ET.SubElement(treeParents["VT"], "DIV")
                vtNode.set("node_name", child.tag_name)
                vtNode.set("left", int(child.location["x"]))
                vtNode.set("top", int(child.location["y"]))
                vtNode.set("right", int(child.location["x"]) + int(child.size["width"]))
                vtNode.set("bottom", int(child.location["y"]) + int(child.size["height"]))
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
    line, idx = "  ", 1
    while idx < level:
        line += "| "
        idx += 1
    atrs = root.attrib
    line += "+ %s: left=%d,top=%d,right=%d,bottom=%d; xpath=\"%s\"" % \
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
    @param browser:        {String} the name of the browser, such as "Firefox", "Chrome"
    @param trreTypes:      {Tuple} (Optional) the target tree types, including "DT", "VT" or "BT"
    @param debug:          {Boolean} (Optional) True to display debugging information; False not
    '''
    # Initialize the driver
    driver, imgFile = None, url.replace("/", "%E2").replace(":", "%3A").replace("?", "%3F")
    if browser == "Firefox":
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities["marionette"] = True
        driver = webdriver.Firefox(capabilities=firefox_capabilities)
        imgFile += "-FF.png"
    elif browser == "Chrome":
        driver = webdriver.Chrome()
        imgFile += "-CH.png"
    pass # elif - if

    # Get ready the browser window and then retrieve the page
    scrollbarwidth = 0
    if isinstance(driver, webdriver.Chrome):
        scrollbarwidth = 35
    elif isinstance(driver, webdriver.Firefox):
        scrollbarwidth = 29
    pass # elif - if
    driver.set_window_size(scrollbarwidth + 1024, 768)
    driver.get(url)

    # Take full page screenshot
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
        dtRoot.set("left", int(body.location["x"]))       # Using body.rect will raise exception for Google Chrome!!!
        dtRoot.set("top", int(body.location["y"]))
        dtRoot.set("right", int(body.location["x"]) + int(body.size["width"]))
        dtRoot.set("bottom", int(body.location["y"]) + int(body.size["height"]))
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
    if browser == "Firefox":
        theCSS = cssFF
    elif browser == "Chrome":
        theCSS = cssCH
    if debug:
        assert theCSS is not None
    for root in treeRoots.values():
        root.set("left", int(body.location["x"]))       # Using body.rect will raise exception for Google Chrome!!!
        root.set("top", int(body.location["y"]))
        root.set("right", int(body.location["x"]) + int(body.size["width"]))
        root.set("bottom", int(body.location["y"]) + int(body.size["height"]))
        for style in theCSS:
            v = body.value_of_css_property(style)
            for root in treeRoots.values():
                root.set("css_" + style, v)
        pass # for style in theCSS
    pass # for root in treeRoots.values()
    mr = []
    BuildTrees(driver, {"element":body, "dom_xpath":xpath}, treeRoots, theCSS, mr, debug=not True)
    if "DT" in treeTypes:
        xmlFile = url.replace("/", "%E2").replace(":", "%3A").replace("?", "%3F")
        if browser == "Firefox":
            xmlFile += "-FF-DT.xml"
        elif browser == "Chrome":
            xmlFile += "-CH-DT.xml"
#         trees["DT"].write(xmlFile)
        mr.append("\n")
        mr += printSubTree(treeRoots["DT"], 0, url, "DT", debug)
    pass # if "DT" in treeTypes
    if "VT" in treeTypes:
        xmlFile = url.replace("/", "%E2").replace(":", "%3A").replace("?", "%3F")
        if browser == "Firefox":
            xmlFile += "-FF-VT.xml"
        elif browser == "Chrome":
            xmlFile += "-CH-VT.xml"
#         trees["VT"].write(xmlFile)
        mr.append("\n")
        mr += printSubTree(treeRoots["VT"], 0, url, "VT", debug)
    pass # if "VT" in treeTypes
    if "BT" in treeTypes:
        xmlFile = url.replace("/", "%E2").replace(":", "%3A").replace("?", "%3F")
        if browser == "Firefox":
            xmlFile += "-FF-BT.xml"
        elif browser == "Chrome":
            xmlFile += "-CH-BT.xml"
#         trees["BT"].write(xmlFile)
        mr.append("\n")
        mr += printSubTree(treeRoots["BT"], 0, url, "BT", debug)
    pass # if "BT" in treeTypes
    txt = url.replace("/", "%E2").replace(":", "%3A").replace("?", "%3F")
    if browser == "Firefox":
        txt += "-FF.txt"
    elif browser == "Chrome":
        txt += "-CH.txt"
    f = open(txt, "w")
    for line in mr:
        f.write(line + "\n")
    f.close()

    # Finally, quit the browser
    driver.quit()
pass # def analyzePage(url, browser, treeTypes=("DT", "VT", "BT"), debug=False)


if __name__ == "__main__":
    urls = ["https://www.google.ca/"]
    for i, url in enumerate(urls):
        analyzePage(url, "Firefox")
#         analyzePage(url, "Chrome", ("VT"))
    pass # for i, url in enumerate(urls)
pass # if __name__ == "__main__"
