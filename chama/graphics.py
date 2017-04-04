"""
The graphics module contains ...
"""
import matplotlib.pyplot as plt
from matplotlib import ticker
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import ConvexHull  
import numpy as np
from matplotlib.patches import Circle, Ellipse, Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.animation import FuncAnimation


def signal_convexhull(signal, scenarios, threshold, timesteps=None,  
                   colormap=plt.cm.viridis, txyz_names=['T', 'X', 'Y', 'Z'], 
                   x_range=(None, None), y_range=(None, None), z_range=(None, None)):
    
    t_col = txyz_names[0]
    x_col = txyz_names[1]
    y_col = txyz_names[2]
    z_col = txyz_names[3]

    if timesteps is None:
        timesteps = sorted(set(signal.loc[:,t_col]))

    fig = plt.figure()
    plt.set_cmap(colormap)
    ax = fig.add_subplot(111, projection='3d')

    for scenario in scenarios:
        i = 0
        for timestep in timesteps:
            try:
                color = colormap(i)
                i = i + 1/float(len(timesteps))
                
                signal_t = signal[signal[t_col] == timestep]
                conc_filter = signal_t[scenario] > threshold
                
                # plot points
                #data = signal_t[[x_col,y_col,z_col,scenario]][conc_filter]
                #data = data.as_matrix()
                #ax.scatter(data[:,0], data[:,1], data[:,2], c=data[:,3],s=30)
                
                data = signal_t[[x_col,y_col,z_col]][conc_filter]
                data = data.as_matrix()
                hull=ConvexHull(data)
                ax.plot_trisurf(data[:,0], data[:,1], data[:,2], 
                                triangles=hull.simplices,
                                edgecolor='none', 
                                shade=False,
                                color=color)
            except:
                pass

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_zlabel(z_col)
    
    ax.set_xlim3d(x_range[0],x_range[1])
    ax.set_ylim3d(y_range[0],y_range[1])
    ax.set_zlim3d(z_range[0],z_range[1])

def signal_xsection(signal, scenarios, threshold = None, timesteps=None, 
                        x_value=None, y_value=None, z_value=None, log_flag = False,
                        colormap=plt.cm.viridis, alpha = 0.7, V = 10,
                        txyz_names=['T', 'X', 'Y', 'Z'], 
                        x_range=(None, None), y_range=(None, None), z_range=(None, None)):
        
    t_col = txyz_names[0]
    x_col = txyz_names[1]
    y_col = txyz_names[2]
    z_col = txyz_names[3]

    if timesteps is None:
        timesteps = sorted(set(signal.loc[:,t_col]))

    if log_flag:
        log_flag = ticker.LogLocator()
    else:
        log_flag = ticker.MaxNLocator()
      
    fig = plt.figure(figsize=(20,5))
    plt.set_cmap(colormap)
    ax1 = fig.add_subplot(1,3,1)
    ax2 = fig.add_subplot(1,3,2)
    ax3 = fig.add_subplot(1,3,3)
    
    signal_t = signal[signal[t_col].isin(timesteps)]
    signal_t = signal_t.groupby([x_col, y_col, z_col]).sum()
    data = signal_t[scenarios]

    def contour_data(temp, threshold, log_flag):
        temp = temp.unstack()
        X = temp.index.values
        Y = temp.columns.values
        Z = temp.values

        if threshold:
            Z[Z<=threshold] = threshold
        Z = np.transpose(Z)
        return X, Y, Z
    
    temp = data.reset_index()
    if z_value:
        if type(z_value) is not list:
            z_value = [z_value]
        temp = temp[temp[z_col].isin(z_value)]
    temp = temp.groupby([x_col,y_col])['C'].mean()
    
    Xi, Yi, Z = contour_data(temp, threshold, log_flag)
    cplot1 = ax1.contourf(Xi, Yi, Z, alpha=alpha, cmap=colormap, locator=log_flag)
    ax1.set_xlim(x_range[0],x_range[1])
    ax1.set_ylim(y_range[0],y_range[1])
    ax1.set_xlabel(x_col)
    ax1.set_ylabel(y_col)

    temp = data.reset_index()
    if y_value:
        if type(y_value) is not list:
            y_value = [y_value]
        temp = temp[temp[y_col].isin(y_value)]
    temp = temp.groupby([x_col,z_col])['C'].mean()
    
    Xi, Yi, Z = contour_data(temp, threshold, log_flag)
    cplot2 = ax2.contourf(Xi, Yi, Z, alpha=alpha, cmap=colormap, locator=log_flag)
    ax2.set_xlim(x_range[0],x_range[1])
    ax2.set_ylim(z_range[0],z_range[1])
    ax2.set_xlabel(x_col)
    ax2.set_ylabel(z_col)

    temp = data.reset_index()
    if x_value:
        if type(x_value) is not list:
            x_value = [x_value]
        temp = temp[temp[x_col].isin(x_value)]
    temp = temp.groupby([y_col,z_col])['C'].mean()
    
    Xi, Yi, Z = contour_data(temp, threshold, log_flag)
    cplot3 = ax3.contourf(Xi, Yi, Z, alpha=alpha, cmap=colormap, locator=log_flag)
    ax3.set_xlim(y_range[0],y_range[1])
    ax3.set_ylim(z_range[0],z_range[1])
    ax3.set_xlabel(y_col)
    ax3.set_ylabel(z_col)

    fig.colorbar(cplot1,ax=ax1)
    fig.colorbar(cplot2,ax=ax2)
    fig.colorbar(cplot3,ax=ax3)

    fig.show()

