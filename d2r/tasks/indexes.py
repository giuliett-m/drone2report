import os
import pathlib
import importlib
import numpy as np
import pandas as pd
from tqdm import tqdm

from d2r.task import Task
import d2r.misc
import d2r.tasks.matrix_returning_indexes as mri
import d2r.tasks.array_returning_indexes  as ari

class indexes(Task):
	def run(self, dataset):
		#the output path
		(ortho, shapes) = dataset.get_files()
		(ortho, ext) = d2r.misc.get_file_corename_ext(ortho)
		outfile = os.path.join(self.config['outfolder'], 'indexes_' + dataset.get_title() + '_' + ortho + '.csv')
		path = pathlib.Path(self.config['outfolder'])
		path.mkdir(parents=True, exist_ok=True)		

		#check if we should do the task or not
		if os.path.isfile(outfile) and self.config['skip_if_already_done']:
			print('skipping. Output file already exists: ' + outfile)
			return(None)

		#room for results
		df = None
		
		#the index list
		index_names = self.config['indexes'].replace(" ", "").split(',')
		
		#the field that is used to index geometries in the shape file
		field = dataset.get_geom_index()
		
		#for each shape in the dataset
		for i in tqdm(dataset.get_geom_field(field)):
			rb = dataset.get_geom_raster(polygon_field=field, polygon_id=i)
			
			#if rb is None it means that we have asked for data outside the image
			if rb is not None:
				#starting to build the saved dict
				(ortho, shapes) = dataset.get_files()
				d = {
					'type' : dataset.get_type(), 
					'dataset' : dataset.get_title(),
					'ortho_file' : ortho, 
					'shapes_file' : shapes,
					field : [i]
				}

				#for each required index
				for current_index in index_names:
					#if it's a matrix-returning index, we are going to compute it and
					#then store some general statistics
					if hasattr(mri, current_index):
						current_index_function = getattr(mri, current_index)
						myindex = current_index_function(rb, dataset.get_channels())
						d[current_index + '_mean'] = np.mean(myindex)
						d[current_index + '_max'] = np.max(myindex)
						d[current_index + '_min'] = np.min(myindex)
					
					#if it's an array-returning index, we are going to compute 
					#it and then just store the info
					if hasattr(ari, current_index):
						current_index_function = getattr(ari, current_index)
						d.update(current_index_function(rb, dataset.get_channels()))
					
				#storing the results
				df = pd.concat([df, pd.DataFrame.from_dict(d)])
		
		#saving the results
		df.to_csv(outfile, index=False)
		
	def parse_config(self, config):
		"""parsing index-specific config parameters"""
		res = super().parse_config(config)
		#no specific parsing required so far
		return(res)


