from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy as np


def st_misalign(vec):
    """Function calculates the angles representing the fiber misalignment
    direction. Angles are represented as Azimuth and elevation angles, where
    Azimuth is the angle of a vector projected into the xy-plane, and the
    elevation angle is the angle between the vector and the z-axis.

    Parameters
    ----------
    vec : Unit vectors of the dominant directions in the volume
    [Array of floats]

    Returns
    -------
    theta : Azimuth angle. Angle between projected vector into the XY-plane
    and the X-axis (domain: -90:90 degrees) [Array of floats]\n
    phi : Elevation angle relative to the z-axis (domain: -90:90 degrees)
    [Array of floats]

    """
    #  Azimuth angle [Y-Z plane]
    theta = np.arctan(vec[2] / vec[1]) * 180 / np.pi
    # Elevation angle [X-Y-Z space] orientation relative to X axis
    phi = (np.arctan(np.sqrt(vec[1]**2 + vec[2]**2) / vec[0])
           * np.sign(vec[1]) * 180 / np.pi)

    return theta, phi


def rot_mat(phi, theta):
    """ Calculate rotation matrix for rotation about the y and z axis.

    Parameters
    ----------
    phi : Rotation angle around y-axis [float - radians]\n
    theta : Rotation angle around z-axis [float - radians]

    Returns
    -------
    R : Rotation matrix [3x3 Array]

    """
    # cos and sin to phi and theta
    cp, sp, ct, st = np.cos(phi), np.sin(phi), np.cos(theta), np.sin(theta)

    # Rotation matrix around z-axis
    Rz = np.array([[cp, -sp, 0],
                   [sp, cp, 0],
                   [0, 0, 1]])
    # Rotation matrix around y-axis
    Rx = np.array([[1, 0, 0],
                   [0, ct, -st],
                   [0, st, ct]])
    # Azimuth and elevation rotation matrix
    R = Rz@Rx
    return R


def orient_average(vec):
    """ Calculate the average orientation of the tomograpy data set.

    Parameters
    ----------
    vec : Eigenvectors from structure tensor analysis [Array]

    Returns
    -------
    vec_new : Corrected eigenvectors for global misalignment
    of tomography scan.

    """
    # Calculate average vector
    vec_avg = (np.average(vec.reshape(3, -1), axis=1)
               / np.linalg.norm(np.average(vec.reshape(3, -1), axis=1)))

    # Calculate average azimuth and elevation angles
    phi_avg = -(np.arctan(np.sqrt(vec_avg[1]**2 + vec_avg[2]**2) / vec_avg[0])
                * np.sign(vec_avg[1]))
    theta_avg = -np.arctan(vec_avg[2] / vec_avg[1])
    print('The mean orientations (azimuth \u03B8, elevation \u03C6) =\
          (%1.2f\u00B0, % 1.2f\u00B0)' % (np.degrees(theta_avg),
          np.degrees(phi_avg)))

    # Calculate rotation matrix
    R = rot_mat(phi_avg, theta_avg)

    # Calculate new orientation vectors
    vec_new = (R@vec.reshape(3, -1)).reshape(vec.shape)
    return vec_new


def plot_hist(data1, data2, bins=180,
              limits=90, alpha=0.5, title=None,
              fig_name='Misalignment_hist', fig_path=''):
    """ Plot histogram of orientation data. Other data sets can also be used by
    considering a representable range (change limits).

    Parameters
    ----------
    data : Orientation data [Array of angles]\n
    bins : Number of bins for histogram. The default is 180 [int]\n
    limits : Histogram range defined by [-limits, limits].
    The default is 90 [float]\n
    title : Plot title [str]\n
    fig_name : Name of saved figure without extension [str].
    Default is Tomo_fig\n
    fig_path : Directory for saving figure [str].
    Default is working directory

    Returns
    -------
    Histogram of orientations before and after angle correction.

    """
    data1_mean = np.average(data1)
    fig, ax = plt.subplots(1, 1, figsize=(10,6))
    # plot histogram of original vector orientations
    ax.hist(data1.ravel(), bins=bins, range=[-limits, limits],
            alpha=alpha, label='Original', color='b', density=True)
    plt.axvline(data1.mean(), color='b', linestyle='solid',
                linewidth=1.5, label=(r'Mean $\phi$'))
    plt.axvline(np.abs(data1).mean(), color='b', linestyle='dotted',
                linewidth=2.5, label=(r'Mean $|\phi|$'))
    
    # plot histogram of corrected vector orientations
    ax.hist(data2.ravel(), bins=bins, range=[-limits, limits],
            alpha=alpha, label='Aligned', color='r', density=True)
    plt.axvline(data2.mean(), color='r', linestyle='solid',
                linewidth=1.5, label=(r'Mean $\phi$'))
    plt.axvline(np.abs(data2).mean(), color='r', linestyle='dotted',
                linewidth=2.5, label=(r'Mean $|\phi|$'))
    # add plot formatting
    ax.set_xlabel('Fiber elevation angle, $\phi$ [$^\circ$]')
    ax.set_ylabel('Fraction [-]')
    ax.set_xlim([-limits,limits])
    plt.legend(loc=2)
    if title:
        ax.set_title(title)
    plt.savefig(fig_path + fig_name + '.png')
    plt.show()
    
def fig_with_colorbar(data, misalignment, title='', alpha=0.5, cmap=None,
                      vmin=None, vmax=None,
                      fig_name='Misalignment_overlay', fig_path=''):
    """ Creates a figure with data, fiber misalignment overlay and color bar.

    Parameters
    ----------
    data : Tomography data 2D slice [Array]\n
    misalignment : Fiber misalignment 2D overlay [Array]\n
    title : Figure title [str]. Default is empty string\n
    alpha : overlay plot bleeding parameter [float]. The default is 0.5\n
    cmap : Color map for fiber misalignment overlay plot [str]\n
    vmin : Minimum limit for fiber misalignment overlay plot.
    The default is None.\n
    vmax : Minimum limit for fiber misalignment overlay plot.
    The default is None.\n
    fig_name : Name of saved figure without extension [str].
    Default is Tomo_fig\n
    fig_path : Directory for saving figure [str].
    Default is working directory

    Returns
    -------
    None.

    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='3%', pad=0.1)
    # cax.tick_params(labelsize=16)

    # plot gray scale tomogram image
    ax.imshow(data, cmap='gray')
    ax.set_ylim(ax.get_ylim()[::-1])

    # plot reg overlay of fibermisalignment
    im = ax.imshow(misalignment, alpha=alpha, cmap=cmap, vmin=vmin, vmax=vmax)

    # add colorbar for misalignment range
    clb = fig.colorbar(im, cax=cax, orientation='vertical',
                       ticks=[vmin, vmin/2, 0, vmax/2, vmax])
    clb.ax.set_title('$\phi$ [$^\circ$]')
    # vertically oriented colorbar
    clb.ax.set_yticklabels(['$<$'+str(vmin), str(vmin/2), '$0$',
                            str(vmax/2), '$>$'+str(vmax)])
    # add plot formatting
    # ax.set_title(title, fontsize=16, fontweight="bold")
    ax.set_xlabel('x-axis [pixels]')
    ax.set_ylabel('y-axis [pixels]')
    plt.savefig(fig_path + fig_name + '.png')
    plt.show()