def animate_puffs(puff, x_range=(None, None), y_range=(None, None), z_range=(None, None)):

    def circles(x, y, s, c='b', vmin=None, vmax=None, **kwargs):
        """
        Make a scatter plot of circles. 
        Similar to plt.scatter, but the size of circles are in data scale.
        Parameters
        ----------
        x, y : scalar or array_like, shape (n, )
            Input data
        s : scalar or array_like, shape (n, ) 
            Radius of circles.
        c : color or sequence of color, optional, default : 'b'
            `c` can be a single color format string, or a sequence of color
            specifications of length `N`, or a sequence of `N` numbers to be
            mapped to colors using the `cmap` and `norm` specified via kwargs.
            Note that `c` should not be a single numeric RGB or RGBA sequence 
            because that is indistinguishable from an array of values
            to be colormapped. (If you insist, use `color` instead.)  
            `c` can be a 2-D array in which the rows are RGB or RGBA, however. 
        vmin, vmax : scalar, optional, default: None
            `vmin` and `vmax` are used in conjunction with `norm` to normalize
            luminance data.  If either are `None`, the min and max of the
            color array is used.
        kwargs : `~matplotlib.collections.Collection` properties
            Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls), 
            norm, cmap, transform, etc.
        Returns
        -------
        paths : `~matplotlib.collections.PathCollection`
        Examples
        --------
        a = np.arange(11)
        circles(a, a, s=a*0.2, c=a, alpha=0.5, ec='none')
        plt.colorbar()
        License
        --------
        This code is under [The BSD 3-Clause License]
        (http://opensource.org/licenses/BSD-3-Clause)
        """

        if np.isscalar(c):
            kwargs.setdefault('color', c)
            c = None

        if 'fc' in kwargs:
            kwargs.setdefault('facecolor', kwargs.pop('fc'))
        if 'ec' in kwargs:
            kwargs.setdefault('edgecolor', kwargs.pop('ec'))
        if 'ls' in kwargs:
            kwargs.setdefault('linestyle', kwargs.pop('ls'))
        if 'lw' in kwargs:
            kwargs.setdefault('linewidth', kwargs.pop('lw'))
        # You can set `facecolor` with an array for each patch,
        # while you can only set `facecolors` with a value for all.

        zipped = np.broadcast(x, y, s)
        patches = [Circle((x_, y_), s_)
                   for x_, y_, s_ in zipped]
        collection = PatchCollection(patches, **kwargs)
        if c is not None:
            c = np.broadcast_to(c, zipped.shape).ravel()
            collection.set_array(c)
            collection.set_clim(vmin, vmax)

        ax = plt.gca()
        ax.add_collection(collection)
        ax.autoscale_view()
        plt.draw_if_interactive()
        if c is not None:
            plt.sci(collection)
        return collection

    fig, ax = plt.subplots()
    # ln, = plt.plot([],[],animated=True)

    def update(time):
        plt.cla()
        ax.set_xlim(x_range[0], x_range[1])
        ax.set_ylim(y_range[0], y_range[1])
        ax.set_title('T = %6.2f' %(time))
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        temp = puff.loc[puff['T'] == time]
        out = circles(temp['X'], temp['Y'], temp['sigmaY'], alpha=0.5, edgecolor='none')
        return out

    ani = FuncAnimation(fig, update, frames=puff['T'].unique())

    # Need a coder like ffmpeg installed in order to save
    # ani.save('puff.mp4')

    plt.show()