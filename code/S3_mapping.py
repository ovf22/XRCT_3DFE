import numpy as np
import pandas as pd
from scipy import ndimage

import M4_IntegrationPoints as M4IP

sample_name = 'shell_sample_name' 
MAP_VAR = np.load(sample_name+'_MAP_VAR.npz')
VOXEL_SIZE = MAP_VAR['VOXEL_SIZE'] 
MODEL_DIM = MAP_VAR['MODEL_DIM'] # Length, Thickness, Width
W_MODEL = MODEL_DIM[2]
phi = MAP_VAR['phi']
theta = MAP_VAR['theta']

result_path = '../results/shell_sample_name_files/figures/'

# %% Import integration points
with open(sample_name+'_IP2.dat', 'r', encoding='cp1257') as f:
    lines = f.readlines()

# Get start of integration point (IP) list.
# Get number of first line that contains...
start_ip = next(i for i, line in enumerate(lines) if 'THE FOLLOWING TABLE IS PRINTED AT THE INTEGRATION POINTS FOR ELEMENT TYPE' in line)
start_ip += 6  # Add offset.
# Find stop of IPs.
# Get the first line searching backwards that contains...
end_ip = len(lines) - next(i for i, line in enumerate(lines[::-1]) if 'THE ANALYSIS HAS BEEN COMPLETED' in line)
end_ip -= 3  # Subtract offset.

# Get IP lines.
ip_lines = lines[start_ip:end_ip]
# Create array with IPs.
ip_coords = np.array([l.split() for l in ip_lines], dtype=float)
ip_indices = ip_coords[:, :2].astype(int)
ip_coords = ip_coords[:, 2:]

# %% Map orientations onto integrations points
voxel_size_mm = VOXEL_SIZE / 1000
# Rescale to match pixel scale.
ip_data_coords = ip_coords / voxel_size_mm
# Translate so that origo becomes center of slice.
# If slice is 2x2 the new center is at (0.5, 0.5), halfway between indices 0 and 1.
ip_data_coords[:,2] -= W_MODEL / VOXEL_SIZE /  2 
ip_data_coords[:,[0,1,2]] += (np.array([phi.shape]) / 2)
# ip_data_coords[:,[0,1,2]] += (np.array([len(phi[:]),0,len(phi[0,0,:])]) / 2)
# Get orientation values at the coordinates using nearest neighbor interpolation (order=0).
# Values outside the data are set to 0.
ip_theta = ndimage.map_coordinates(theta, ip_data_coords.T, order=0, cval=np.nan)
ip_phi = ndimage.map_coordinates(phi, ip_data_coords.T, order=0, cval=np.nan)

# %% 3D scatter
M4IP.Int_point_plotting(ip_coords, ip_phi, Nplots=1, unit='$^\circ$', 
                        variable='$\phi$',
                        fig_name=sample_name+'_IP-3D misalignment',
                        fig_path=result_path)


# %% Create dataframe for easy group iteration.
df = pd.DataFrame(ip_indices, columns=['ele_id', 'ip_id'])

# Get max ids.
element_max_index = df['ele_id'].max()
ip_max_index = df['ip_id'].max()

# Set NaN values to zero.
ip_phi_out = ip_phi.copy()
ip_phi_out[np.isnan(ip_phi_out)] = 0

ip_theta_out = ip_theta.copy()
ip_theta_out[np.isnan(ip_theta_out)] = 0

# Set phi and theta values.
df['PHI'] = np.radians(ip_phi_out)
df['THETA'] = np.radians(ip_theta_out)

for column in df.columns[2:]:
    # Open writable file.
    with open(f'{sample_name}_{column}.f', 'w') as output:
        # Write header.
        output.write(f'      real*8 {column}0({ip_max_index},{element_max_index})\n')
    
        # For each element...
        for ele_id, group in df.groupby('ele_id'):
            ip_ids = group['ip_id']
            # Create element header.
            line = f'      DATA ({column}0(I,{ele_id}), I={ip_ids.min()},{ip_ids.max()})/ '
            # Get phis for the element.
            angles = [f'{angle:.6f}' for angle in group[column]]
            for i in range(3, len(angles), 3):
                # Only have three phis per line.
                angles[i] = '\n     &  ' + angles[i]
            # Add commas.
            line += ', '.join(angles)
    
            output.write(line + '/\n')
            