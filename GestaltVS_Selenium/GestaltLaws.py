'''
Created on Jun 21, 2016

@author: MarcoXZh
'''

import sys, re
import xml.etree.ElementTree as ET
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from PIL import Image
from ImageComparison import calcSSIM

def sameColor(color1, color2):
    '''
    @param color1:         {String} rgb string such as "rgb(0,0,0)"
    @param color2:         {String} rgb string such as "rgb(0,0,0)"
    @return:               {Boolean} True if the two colors are the same; False otherwise
    '''
    if color1 == "transparent" and color2 == "transparent":
        return True
    if color1 != "transparent" and color2 != "transparent":
        if "," in color1:
            rgb1 = re.split(r"\D+", color1)[1:-1]
            rgb1 = sRGBColor(int(rgb1[0]), int(rgb1[1]), int(rgb1[2]), is_upscaled=True)
        else:
            rgb1 = sRGBColor.new_from_rgb_hex(color1)
        if "," in color2:
            rgb2 = re.split(r"\D+", color2)[1:-1]
            rgb2 = sRGBColor(int(rgb2[0]), int(rgb2[1]), int(rgb2[2]), is_upscaled=True)
        else:
            rgb2 = sRGBColor.new_from_rgb_hex(color2)
        return delta_e_cie2000(convert_color(rgb1, LabColor), convert_color(rgb2, LabColor)) < 4.65
    pass # if color1 != "transparent" and color2 != "ransparent"
    return False
pass # def sameColor(color1, color2)

def sameImage(img1, img2):
    empty1 = (img1 == "none" or img1 == "")
    empty2 = (img2 == "none" or img2 == "")
    if empty1 and empty2:
        return True
    if not empty1 or not empty2:
        return False
    if img1 == img2:
        return True
#     return False
    return calcSSIM(Image.open(img1), Image.open(img2)) < 0.4
pass # def sameImage(img1, img2)

def normalizedHausdorffDistance(node1, node2):

    def normailizedDistance_AtoB(nodeA, nodeB):
        leftA = 1.0 * int(nodeA.location["x"])
        topA = 1.0 * int(nodeA.location["y"])
        rightA = 1.0 * int(nodeA.location["x"]) + int(nodeA.size["width"])
        bottomA = 1.0 * int(nodeA.location["y"]) + int(nodeB.size["height"])
        leftB = 1.0 * int(nodeB.location["x"])
        topB = 1.0 * int(nodeB.location["y"])
        rightB = 1.0 * int(nodeB.location["x"]) + int(nodeB.size["width"])
        bottomB = 1.0 * int(nodeB.location["y"]) + int(nodeB.size["height"])
        widthA, widthB = abs(rightA - leftA), abs(rightB - leftB);
        heightA, heightB = abs(bottomA - topA), abs(bottomB - topB);
        centerXA, centerYA = leftA + 0.5 * widthA, topA + 0.5 * heightA;
        centerXB, centerYB = leftB + 0.5 * widthB, topB + 0.5 * heightB

        if leftA >= leftB and rightA <= rightB and topA >= topB and bottomA <= bottomB:
            return 0.0
        if leftA >= leftB and rightA <= rightB:
            return (abs(topB - topA) if centerYA  < centerYB else abs(bottomA - bottomB)) / heightA
        if topA >= topB and bottomA <= bottomB:
            return (abs(leftB - leftA) if centerXA < centerXB else abs(rightA - rightB)) / widthA
        deltaX = leftB - leftA if centerXA < centerXB else rightA - rightB
        deltaY = topB - topA if centerYA < centerYB else bottomA - bottomB
        return (deltaX ** 2.0 + deltaY ** 2.0) ** 0.5 / (widthA ** 2.0 + heightA ** 2.0) ** 0.5
    pass # def normailizedDistance_AtoB(nodeA, nodeB)

    return max(normailizedDistance_AtoB(node1, node2), normailizedDistance_AtoB(node2, node1))
pass # def normalizedHausdorffDistance(node1, node2)

