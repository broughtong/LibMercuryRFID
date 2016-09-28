#todo
#model[0] needs to contain size/res
#new constructors and functions
#model generic naming changed
import pickle, math

class SpatioModel():

	def __init__(self, fileName, onlyGeneric=False, defaultToGeneric=True):

		#Use exclusively the generic sensor model (for comparison purposes)
		self.onlyGeneric = onlyGeneric
		#Use the generic sensor model if a particular frequency doesn't have any data
		self.defaultToGeneric = defaultToGeneric

		self.model = pickle.load(open(fileName, "rb"))
		self.gridSize = self.model[0][6]
		self.gridResolution = self.model[0][7]

		if self.gridSize % self.gridResolution > 0.001:
			print "Error: Sensor model size/resolution do not match"
	
	def getProbability(self, x, y, rssiDB, freqKHz="generic"):

		#x,y in robot frame of reference

		if x > self.gridSize or y > self.gridSize or x < -self.gridSize or y < -self.gridSize:
			print "Warning: Position outside of sensor mode, consider creating a larger sensor model"
			return pow(10, -99)

		roundedx = x - (x % self.gridResolution)
		roundedy = y - (y % self.gridResolution)

		indexx = roundedx / self.gridResolution
		indexy = roundedy / self.gridResolution

		offsetx = indexx + (self.gridSize / self.gridResolution)
		offsety = indexy + (self.gridSize / self.gridResolution)

		index = int(((self.gridSize / self.gridResolution) * 2 * offsety) + offsetx)

		modelRSSI = None
		modelSTD = None

		for i in self.model:
			if i[1] == freqKHz:

				if self.onlyGeneric == True:
					if self.model[0][4][index] == None:
						return pow(10, -99)
					else:
						modelRSSI = self.model[0][4][index]
						modelSTD = self.model[0][5][index]
				else:
					if i[4][index] == None:
						if self.defaultToGeneric == True:
							if self.model[0][4][index] == None:
								return pow(10, -99)
							else:
								modelRSSI = self.model[0][4][index]
								modelSTD = self.model[0][5][index]
						else:
							return pow(10, -99)
					else:
						modelRSSI = i[4][index]
						modelSTD = i[5][index]

		rssiDifference = rssiDB - modelRSSI

		probability = math.exp(-math.pow(rssiDifference, 2) / (2 * modelSTD * modelSTD)) / (modelSTD * math.sqrt(2 * math.pi))

		return probability
