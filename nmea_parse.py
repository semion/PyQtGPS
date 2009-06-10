class GPGGAParser(object):
	import logging
	
	def __init__(self, sentance):
		import time, logging
		
		logging.debug("GPPGAParser started")
		logging.debug("Trying to parse: "+sentance)
		(self.format,
		 self.utc,
		 self.latitude, 
		 self.northsouth, 
		 self.longitude, 
		 self.eastwest, 
		 self.quality, 
		 self.number_of_satellites_in_use, 
		 self.horizontal_dilution, 
		 self.altitude, 
		 self.above_sea_unit, 
		 self.geoidal_separation, 
		 self.geoidal_separation_unit, 
		 self.data_age, 
		 self.diff_ref_stationID) = sentance.split(",")

		latitude_in=float(self.latitude)
		longitude_in=float(self.longitude)
		if self.northsouth == 'S':
			latitude_in = -latitude_in
		if self.eastwest == 'W':
			longitude_in = -longitude_in

		latitude_degrees = int(latitude_in/100)
		latitude_minutes = latitude_in - latitude_degrees*100
		
		longitude_degrees = int(longitude_in/100)
		longitude_minutes = longitude_in - longitude_degrees*100
		
		self.latitude = latitude_degrees + (latitude_minutes/60)
		self.longitude = longitude_degrees + (longitude_minutes/60)
		
		self.timeOfFix = time.strftime("%H:%M:%S", time.strptime(self.utc.split(".")[0],"%H%M%S"))
		self.altitude = float(self.altitude)
		logging.debug("GPPGAParser finished")
