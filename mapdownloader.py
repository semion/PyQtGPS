#!/usr/bin/python
# -*- coding: UTF-8 -*-


from globalmaptiles import GlobalMercator
from threading import Thread
import urllib2, os, random, Queue

MAX_THREADS = 4

class Downloader(object):
    '''
    Based on http://www.wellho.net/solutions/python-python-threads-a-first-example.html
    '''
    
    def __init__(self, mapdir, minzoom, maxzoom):
        self.mercator = GlobalMercator(256)
        self.minzoom = minzoom
        self.maxzoom = maxzoom
        self.TopRightLat = None
        self.TopRightLon = None
        self.BottomLeftLat = None
        self.BottomLeftLon = None
        self.mminx = None
        self.mminy = None
        self.mmaxx = None
        self.mmaxy = None
        self.mapdir = mapdir
        self.jobs = Queue.Queue()       
        
    def download(self, toprightlat, toprightlon, bottomleftlat, bottomleftlon):
        self.TopRightLat = toprightlat
        self.TopRightLon = toprightlon
        self.BottomLeftLat = bottomleftlat
        self.BottomLeftLon = bottomleftlon        
        self.mminx, self.mminy = self.mercator.LatLonToMeters(toprightlat, toprightlon)
        self.mmaxx, self.mmaxy = self.mercator.LatLonToMeters(bottomleftlat, bottomleftlon)
        
        map(self.addJobForZoom, range(self.minzoom, self.maxzoom+1))
        
        self.runJobs()
        
    def addJobForZoom(self, zoom):
        tminx, tminy = self.mercator.MetersToTile(self.mminx, self.mminy, zoom)
        tmaxx, tmaxy = self.mercator.MetersToTile(self.mmaxx, self.mmaxy, zoom)
        
        if tminx > tmaxx:
            tminx, tmaxx = tmaxx, tminx
        if tminy > tmaxy:
            tminy, tmaxy = tmaxy, tminy
        
        for tx in range(tminx, tmaxx+1):
            for ty in range(tminy, tmaxy+1):
                gx, gy = self.mercator.GoogleTile(tx, ty, zoom)
                self.jobs.put({'x':gx, 'y':gy, 'z':zoom})        
                
    def runJobs(self):
        workers = []
        for threadNum in range(0, MAX_THREADS):
            subdownloader = self.SubDownloader(self)
            workers.append(subdownloader)
            workers[-1].start()
        
        for worker in workers:
            worker.join(20)
                    
        print "Finished!"
        
    class SubDownloader(Thread):
        def __init__ (self, parent):
            Thread.__init__(self)
            self.parent = parent
            
        def run(self):
            while 1:
                try:
                    job = self.parent.jobs.get(0)
                except Queue.Empty:
                    return
                mt = random.randrange(0,4)
                filename = '%i/gm_%i_%i_%i.png' % (job['z'], job['x'], job['y'], job['z'])
                if os.path.isfile('%s%s' % (self.parent.mapdir, filename)):
#                    print "skippnig", filename, "left:", self.parent.jobs.qsize()
                    continue
                if not os.path.isdir('%s%s' % (self.parent.mapdir, job['z'])):
                    os.mkdir('%s%s' % (self.parent.mapdir, job['z']))
#                http://mt1.google.com/vt/lyrs=m@115&hl=en&x=39141&s=&y=26445&z=16&s=Gali
                url = 'http://mt%i.google.com/vt/lyrs=m@115&hl=en&x=%i&y=%i&z=%i&s=' % (mt, job['x'], job['y'], job['z'])
                try:
                    tile = urllib2.urlopen(url=url, timeout=20).read()
                except:
#                    print "Can't open", url, "left:", self.parent.jobs.qsize()
                    continue               
                fh = open(filename, 'wb')
                fh.write(tile)
                fh.close()
#                print filename, "done, left:", self.parent.jobs.qsize()
                
                
if __name__ == '__main__':
    dl = Downloader("./", 15, 17)
    dl.download(32.797940, 35.100499, 32.915653, 35.112256)
    
    
                