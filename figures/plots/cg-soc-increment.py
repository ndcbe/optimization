"""Generic vector accounting, schematic; does not recompute the canonical circle result."""
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,1.65));ax.set(xlim=(0,10),ylim=(-.2,2.8));ax.axis('off')
    pts=[(.8,1.5),(4.5,1.5),(8.8,2.25),(8.8,.45)]
    for x,y in pts:ax.plot(x,y,'ko',ms=5)
    for a,b in [(pts[0],pts[1]),(pts[1],pts[2]),(pts[0],pts[3])]:ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color='black',lw=1.4,shrinkA=4,shrinkB=4))
    ax.text(.8,1.83,r'$\mathbf{x}^k$',ha='center',fontsize=12);ax.text(4.5,1.75,r'$\mathbf{x}^k+\mathbf{d}$',ha='center',fontsize=11)
    ax.text(2.6,1.75,r'$\mathbf{d}$',fontsize=12);ax.text(6.5,2.15,r'increment $\mathbf{r}$',ha='center',fontsize=11)
    ax.text(5,.35,r'replacement $\hat{\mathbf{d}}$',ha='center',fontsize=11)
    ax.text(8.8,2.57,r'$\mathbf{x}^k+\mathbf{d}+\mathbf{r}$',ha='center',fontsize=11);ax.text(8.8,.02,r'$\mathbf{x}^k+\hat{\mathbf{d}}$',ha='center',fontsize=11)
    ax.text(.4,2.75,'General step conventions (schematic)',ha='left',fontsize=10)
    fig.tight_layout();return fig
