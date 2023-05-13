import matplotlib.pyplot as plt
import numpy as np

   
def Int_point_plotting(ip_coords, ip_data_set, Nplots, vmin=[-10], vmax=[10], unit='unit', 
                            variable='Var', fig_name='Test',
                            fig_path='',fig_title='', figsize=(9, 6), sp_title=None):
    print('Start plotting')
    seismic_nan_green = plt.cm.seismic.copy()
    
    x_min, x_max = np.min(ip_coords[:, 0]), np.max(ip_coords[:, 0])
    y_min, y_max = np.min(ip_coords[:, 1]), np.max(ip_coords[:, 1])
    z_min, z_max = np.min(ip_coords[:, 2]), np.max(ip_coords[:, 2])
    
    frame_xy = np.array([[x_min, x_max, x_max, x_min, x_min],
                         [y_min, y_min, y_max, y_max, y_min],
                         [z_min, z_min, z_min, z_min, z_min]])
    
    frame_xz = np.array([[x_min, x_max, x_max, x_min, x_min],
                         [y_max, y_max, y_max, y_max, y_max],
                         [z_min, z_min, z_max, z_max, z_min]])
    
    frame_yz = np.array([[x_max, x_max, x_max, x_max, x_max],
                         [y_max, y_min, y_min, y_max, y_max],
                         [z_min, z_min, z_max, z_max, z_min]])
    
    fig = plt.figure(figsize=figsize)
    
    for i in range(Nplots):
        if ip_data_set.ndim==1:
            ip_data = ip_data_set
        else:
            ip_data=ip_data_set[:,i]
        ax = fig.add_subplot(1, Nplots, i+1, projection='3d')
        ax.set_box_aspect([1,(z_max-z_min)/(x_max-x_min),(y_max-y_min)/(x_max-x_min)])
        
        ax.plot3D(frame_xy[0, :], frame_xy[2, :], frame_xy[1, :], 'k', linewidth=0.5, zorder=100)
        ax.plot3D(frame_xz[0, :], frame_xz[2, :], frame_xz[1, :], 'k', linewidth=0.5, zorder=100)
        ax.plot3D(frame_yz[0, :], frame_yz[2, :], frame_yz[1, :], 'k', linewidth=0.5, zorder=100)
        ax.set(xlabel='x-axis [mm]',
               ylabel='z-axis [mm]',
               zlabel='y-axis [mm]')
        
        
        sc3D = ax.scatter(ip_coords[:, 0], ip_coords[:, 2], ip_coords[:, 1], 
                          c=ip_data, cmap=seismic_nan_green, 
                          vmin=vmin[i], vmax=vmax[i], s=10, alpha=.3)
        clb = fig.colorbar(sc3D, shrink=0.5, pad=0.1, ticks=[vmin[i], vmin[i]/2, 
                           0, vmax[i]/2, vmax[i]])
        clb.ax.set_title(variable)
        
        if ip_data_set.ndim == 1:
            clb.ax.set_yticklabels(['$<$'+str(round(vmin[i]))+unit, str(round(vmin[i]/2))+unit,
                                    '0'+unit, str(round(vmax[i]/2))+unit, '$>$'+str(round(vmax[i]))+unit])
        else:
            clb.ax.set_yticklabels([str(round(vmin[i]))+unit, str(round(vmin[i]/2))+unit,
                                    '0'+unit, str(round(vmax[i]/2))+unit, str(round(vmax[i]))+unit])
        
        if sp_title != None:
            ax.title.set_text(sp_title[i])
            ax.title.set_size(16)
        ax.view_init(azim=-60, elev=10)
         
        major_ticks_x=np.linspace(np.round(x_min, 1), np.round(x_max, 1), 5)
        minor_ticks_x=np.linspace(np.round(x_min, 1), np.round(x_max, 1), 5)
        major_ticks_y=np.linspace(np.round(z_min, 1), np.round(z_max, 1), 3)
        minor_ticks_y=np.linspace(np.round(z_min, 1), np.round(z_max, 1), 3)
        major_ticks_z=np.linspace(np.round(y_min, 1), np.round(y_max, 1), 5)
        minor_ticks_z=np.linspace(np.round(y_min, 1), np.round(y_max, 1), 5)
        
        ax.xaxis.labelpad = 10
        ax.yaxis.labelpad = 10
        ax.zaxis.labelpad = 10
        
        ax.set_xticks(major_ticks_x)
        ax.set_yticks(major_ticks_y)
        ax.set_zticks(major_ticks_z)
        ax.set_xticks(minor_ticks_x,minor=True)
        ax.set_yticks(minor_ticks_y,minor=True)
        ax.set_zticks(minor_ticks_z,minor=True)
        
        ax.grid(which="major",alpha=0.6)
        ax.grid(which="minor",alpha=0.3)
    
        ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    fig.suptitle(fig_title, fontsize=20)
    plt.tight_layout()
    plt.savefig(fig_path + fig_name + '.png', dpi=300)
    

