'''
Created on Mar 8, 2016

@author: Marco
'''
import os, shutil, random, re, datetime, natsort, math
import numpy
from skimage import img_as_float
from skimage.measure import compare_ssim as ssim
from PIL import Image, ImageOps

imgDB = 'TestCases/McGill Calibrated Colour Image Database'
imgFiles = {}
for root, dirs, files in os.walk(imgDB):
    for subdir in dirs:
        imgFiles[subdir] = [os.path.join(root, subdir, f) for f in os.listdir(os.path.join(root, subdir))]
pass # for - for

def MyTestSet(number=10, size=50, debug=False):
    '''
    Create a random test set from the original image database
    @param number: {Integer} (Optional) number of subsets in the test set. Default to 10
    @param size:   {Integer} (Optional) number of test cases per subset. Default to 50
    @param debug: {Boolean} (Optinal) True to display debugging information; False not
    '''
    allFiles = []
    for files in imgFiles.values():
        allFiles += files[:]

    for i in range(number):
        if debug:
            print 'Creating Test Set %02d:' % (i+1),
        pass # if debug
        if os.path.isdir('TestCases/ImgSet%02d' % (i+1)):
            shutil.rmtree('TestCases/ImgSet%02d' % (i+1))
        os.makedirs('TestCases/ImgSet%02d' % (i+1))

        for j in range(size):
            if debug and j != 0 and j % 5 == 0:
                print '.',
            pass # if debug and j != 0 and j % 5 == 0
            random.shuffle(allFiles)
            shutil.copyfile(allFiles[-1],
                            os.path.join('TestCases/ImgSet%02d' % (i+1), re.split(r'[/|\\]', allFiles[-1])[-1]))
            allFiles = allFiles[:-1]
        pass # for j in range(size)
        if debug:
            print 'done'
        pass # if debug
    pass # for i in range(number)
pass # def MyTestSet(number=10, size=50, debug=False)

def openImageFromSubset(subset):
    '''
    Open a subset, return the paths and "Image" object of all image files
    '''
    imgs = os.listdir(subset)
    index = 0
    while index < len(imgs):
        if not imgs[index].endswith('.tif'):
            imgs.pop(index)
            index -= 1
        else:
            imgs[index] = os.path.join(subset, imgs[index])
        index += 1
    pass # while index < len(imgs)
    imgs = natsort.natsorted(imgs)
    imgs.sort()
    return [(img, Image.open(img)) for img in imgs]
pass # def openImageFromSubset(subset)

def calcMSE(imageA, imageB):
    '''
    Mean Squared Error:
    https://en.wikipedia.org/wiki/Mean_squared_error

    Reference:
    http://scikit-image.org/docs/dev/auto_examples/plot_ssim.html
    '''
    img1 = ImageOps.grayscale(imageA.copy())
    img2 = ImageOps.grayscale(imageB.copy())
    width, height = max(img1.size[0], img2.size[0]), max(img1.size[1], img2.size[1])
    if (width, height) != img1.size:
        img1 = img1.resize((width, height))
    if (width, height) != img2.size:
        img2 = img2.resize((width, height))
    return numpy.linalg.norm(img_as_float(img1) - img_as_float(img2))
pass # def calcMSE(imageA, imageB)

def calcPSNR(imageA, imageB):
    '''
    Peak signal-to-noise ratio:
    https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio

    Reference -- psnr:
    https://github.com/aizvorski/video-quality/blob/master/psnr.py
    '''
    vMSE = calcMSE(imageA, imageB)
    if vMSE == 0:
        return 100
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(vMSE))
pass # def calcPSNR(imageA, imageB)

def calcSSIM(imageA, imageB):
    '''
    Structural Similarity Measure:
    [1] Z. Wang, A. C. Bovik, H. R. Sheikh and E. P. Simoncelli. Image quality assessment: From error visibility to
        structural similarity. IEEE Transactions on Image Processing, 13(4):600--612, 2004. 
    [2] Z. Wang and A. C. Bovik. Mean squared error: Love it or leave it? - A new look at signal fidelity measures.
        IEEE Signal Processing Magazine, 26(1):98--117, 2009.

    Reference -- ssim:
    http://scikit-image.org/docs/dev/auto_examples/plot_ssim.html
    '''
    img1 = ImageOps.grayscale(imageA.copy())
    img2 = ImageOps.grayscale(imageB.copy())
    width, height = max(img1.size[0], img2.size[0]), max(img1.size[1], img2.size[1])
    if (width, height) != img1.size:
        img1 = img1.resize((width, height))
    if (width, height) != img2.size:
        img2 = img2.resize((width, height))
    return ssim(img_as_float(img1), img_as_float(img2))
pass # def calcSSIM(imageA, imageB)

def calcNCD():
    '''
    DO NOTHING HERE!
    python3 ncds.py ImgSet01/*.tif > ncd-01.txt

    Reference: https://github.com/DavyLandman/ncd
    '''
pass # def calcNCD()

