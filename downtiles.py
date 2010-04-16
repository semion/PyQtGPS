import sys, re, globalmaptiles

def Usage(s = ""):
	print "Usage: globalmaptiles.py [-profile 'mercator'|'geodetic'] zoomlevel lat lon [latmax lonmax]"
	print
	if s:
		print s
		print
	print "This utility prints for given WGS84 lat/lon coordinates (or bounding box) the list of tiles"
	print "covering specified area. Tiles are in the given 'profile' (default is Google Maps 'mercator')"
	print "and in the given pyramid 'zoomlevel'."
	print "For each tile several information is printed including bonding box in EPSG:900913 and WGS84."
	sys.exit(1)

profile = 'mercator'
zoomlevel = None
lat, lon, latmax, lonmax = None, None, None, None
boundingbox = False

argv = sys.argv
i = 1
while i < len(argv):
	arg = argv[i]

	if arg == '-profile':
		i = i + 1
		profile = argv[i]
	
	if zoomlevel is None:
		zoomlevel = int(argv[i])
	elif lat is None:
		lat = float(argv[i])
	elif lon is None:
		lon = float(argv[i])
	elif latmax is None:
		latmax = float(argv[i])
	elif lonmax is None:
		lonmax = float(argv[i])
	else:
		Usage("ERROR: Too many parameters")

	i = i + 1

if profile != 'mercator':
	Usage("ERROR: Sorry, given profile is not implemented yet.")

if zoomlevel == None or lat == None or lon == None:
	Usage("ERROR: Specify at least 'zoomlevel', 'lat' and 'lon'.")
if latmax is not None and lonmax is None:
	Usage("ERROR: Both 'latmax' and 'lonmax' must be given.")

if latmax != None and lonmax != None:
	if latmax < lat:
		Usage("ERROR: 'latmax' must be bigger then 'lat'")
	if lonmax < lon:
		Usage("ERROR: 'lonmax' must be bigger then 'lon'")
	boundingbox = (lon, lat, lonmax, latmax)

tz = zoomlevel
mercator = globalmaptiles.GlobalMercator()
mx, my = mercator.LatLonToMeters( lat, lon )
tminx, tminy = mercator.MetersToTile( mx, my, tz )

if boundingbox:
	mx, my = mercator.LatLonToMeters( latmax, lonmax )
	tmaxx, tmaxy = mercator.MetersToTile( mx, my, tz )
else:
	tmaxx, tmaxy = tminx, tminy

f = open("tiles.html", "w")
f.write("<html><head></head><body>\n")
mt = 0
	
for ty in range(tminy, tmaxy+1):
	for tx in range(tminx, tmaxx+1):	
		gx, gy = mercator.GoogleTile(tx, ty, tz)
		text = '<a href="http://mt%i.google.com/mt/v=w2.92&hl=en&x=%i&y=%i&z=%i&s=">%i_%i_%i.png</a>\n' % (mt%4, gx, gy, tz, tz, gx, gy)
		mt += 1
		f.write(text)
f.write("</body></html>")
f.close()