'''
Created on Jan 11, 2016

@author: MarcoXZh
'''
import math, requests, re, sqlite3
from urlparse import urlparse
from lxml import html

def AlexaGlobalTopSites(num=500, debug=True):
    '''
    Retrieve global top sites from Alexa (http://www.alexa.com/topsites)
    @param num:   {Integer} number of top sites, default is all (500)
    @param debug: {Boolean} True to display debugging information; False not
    '''
    topSites = []
    finished = False
    pageIndex = 0
    while pageIndex < 20:
        url = 'http://www.alexa.com/topsites/global;%d' % pageIndex
        if debug:
            print 'Crawling Alexa page %d/%d: %s' % (pageIndex+1, math.ceil(num/25.0), url)
        try:
            links = html.fromstring(requests.request('GET', url, timeout=5).text) \
                        .xpath('//p[@class=\"desc-paragraph\"]/a/text()')
        except:
            pass
        pass # try - except
        for link in links:
            link = link.lower()
            if len(topSites) >= num:
                finished = True
                break
            pass # if len(topSites) >= num
            topsite = {'host':link, 'url':''}
            try:
                if debug:
                    print '  Crawling top site: %d/%d: %-30s...' % (len(topSites)+1, num, link), 
                topsite['url'] = requests.request('GET', 'http://' + link, timeout=10).url
                if debug:
                    print ('done: %s' % topsite['url'])
            except:
                if debug:
                    print 'exception!!'
            pass # try - except
            topSites.append(topsite)
        pass # for link in links
        if finished:
            break
        pageIndex += 1
    pass # while pageIndex < 20

    if debug:
        print 'Output the results'
    f = open('TestCases/topsites.txt', 'w')
    for i, topsite in enumerate(topSites):
        if debug:
            print i, topsite
        f.write('%3d\t%-30s\t%s\n' % (i+1, topsite['host'], topsite['url']))
    pass # for i, topsite in enumerate(topSites)
    f.close()
pass # def AlexaGlobalTopSites(num=500, debug=True)

def crawTopWebsites(debug=True):
    '''
    Crawl the top sites and save results
    @param debug: {Boolean} True to display debugging information; False not
    '''
    sites = []
    f = open('TestCases/topsites160111.txt', 'r')
    for line in f:
        cols = re.split('\\s+', line.strip())
        if len(cols) == 3:
            sites.append(cols[1:3])
    pass # for line in f
    f.close()
    f = open('TestCases/LinkPool.txt', 'w')
    f.close()
    for i, site in enumerate(sites):
        if debug:
            print 'Crawling %3d/%3d: %s' % (i+1, len(sites), site[-1])
        links = []
        try:
            links = html.fromstring(requests.request('GET', site[-1].strip(), timeout=10).text).xpath('//a/@href')
        except:
            pass
        pass # try - except
        if debug:
            print ('  all links: %d' % len(links)),
        activeLinks = set()
        for link in links:
            if link is None or link.strip() == '':
                continue
            href = link.strip()
            if href.startswith('/'):
                host = urlparse(site[-1])
                href = '%s://%s%s' % (host.scheme, host.netloc, href)
            pass # if href.startswith('/')
            if '#' in href:
                href = href[:href.index('#')]
            activeLinks.add(href)
        pass # for link in links
        activeLinks = list(activeLinks)
        if debug:
            print ('active links: %d' % len(activeLinks)),
        f = open('TestCases/LinkPool.txt', 'ab')
        for link in activeLinks:
            f.write((link + '\n').encode('UTF-8'))
        f.close()
        if debug:
            print 'done'
    pass # for i, site in enumerate(sites)
pass # def crawTopWebsites(debug=True)

def saveSqliteDatabase(debug=False):
    '''
    Save crawling results to SQLite database
    @param debug: {Boolean} True to display debugging information; False not
    '''
    conn = sqlite3.connect('TestCases/WebPages.db')
    c = conn.cursor()

    # Step 1: save top sites
    c.execute('DROP TABLE IF EXISTS pages_160111;')
    c.execute('CREATE TABLE pages_160111 (idx int primary key, host text, url text, valid int);')
    lines = []
    f = open('TestCases/topsites160111.txt', 'r')
    for line in f:
        cols = re.split('\\s+', line.strip())
        lines.append((int(cols[0]),                             # idx, int, primary key
                      cols[1],                                  # host, text
                      cols[2] if len(cols) > 2 else 'None',     # url, text
                      1 if len(cols) == 3 else 0 ))             # valid, int (boolean)
    pass # for line in f
    f.close()
    c.executemany('INSERT INTO pages_160111 VALUES (?, ?, ?, ?)', lines)
    conn.commit()

    # Step 2: save crawling results
    c.execute('DROP TABLE IF EXISTS pages_160114;')
    c.execute('CREATE TABLE pages_160114 (idx int primary key, url text);')
    lines = set()
    f = open('TestCases/LinkPool.txt', 'r')
    for line in f:
        try:
            x = line.strip().encode('ASCII', 'replace')
            if x != '':
                lines.add(x)
        except:
            pass
        pass # try - except
    pass # for line in f
    f.close()
    lines = list(lines)
    for i in range(len(lines)):
        lines[i] = (i+1, lines[i])
    c.executemany('INSERT INTO pages_160114 VALUES (?, ?)', lines)
    conn.commit()

    # Step 3: save crawling logs
    c.execute('DROP TABLE IF EXISTS crawl_log;')
    c.execute('CREATE TABLE crawl_log (idx int primary key, url text, link_all int, link_active);')
    lines = []
    f = open('TestCases/CrawlingLogs.txt', 'r')
    idxLine = 0
    lines, record = [], {}
    for line in f:
        idxLine += 1
        if idxLine % 2 == 1:
            assert '/469: ' in line
            cols = line.strip().split('/469: ')
            assert len(cols) == 2
            record['idx'] = int(re.split('\\s+', cols[0])[-1])
            record['url'] = cols[1].strip()
        else:
            cols = re.split('\\s+', line.strip())
            assert len(cols) == 7
            record['all'] = int(cols[2])
            record['active'] = int(cols[5])
            lines.append(record)
            record = {}
        pass # else - if idxLine % 2 == 1
    pass # for line in f
    f.close()
    lines = [(line['idx'], line['url'], line['all'], line['active']) for line in lines]
    c.executemany('INSERT INTO crawl_log VALUES (?, ?, ?, ?)', lines)
    conn.commit()

    conn.close()
pass # def saveSqliteDatabase(debug=False)


if __name__ == '__main__':
#     AlexaGlobalTopSites(500)
#     crawTopWebsites()
    '''
    SQLite usage:
    .open WebPages.db
    .tables
    .schema pages_160111
    .schema pages_160114
    .schema crawl_log
    .mode column
    .header on
    SELECT * FROM pares_160111;
    SELECT count(*) FROM pares_160111;
    .exit
    '''
    saveSqliteDatabase()
pass # if __name__ == '__main__'
