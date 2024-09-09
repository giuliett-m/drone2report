#This module implements .ini config file parsing, plus several data transformation and
#validation. The core function is read_config(), which requires the .ini infile and
#returns a two (or more) levels dictionary (not a configparser). First level keys are 
#the .ini sections, second level are values.  
#We use the same notation as configparser objects, in particular we refer to "interpolate"
#as the operation of tweaking data, e.g. typing (so that values are actually booleans, int
#and so forth). The main extra functionality injected is the possibility of having lists,
#which are not supported by configparser. When possible we use however configparser
#native interpolation/validation mechanisms

import configparser
import os
import pprint

from d2r.dataset import Dataset
from d2r.render import Render
from d2r.analysis import Analysis

def read_config(infile):
	'''
	Reads the config file in .ini format, parse some data so e.g. there's lists
	and not many keys, returns a dictionary
	'''
	
	#check if file exists
	if not os.path.exists(infile):
		msg = 'Config file does not exist: ' + infile
		raise FileNotFoundError(msg)
	
	#instantiate a configparser object
	config = configparser.ConfigParser(interpolation = configparser.ExtendedInterpolation())
	config.read(infile)
	
	#prepare the output lists, first level of keys
	datasets = []
	analyses = []
	renders = []
	
	#loading everything
	for section in config.sections():
		#breaking up the section name, which should be "OPERATION qual1 <qual2>"
		pieces = section.split()
		if len(pieces) < 2 or len(pieces) > 3:
			msg = 'Bad section name: ' + section
			raise ValueError(msg)
		op = pieces[0]
		title = " ".join(pieces[1:])
		
		#each section is an instance of an object
		found = False
		if op == 'DATA':
			datasets.append(Dataset(title, config[section]))
			found = True
		if op == 'ANALYSIS':
			analyses.append(Analysis(title, config[section]))
			found = True
		if op == 'RENDER':
			renders.append(Render(title, config[section]))
			found = True
		if not found:
			raise ValueError('Bad section name: ' + op)
	return(datasets, analyses, renders)

 
def parse_channels(value):
	"""parses channels: comma separated string values, which will be forced to lowercase and removed of spaces"""
	return value.lower().replace(" ", "").split(',')
