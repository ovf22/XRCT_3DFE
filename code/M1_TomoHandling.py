import matplotlib.pyplot as plt
import numpy as np
import sys

def tomo_crop(data_crop, xcut=0, ycut=0, zcut=0):
    """ Crop the tomography data according to the cutting parameters

    Parameters
    ----------
    data_crop : Tomography data file [Array] \n
    xcut : Amount of voxels removed from each side of the volume in the
    x-direction [int]. Default is 0.\n
    ycut : Amount of voxels removed from each side of the volume in the
    y-direction [int]. Default is 0.\n
    zcut : Amount of voxels removed from each side of the volume in the
    x-direction [int]. Default is 0.

    Returns
    -------
    data : Tomography data from ROI [Array]

    """
    # Write tomography data into array
    no_slicing = slice(None)
    data_shape = data_crop.shape
    cut_arr = 2 * np.array([xcut, ycut, zcut])

    # If the cropping dimensions are bigger than the tomography data set,
    # then kill the script
    if np.any(cut_arr > data_shape):
        print('Too much data was removed. Adjust cut parameters')
        sys.exit()

    # If any cutting parameters are chosen, then crop the volume accordingly
    # Else return the full data set
    if np.any(cut_arr > 0):
        print('Cropping data')
        if xcut != 0:
            x_slice = slice(xcut, -xcut)
        else:
            x_slice = no_slicing
        if ycut != 0:
            y_slice = slice(ycut, -ycut)
        else:
            y_slice = no_slicing
        if zcut != 0:
            z_slice = slice(zcut, -zcut)
        else:
            z_slice = no_slicing

        data = data_crop[x_slice, y_slice, z_slice]
    else:
        data = data_crop
        print('No cropping performed')
    return data


def tomo_plot_3(data, x_slice=0, y_slice=0, z_slice=0, title='',
                fig_name='Tomo_fig', fig_path='', figsize=(10, 10)):
    fig3 = plt.figure(constrained_layout=True, figsize=figsize)
    gs = fig3.add_gridspec(2, 2, width_ratios=([1.5, 1]), 
                           height_ratios=(1,data.shape[2]/data.shape[1]),
                           wspace=-0.1, hspace=0.05, left=0.1, right=0.9, 
                           bottom=0.1, top=0.9)
    f3_ax1 = fig3.add_subplot(gs[0,0])
    f3_ax2 = fig3.add_subplot(gs[1,0], sharex= f3_ax1)
    f3_ax3 = fig3.add_subplot(gs[:, 1])
    L,W,T = data.shape
    
    liney = np.array([[0,L],[y_slice, y_slice]])
    linex = np.array([[x_slice, x_slice],[0,W]])
    frame2=np.array([[1,L-1,L-1,1,1],[1,1,W-1,W-1,1]])
    f3_ax1.plot(liney[0,:],liney[1,:],'g', linewidth=2)
    f3_ax1.plot(linex[0,:],linex[1,:],'r', linewidth=2)
    f3_ax1.plot(frame2[0,:],frame2[1,:],'b', linewidth=3)
    img = data[:, :, z_slice].T
    f3_ax1.imshow(img.squeeze(), cmap='gray')
    f3_ax1.set_ylim(f3_ax1.get_ylim()[::-1])
    f3_ax1.set(xlabel='x-axis  [Voxel index]',
             ylabel='y-axis  [Voxel index]')

    # Plot xz-slice
    linex = np.array([[x_slice, x_slice],[0,T]])
    linez = np.array([[0,L],[z_slice, z_slice]])
    frame1=np.array([[2,L-2,L-2,2,2],[2,2,T-2,T-2,2]])
    img = data[:, y_slice, :].T
    f3_ax2.plot(linex[0,:],linex[1,:],'r', linewidth=2)
    f3_ax2.plot(linez[0,:],linez[1,:],'b', linewidth=2)
    f3_ax2.plot(frame1[0,:],frame1[1,:],'g', linewidth=4)
    f3_ax2.imshow(img.squeeze(), cmap='gray')
    f3_ax2.set_ylim(f3_ax2.get_ylim()[::-1])
    f3_ax2.set(xlabel='x-axis  [Voxel index]',
             ylabel='z-axis  [Voxel index]')

    # Plot yz-slice
    liney = np.array([[0,T],[y_slice, y_slice]])
    linez = np.array([[z_slice, z_slice],[0,W]])
    frame0=np.array([[1,T-1,T-1,1,1],[1,1,W-1,W-1,1]])
    f3_ax3.plot(liney[1,:],liney[0,:],'g', linewidth=2)
    f3_ax3.plot(linez[1,:],linez[0,:],'b', linewidth=2)
    f3_ax3.plot(frame0[1,:],frame0[0,:],'r', linewidth=3)    
    img = data[x_slice, :, :].T
    f3_ax3.imshow(img.squeeze(), cmap='gray')
    f3_ax3.set_ylim(f3_ax3.get_ylim()[::-1])
    f3_ax3.set(xlabel='y-axis  [Voxel index]',
             ylabel='z-axis  [Voxel index]')
    plt.savefig(fig_path + fig_name + '.png')