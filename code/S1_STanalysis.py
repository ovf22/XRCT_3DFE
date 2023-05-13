import nibabel as nib
import numpy as np
import os

from structure_tensor import eig_special_3d, structure_tensor_3d

import M1_TomoHandling as M1TH
import M2_Alignment as M2A



#%%  File names and directory
# If you are running the script from a python editor like Spyder, then change
# the sample name to the name of your data set
sample_name = 'shell_sample_name'
file_name = sample_name + '.nii'

data_path = '../data'
result_path = '../results/'+sample_name+'_files/figures/'

data_file_path = os.path.join(data_path, file_name)

# Assign sample material coordinate system [x, y, z] = [length, thickness, width]
sample_coor_axis = [1, 2, 0]

#%% Load NIfTI data.
nii_file = nib.load(data_file_path)
data_full =np.array(nii_file.dataobj[slice(None),slice(None),slice(None)])
    

# Change the tomogram coordinate system to the material coordinate system
data_full = np.moveaxis(data_full, [0, 1, 2], sample_coor_axis)  

# Crop data
crop_edge = shell_crop
data = M1TH.tomo_crop(data_full, xcut=crop_edge, ycut=crop_edge, zcut=crop_edge)
    
# Read meta data.
data_shape = data.shape
data_type = nii_file.get_data_dtype()
VOXEL_SIZE = nii_file.affine[0, 0]

# Set known fiber diameter in micro meters.
FIBER_DIAMETER = 7

# %% Plot all planes
M1TH.tomo_plot_3(data,
                x_slice=int(data_shape[0]/2),
                y_slice=int(data_shape[1]/2),
                z_slice=int(data_shape[2]/2), 
                figsize=(12,10),
                fig_name=sample_name+'_Tomo_fig',
                fig_path=result_path)

# %% Calculate ST -> S
# Jeppesen2021
rho = FIBER_DIAMETER / VOXEL_SIZE
rho = round(rho, 2)
sigma = rho / 2


# %% In[11]: Structure tensor analysis
# Copy volume and cast it to 64-bit floating point.
data_f = data.astype(np.float64)

# Calculate S.
S = structure_tensor_3d(data_f, sigma, rho)

truncate = 4 
kernel_radius = int(max(sigma, rho) * truncate + 0.5)
print('kernel_radius:', kernel_radius)

S = S[:, kernel_radius:-kernel_radius, 
      kernel_radius:-kernel_radius, 
      kernel_radius:-kernel_radius]
S.shape

data_s = data_f[kernel_radius:-kernel_radius,
                kernel_radius:-kernel_radius,
                kernel_radius:-kernel_radius]
# Clear some memory.
del data_f

# %%
val, vec = eig_special_3d(S, full=False) # 3D

del S
val = val.astype(np.float32)
vec = vec.astype(np.float32)

# Smallest eigenvalue corresponds to predominant direction i.e., fiber direction.
# Eigenvectors are returned as vec=[z,y,x], this is flipped back to vec=[x,y,z]
vec = np.flip(vec, axis=[0])

# Eigenvectors desribe the dominant material orientation. This is not a unique 
# direction as an opposite vector share the same orientation as the eigenvector.
# This will cause a noise appearance in the visualization of material orientations.
# All eigenvectors are thus multiplied with the sign og the x-component to align
# the vectors in the positive x-direction.
vec_r = vec * np.sign(vec[0])

# %% Calculate orientations
# Calculate fiber mialignment (Azimuth and elevation angles)
theta, phi = M2A.st_misalign(vec_r)

# The global fiber orientation may not be aligned with the global material 
# coordinate system. All eigenvectors may thus be rotated to a new reference axis.
# Rotate all vectors to reference axis 
vec_new = M2A.orient_average(vec_r)

# Calculate fiber mialignment for new reference axis (Azimuth and elevation angles)
theta_new, phi_new = M2A.st_misalign(vec_new)

# - Histogram of orientation before and after correcting global alignment
M2A.plot_hist(phi, phi_new, limits=5, bins=360, alpha=0.5,
              fig_name=sample_name+'_Misalignment_hist' , fig_path=result_path)

# %% - Overlay plot of fiber misalignment
SI = 50  # Slice of interest
M2A.fig_with_colorbar(
    data_s[:, :, SI].T,
    phi_new[:, :, SI].T,
    'Fiber misalignment relative to global fiber direction',
    cmap='coolwarm',
    alpha=0.5,
    vmin=-10,
    vmax=10,
    fig_name=sample_name+'_Fiber_misalignment_overlay',
    fig_path=result_path)

# %% FE-Model dimensions
PADDING = 2*70
L_MODEL = len(data_s[:,0,0])*VOXEL_SIZE + 2 * PADDING
T_MODEL = len(data_s[0,:,0])*VOXEL_SIZE
W_MODEL = len(data_s[0,0,:])*VOXEL_SIZE 
   
MODEL_DIM = [L_MODEL, T_MODEL, W_MODEL]
MODEL_DIM_FILE = sample_name+'_TomoDim.txt'
# Save model dimensions to file. The file is used in S2_Cube.py
np.savetxt(MODEL_DIM_FILE, MODEL_DIM, delimiter=';')


# %% Save variables and constants for mapping orientations to integration 
# Variables for S3_mapping.py
np.savez(sample_name+'_MAP_VAR.npz', VOXEL_SIZE=VOXEL_SIZE, 
         MODEL_DIM=MODEL_DIM, phi=phi_new, theta=theta_new)