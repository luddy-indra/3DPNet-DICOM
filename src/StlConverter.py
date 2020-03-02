import numpy as np                   # fundamental package for scientific computing
import dicom                         # python package for working with DICOM
import os                            # provides a way of using operatint system dependent functionality
import matplotlib.pyplot as plt      # plotting library for the python
import shutil
from stl import mesh
from zipfile import ZipFile
from glob import glob 
from pathlib import Path             # classes representing filesystem paths
from glob import glob                # finds  all the pathnames matching a specified pattern according the rules
from mpl_toolkits.mplot3d.art3d import Poly3DCollection      #provides some basic 3D plotting tools
#import scipy.ndimage                 # the standart deviation of the gaussian filter are given for each axis
from scipy.ndimage import gaussian_filter
from skimage import morphology       # morphological image processing
from skimage import measure          # measure image region properties image
from skimage.transform import resize # specify an output image shape 
from plotly import __version__       # plotly version check
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot  # interactive plotly graphs to the offline environment
from plotly.tools import FigureFactory as FF                 # API contains a figure factory
from plotly.graph_objs import *                              # data visualization toolbox

class StlConverter:
    def __init__(self):
        #super(self).__init__()
        self.PATH_HZIP = '/home/jupyter-luddy/Luddy_Projec/data/history_zip/'
        self.PATH_HSTL = '/home/jupyter-luddy/Luddy_Project/data/history_stl/'
        #self.PATH_HGCODE = '/home/jupyter-luddy/Luddy_Project/data/history_gcode/'
        self.PATH_TZIP = '/home/jupyter-luddy/Luddy_Project/data/temporary_zip/'
        self.PATH_TSTL = '/home/jupyter-luddy/Luddy_Project/data/temporary_stl/'
        #self.PATH_TGCODE = '/home/jupyter-luddy/Luddy_Project/data/temporary_gcode/'
        self.PATH_T3D = '/home/jupyter-luddy/Luddy_Project/data/temporary_3d_images/'
  
    def convert_to_stl(self, filename):
        print(filename)
        pos_slash = filename.rfind('/')
        ext = filename.rfind('.')
        file = str(filename)[pos_slash+1:ext]
        print(file)
        pos_under = file.find('_')
        ori_filename = str(file)[pos_under+1:]
        print(ori_filename)
        with ZipFile(filename, 'r') as zips: 
            zips.extractall(self.PATH_TZIP)
        data_folder = os.path.join(str(self.PATH_TZIP), ori_filename)
        print(data_folder)
        av, af = self.make_mesh(self.resample_image(data_folder,data_folder), 226, 3)
        file_stl = self.save_stl(av, af)
        return file_stl
    
    def load_scan(self, path):
        print(path)
        slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
        slices.sort(key = lambda x: int(x.InstanceNumber))
        try:
            slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
        except:
            slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
            
        for s in slices:
            s.SliceThickness = slice_thickness
       
        return slices
    
    def get_pixels_hu(self, scans):
        image = np.stack([s.pixel_array for s in scans])
        image = image.astype(np.int16)
        image[image == 400] = 0
        
        #Convert to Hounsfield units (HU)
        intercept = scans[0].RescaleIntercept
        slope = scans[0].RescaleSlope
        
        if slope != 1:
            image = slope * image.astype(np.float64)
            image = image.astype(np.int16)
            
        image += np.int16(intercept)
        
        return np.array(image, dtype=np.int16)
        
    def resample_image(self, path,output_path):
        id=0
        
        patient = self.load_scan(path)
        imgs = self.get_pixels_hu(patient)
        
        np.save(output_path + "fullimages_%d.npy" % (id), imgs)
        imgs_to_process = np.load(output_path+'fullimages_{}.npy'.format(id))

        imgs_after_resamp = gaussian_filter(imgs_to_process, 2)
        return imgs_after_resamp

    def make_mesh(self, image, threshold=-300, step_size=1):
        # Original cobe by Howard Chen, from Radiology Data Quest,
        # accesed at http://www.raddq.com/dicom-processing-segmentation-visulation-in-python/
        #print("Transposing surface")
        p = image.transpose(2,1,0)  
        
        #print("Calculating surface")
        verts, faces, norm, val = measure.marching_cubes_lewiner(p, threshold, step_size=step_size, allow_degenerate=True) 
        # to find surface in 3D volumetric data
        return verts, faces
        
    def save_stl(self, av,af):
        cube = mesh.Mesh(np.zeros(af.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(af):
            for j in range(3):
                cube.vectors[i][j] = av[f[j],:]
        return cube
