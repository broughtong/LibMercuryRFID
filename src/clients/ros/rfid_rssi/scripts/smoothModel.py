from scipy import ndimage
import numpy
import pickle

model = pickle.load(open("models/3000.p", "rb"))

model = [model[0]]

print model

for i in model:
	w = i[2].info.width
	h = i[2].info.height

	avr = numpy.array(i[3]).reshape(w, h).astype(float)
	avrFilt = ndimage.filters.gaussian_filter(avr, sigma=0.45, mode = 'reflect')

	#todo save back to model structure(i[2])
	print model


#save corrected model
fname = "models/3000.p"
pickle.dump(model, open(fname, "wb"))