def MergeNodeByGestaltLaws(elements, parent, CSS, debug=False):
    '''
    @param elements:       {List} contains all sibling WebElements, both visible and invisible
    @param parent:         {ET.Element} the parent of the newly created BT nodes
    @param CSS:            {List} contains all supported CSS properties
    @param debug:          {Boolean} (Optional) True to display debugging information; False not
    @return :              {Tuple} the BT nodes created, as well as the BT-DT map list
    '''
    children = []
    for e in elements:
        if e.is_displayed() and int(e.size["height"]) != 0 and int(e.size["width"]) != 0.0:
            children.append(e)
    pass # for - if
    elements = children

    if len(elements) == 0:
        return [], []

    nhds, sames = [], []
    for i, sibling in enumerate(elements):
        if i == len(elements)-1:
            break
        node1, node2 = sibling, elements[i+1]
        same = (node1.value_of_css_property("position") == node2.value_of_css_property("position"))     # Common fate
        if not same:                                                                                    # Continuity
            same = (int(node1.location["x"]) == int(node2.location["x"]) or \
                    int(node1.location["y"]) == int(node2.location["y"]) or \
                    int(node1.location["x"]) + int(node1.size["width"]) == \
                    int(node2.location["x"]) + int(node2.size["width"]) or \
                    int(node1.location["y"]) + int(node1.size["height"]) == \
                    int(node2.location["y"]) + int(node2.size["height"]))
        if not same:                                                                                    # Similarity
            idx = 0
            while idx < len(CSS):
                css1 = node1.value_of_css_property(CSS[idx]).strip()
                css2 = node2.value_of_css_property(CSS[idx]).strip()
                if "color" in CSS[idx] and not sameColor(css1, css2):
                    break
                if "image" in CSS[idx] and not sameImage(css1, css2):
                    break
                if css1 != css2:
                    break
                idx += 1
            pass # while idx < len(CSS)
            same = (idx >= len(CSS))
        pass # if not same
        sames.append(same)
        nhds.append(normalizedHausdorffDistance(node1, node2))                                            # Proximity
    pass # for i, sibling in enumerate(elements)

    if debug and (len(sames) != len(elements) - 1 or len(nhds) != len(elements) - 1):
        print "Error: NHDs and SAMEs size issue"
    btNodeMapList, btNodes = [], []
    curNodeMapList, curNodes = [0], [elements[0]]
    if len(elements) != 1:
        avg = 1.0 * sum(nhds) / len(nhds)
        for i in range(len(nhds)):
            if nhds[i] <= avg or sames[i]:
                curNodeMapList.append(i+1)
                curNodes.append(elements[i+1])
            else:
                btNodeMapList.append(curNodeMapList)
                curNodeMapList = [i+1]
                btNodes.append(curNodes)
                curNodes = [elements[i+1]]
            pass # else - if nhds[i] <= avg or sames[i]
        pass # for i in range(len(nhds))
        if len(curNodeMapList) > 0:
            btNodeMapList.append(curNodeMapList)
            btNodes.append(curNodes)
        pass # if len(curNodeMapList) > 0
    pass # if len(elements) != 1
    pXpath = parent.attrib["xpath"] + "/"
    for i, nodes in enumerate(btNodes):
        btNode = ET.SubElement(parent, "DIV")
        node_name = "[%s]" % (",".join(str(x) for x in btNodeMapList[i]))
        btNode.set("node_name", node_name)
        btNode.set("xpath", pXpath + node_name)
        left, top, right, bottom = sys.maxint, sys.maxint, -1, -1
        for node in nodes:
            l, r = int(node.location["x"]), int(node.location["x"]) + int(node.size["width"])
            t, b = int(node.location["y"]), int(node.location["y"]) + int(node.size["height"])
            if l < left:    left = l
            if t < top:     top = t
            if r > right:   right = r
            if b > bottom:  bottom = b
        pass # for node in nodes
        btNode.set("left", "%d" % left)
        btNode.set("top", "%d" % top)
        btNode.set("right", "%d" % right)
        btNode.set("bottom", "%d" % bottom)
        for style in CSS:
            v = nodes[0].value_of_css_property(style)
            btNode.set("css_" + style, v)
        pass # for style in CSS
        btNodes[i] = btNode
    pass # for i, nodes in enumerate(btNodes)

    return btNodeMapList, btNodes
pass # def MergeNodeByGestaltLaws(elements, parent, CSS, debug=False)
