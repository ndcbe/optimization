"""Schematic filter acceptance tasks; source-specific switching is stated in text."""
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,1.7));ax.set(xlim=(0,10),ylim=(0,2.7));ax.axis('off')
    def box(x,y,text):
        ax.text(x,y,text,ha='center',va='center',fontsize=10,bbox=dict(boxstyle='round,pad=.45',facecolor='white',edgecolor='black'))
    box(1.2,1.8,'Historical\nfilter test');box(4.2,1.8,'Switch at\nthis trial?');box(8,2.25,'Objective\nArmijo');box(8,1.25,'Current-pair\nprogress')
    for a,b in [((2.35,1.8),(3.25,1.8)),((5.18,1.96),(6.75,2.25)),((5.18,1.6),(6.75,1.25))]:ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color='black'))
    ax.text(2.8,2.03,'pass',ha='center',fontsize=9);ax.text(6,2.3,'yes',fontsize=9);ax.text(6,1.0,'no',fontsize=9)
    ax.text(5,.25,r'Unacceptable trials $\longrightarrow$ shorten $\alpha$; no acceptable trial $\longrightarrow$ restoration',ha='center',fontsize=10)
    fig.tight_layout();return fig
