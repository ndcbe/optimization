"""Row Jacobians act on movement; their transpose acts on multipliers."""
import matplotlib.pyplot as plt
def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,2.4),layout="constrained");ax.set(xlim=(0,10),ylim=(0,3));ax.axis('off')
    for y,lhs,rhs,label in [(2.2,r'$\mathbf{J}_g\,\mathbf{p}$',r'$\Delta\mathbf{g}$','first-order constraint change'),(.85,r'$\mathbf{J}_g^T\,\mathbf{u}$',r'$-\nabla f-\mathbf{J}_h^T\mathbf{v}$','gradient balance')]:
        ax.text(.1,y,lhs,fontsize=19,va='center',bbox=dict(boxstyle='round',facecolor='#E8F2F8',edgecolor='black'))
        ax.annotate('',xy=(4.2,y),xytext=(3,y),arrowprops=dict(arrowstyle='->',color='black',lw=2))
        ax.text(4.5,y,rhs,fontsize=18,va='center')
        ax.text(4.5,y-.55,label,fontsize=11)
    return fig