def resultsCollecting(number=10):
    files = set()
    records = {}
    for i in range(number):
        f = open('TestCases/ImageComparison/mse-results%02d.txt' % (i+1), 'r')
        for line in f:
            cols = line.strip().split('\t')
            files.add(cols[2][5:])
            files.add(cols[3][5:])
            records[(cols[2][5:], cols[3][5:])] = {'mse': float(cols[-1][4:])}
        pass # for line in f
        f.close()
        f = open('TestCases/ImageComparison/psnr-results%02d.txt' % (i+1), 'r')
        for line in f:
            cols = line.strip().split('\t')
            files.add(cols[2][5:])
            files.add(cols[3][5:])
            records[(cols[2][5:], cols[3][5:])]['psnr'] = float(cols[-1][5:])
        pass # for line in f
        f.close()
        f = open('TestCases/ImageComparison/ssim-results%02d.txt' % (i+1), 'r')
        for line in f:
            cols = line.strip().split('\t')
            files.add(cols[2][5:])
            files.add(cols[3][5:])
            records[(cols[2][5:], cols[3][5:])]['ssim'] = float(cols[-1][5:])
        pass # for line in f
        f.close()
        f = open('TestCases/ImageComparison/ncd-results%02d.txt' % (i+1), 'r')
        for line in f:
            cols = line.strip().split('\t')
            files.add(cols[2][5:])
            files.add(cols[3][5:])
            records[(cols[2][5:], cols[3][5:])]['ncd'] = float(cols[-1][4:])
        pass # for line in f
        f.close()
    pass # for i in range(number)

    results = []
    for k1, k2 in records.keys():
        if k1.split()[0] == k2.split()[0]:
            results = [(k1, k2, records[(k1, k2)])] + results
        else:
            results.append((k1, k2, records[(k1, k2)]))
    pass # for k1, k2 in records.keys()

    f = open('TestCases/ImageComparison.log', 'w')
    f.write('Image 1\tImage 2\tNCD\tSSIM\tPSNR\tMSE\n')
    for r in results:
        f.write('%s\t%s\t%.4f\t%.4f\t%.4f\t%.4f\n' % (r[0], r[1], r[2]['ncd'], r[2]['ssim'], r[2]['psnr'], r[2]['mse']))
    f.close()
pass # def resultsCollecting(number=10)


if __name__ == '__main__':
    numSubsets = 10
    createTestSet = not True
    calculation = not True
    collection = True

    if createTestSet:
        MyTestSet(number=numSubsets, debug=True)

    if calculation:
        for i in range(numSubsets):
            imgs = openImageFromSubset(os.path.join('TestCases', 'ImgSet%02d' % (i + 1)))
            f = open(os.path.join('TestCases', 'ssim-results%02d.txt' % (i+1)), 'w')
            f.close()
            f = open(os.path.join('TestCases', 'mse-results%02d.txt' % (i+1)), 'w')
            f.close()
            f = open(os.path.join('TestCases', 'psnr-results%02d.txt' % (i+1)), 'w')
            f.close()
            idx, total = 1, len(imgs) * (len(imgs) - 1) / 2
            for x in range(len(imgs)):
                for y in range(x+1, len(imgs)):
                    path1, img1 = imgs[x]
                    path2, img2 = imgs[y]
                    print 'subset%02d: %d/%d %s %s' % (i+1, idx, total, path1, path2),
    
                    # Calculate MSE
                    t1 = datetime.datetime.now()
                    vMSE = calcMSE(img1, img2)
                    f = open(os.path.join('TestCases', 'mse-results%02d.txt' % (i+1)), 'a')
                    strMSE = 'None' if vMSE is None else '%.4f' % vMSE
                    f.write('i=%03d\tj=%03d\timg1=%-28s\timg2=%-28s\tmse=%s\n' % \
                            (x, y, path1, path2, strMSE))
                    f.close()
                    t2 = datetime.datetime.now()
                    print 'MSE=%.4f; time=%s' % (vMSE, t2 - t1),
    
                    # Calculate MSE
                    t1 = datetime.datetime.now()
                    vPSNR = calcPSNR(img1, img2)
                    f = open(os.path.join('TestCases', 'psnr-results%02d.txt' % (i+1)), 'a')
                    strPSNR = 'None' if vPSNR is None else '%.4f' % vPSNR
                    f.write('i=%03d\tj=%03d\timg1=%-28s\timg2=%-28s\tpsnr=%s\n' % \
                            (x, y, path1, path2, strPSNR))
                    f.close()
                    t2 = datetime.datetime.now()
                    print 'PSNR=%.4f; time=%s' % (vPSNR, t2 - t1),
    
                    # Calculate SSIM
                    t1 = datetime.datetime.now()
                    vSSIM = calcSSIM(img1, img2)
                    f = open(os.path.join('TestCases', 'ssim-results%02d.txt' % (i+1)), 'a')
                    strSSIM = 'None' if vSSIM is None else '%.4f' % vSSIM
                    f.write('i=%03d\tj=%03d\timg1=%-28s\timg2=%-28s\tssim=%s\n' % \
                            (x, y, path1, path2, strSSIM))
                    f.close()
                    t2 = datetime.datetime.now()
                    print 'SSIM=%.4f; time=%s' % (vSSIM, t2 - t1)
    
                    idx += 1
            pass # for - for
        pass # for i in range(numSubsets)
    pass # if calculation

    if collection:
        resultsCollecting(numSubsets)
pass # if __name__ == '__main__'
