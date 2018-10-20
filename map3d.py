#import dependent modules
import sys
import numpy as np
from mayavi import mlab



def map3d_surface(mode,xdata=None,ydata=None,zdata=None,scalardata=None,vmin=None,vmax=None,data_cmap='blue-red',data_alpha=1,topo=None,topo_limits=None,zscale=500.,topo_vmin=None,topo_vmax=None,topo_cmap='bone',topo_cmap_reverse=False,land_constant=False,land_color=(0.7,0.7,0.7),set_view=None):
    """
    mode = (string) coordinate system of 3D projection. Options are 'rectangle' (default), 'spherical' or 'cylindrical'
    xdata = optional; (1D numpy array) longitude values for data array
    ydata = optional; (1D numpy array) latitude values for data array
    zdata = optional; (1D numpy array) depth values for data array
    scalardata = optional; (2D numpy array) scalar field to plot colors on surface
    vmin = (float) colorbar minimum for data
    vmax = (float) colorbar maximum for data
    data_cmap = colormap for data surface, default is blue-red
    data_alpha = (float or int) opacity for data surface from 0 to 1, default is 1
    topo = optional; input topography file, default is etopo 30 
    topo_limits = optional; longitude and latitude limits for 3d topography plot [lon_min, lon_max, lat_min, lat_max], longitudes range -180 to 180, latitude -90 to 90, default is entire globe
    zscale = optional; change vertical scaling for plotting, default is 500
    topo_cmap = optional; default is bone 
    topo_cmap_reverse = optional; reverse topography colormap, default is false
    set_view = optional; set the mayavi camera angle with input [azimuth, elevation, distance, focal point], default is 
    """
    #TODO expand/clean descriptions
        
    #load topo data
    data = np.load('etopo1_30min.npz')
    xraw = data['x']
    yraw = data['y']
    zraw = np.swapaxes(data['z'][:,:],0,1)
    zraw[zraw>0]=0.
    phi = (yraw[:]*np.pi*2)/360.+np.pi/2.
    theta = (xraw[:]*np.pi*2)/360.
    c = zraw
    theta=np.append(theta,theta[0])
    c = np.concatenate((c,np.expand_dims(c[0,:],axis=0)),axis=0)

    if topo_limits is not None:
        phi_1 = topo_limits[2]
        phi_2 = topo_limits[3]
        theta_1 = topo_limits[0]
        theta_2 = topo_limits[1]

        phi_ind1 = np.argmin(np.abs(yraw-phi_1))
        phi_ind2 = np.argmin(np.abs(yraw-phi_2))
        theta_ind1 = np.argmin(np.abs(xraw-theta_1))
        theta_ind2 = np.argmin(np.abs(xraw-theta_2))

        #restrict topo extent
        phi=phi[phi_ind1:phi_ind2]
        theta=theta[theta_ind1:theta_ind2]
        c = c[theta_ind1:theta_ind2:,phi_ind1:phi_ind2]
    phi, theta = np.meshgrid(phi,theta)
   


    if topo_vmin is None:
        tvmin = 0
    else:
        tvmin = topo_vmin
    if topo_vmax is None:
        tvmax = 7000
    else:
        tvmax = topo_vmax
    
    #make figure
    mlab.figure(size = (1024,768),bgcolor = (1,1,1), fgcolor = (0.5, 0.5, 0.5))
    mlab.clf()
    # Plot Bathymetry mesh
    if mode is 'sphere':
        x = np.sin(phi) * np.cos(theta[::-1]) * (1 + c/zscale)
        y = np.sin(phi) * np.sin(theta[::-1]) * (1 + c/zscale)
        z = np.cos(phi) * (1 + c/zscale)
    
    elif mode is 'cylinder':
        x = np.sin(phi) * np.cos(theta[::-1])
        y = np.sin(phi) * np.sin(theta[::-1])
        z = c/zscale
    
    elif mode is 'rectangle':
        y, x = np.meshgrid(yraw[phi_ind1:phi_ind2],xraw[theta_ind1:theta_ind2])
        z = c/zscale
    
    #make bathymetry mesh
    m = mlab.mesh(x, y, z, scalars = -c, colormap=topo_cmap,vmin=tvmin,vmax=tvmax)
    
    #optional: reverse bathymetry colormap
    if topo_cmap_reverse is True:
        lut = m.module_manager.scalar_lut_manager.lut.table.to_array() 
        ilut=lut[::-1]
        m.module_manager.scalar_lut_manager.lut.table = ilut

    #optional: plot constant color on land
    if land_constant is True:
        sl = mlab.mesh(x, y, z,mask = c<0,color =land_color)


    #optional: plot data surface
    if xdata is not None and ydata is not None and zdata is not None:
        #TODO add an error message if not all data fields are provided
        #prep data grid
        phi_iso, theta_iso = np.meshgrid(((ydata*np.pi*2)/360.)+np.pi/2.,(xdata*np.pi*2)/360.)
 
        if mode is 'sphere':
            x_iso = np.sin(phi_iso) * np.cos(theta_iso[::-1]) * (1 -depth_h/zscale)
            y_iso = np.sin(phi_iso) * np.sin(theta_iso[::-1]) * (1 -zdata/zscale)
            z_iso = np.cos(phi_iso) * (1 -zdata/zscale)
        elif mode is 'cylinder':
            x_iso = np.sin(phi_iso) * np.cos(theta_iso[::-1])
            y_iso = np.sin(phi_iso) * np.sin(theta_iso[::-1])
            z_iso = zdata/zscale
    
        elif mode is 'rectangle':
            y_iso,z_iso = np.meshgrid(ydata,zdata)
            x_iso,z_iso = np.meshgrid(xdata,zdata)
            z_iso =-z_iso/zscale 
        
    if scalardata is not None:
        m = mlab.mesh(x_iso, y_iso, z_iso,scalars=scalardata,colormap=data_cmap,vmin =vmin,vmax=vmax,opacity=data_alpha)
        m.module_manager.scalar_lut_manager.lut.nan_color = [0,0,0,0]
    else:
        m = mlab.mesh(x_iso, y_iso, z_iso,vmin =vmin,vmax=vmax,opacity=data_alpha)
             
    #optional: change mayavi camera settings
    if set_view is None:
        mlab.view(distance = 'auto')
    else:
        mlab.view(azimuth = set_view[0], elevation = set_view[1], distance = set_view[2], focalpoint = set_view[3])


    return mlab

