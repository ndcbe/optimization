"""Separator pair vs aggregate: exact unit-cube polyhedra and a common slice.

No solver or notebook result is reproduced. The five binary vertices are common;
the aggregate has two extra fractional vertices. The y_M=0 slice exhibits the
strict containment and the witness (1,0,1/2). BGW §15.7, Example 15.4.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def _faces(points):
    # Supporting planes merge coplanar triangles into polygon faces.
    from scipy.spatial import ConvexHull
    hull = ConvexHull(points)
    planes = {}
    for equation in hull.equations:
        key = tuple(np.round(equation, 10))
        planes[key] = equation
    faces = []
    for eq in planes.values():
        face = points[np.abs(points @ eq[:3] + eq[3]) < 1e-9]
        center = face.mean(axis=0)
        normal = eq[:3]
        u = face[0]-center
        u /= np.linalg.norm(u)
        v = np.cross(normal,u)
        order = np.argsort(np.arctan2((face-center)@v,(face-center)@u))
        faces.append(face[order])
    return faces


COMMON_VERTICES = np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0],[0,0,1]],dtype=float)
AGGREGATE_EXTRA = np.array([[1,0,0.5],[0,1,0.5]])


def make_figure():
    common, extra = COMMON_VERTICES, AGGREGATE_EXTRA
    fig = plt.figure(figsize=(10.4,7.5))
    for k, (name,points) in enumerate((('Pair of rows',common),('Aggregated row',np.vstack((common,extra))))):
        ax = fig.add_subplot(2,2,k+1,projection='3d')
        ax.add_collection3d(Poly3DCollection(_faces(points),facecolors='#56B4E9',
                            alpha=0.2,edgecolors='black',linewidths=1))
        ax.scatter(*common.T,color='black',marker='o',s=24,depthshade=False)
        if k:
            ax.scatter(*extra.T,color='#D55E00',marker='s',s=48,depthshade=False)
        ax.set(xlim=(0,1),ylim=(0,1),zlim=(0,1),xlabel='$y_A$',ylabel='$y_M$',zlabel='$y_{CS}$')
        ax.set_xticks([0,1]);ax.set_yticks([0,1]);ax.set_zticks([0,0.5,1])
        ax.set_title(name,pad=2,fontsize=15)
        ax.view_init(elev=23,azim=-57)
        ax.set_box_aspect((1,1,1))
        for axis in (ax.xaxis,ax.yaxis,ax.zaxis):
            axis.line.set_color('black');axis.pane.set_alpha(0)
        ax.grid(False)
    ax=fig.add_subplot(2,1,2)
    pair=np.array([[0,0],[1,0],[0,1]])
    aggregate=np.array([[0,0],[1,0],[1,0.5],[0,1]])
    ax.add_patch(Polygon(aggregate,facecolor='#E69F00',alpha=0.2,hatch='xxx',edgecolor='black'))
    ax.add_patch(Polygon(pair,facecolor='#56B4E9',alpha=0.3,hatch='///',edgecolor='black'))
    ax.plot([0,1],[1,0],color='#0072B2',linestyle='-',linewidth=2.4)
    ax.plot([0,1],[1,0.5],color='#D55E00',linestyle='--',linewidth=2.4)
    ax.plot([1],[0.5],marker='s',color='#D55E00',linestyle='none',markersize=9)
    ax.annotate('Witness $(1,0,1/2)$',xy=(1,0.5),xytext=(0.71,0.78),fontsize=12,
                arrowprops=dict(arrowstyle='->',color='black'))
    ax.text(0.10,0.12,'Both relaxations',fontsize=12,bbox=dict(facecolor='white',edgecolor='none',pad=2))
    ax.text(0.53,0.43,'Aggregate only',fontsize=12,rotation=-28,
            bbox=dict(facecolor='white',edgecolor='none',pad=1))
    ax.set(xlim=(-0.03,1.06),ylim=(-0.03,1.06),xlabel='$y_A$',ylabel='$y_{CS}$',
           title='Slice $y_M=0$: pair $y_A+y_{CS}\\leq1$; aggregate $y_A+2y_{CS}\\leq2$')
    ax.set_xticks([0,0.5,1]);ax.set_yticks([0,0.5,1]);ax.set_aspect('equal',adjustable='box')
    for spine in ax.spines.values():spine.set_color('black')
    fig.subplots_adjust(left=0.05,right=0.95,top=0.94,bottom=0.09,hspace=0.38)
    return fig
