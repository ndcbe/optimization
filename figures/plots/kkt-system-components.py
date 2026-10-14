"""The parts of a scalar-constraint KKT system share the same candidate."""
import matplotlib.pyplot as plt
def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,1.55),layout="constrained")
    ax.set(xlim=(0,10),ylim=(0,2));ax.axis('off')
    box=dict(boxstyle='round,pad=.25',facecolor='white',edgecolor='black')
    ax.text(5,1.62,r'$\nabla f(\mathbf{x})+u\nabla g(\mathbf{x})+v\nabla h(\mathbf{x})=\mathbf{0}$',ha='center',fontsize=15,bbox=box)
    for x,label in [(1.2,r'$g(\mathbf{x})\leq0$'),(3.65,r'$h(\mathbf{x})=0$'),(6.05,r'$u\geq0$'),(8.45,r'$u g(\mathbf{x})=0$')]:
        ax.annotate('',xy=(x,.74),xytext=(5,1.35),arrowprops=dict(arrowstyle='-',color='black',lw=.8))
        ax.text(x,.45,label,ha='center',fontsize=14,bbox=box)
    return fig
