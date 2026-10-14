"""Prepared mechanism: multiply constraint changes by minus their multipliers."""
import matplotlib.pyplot as plt
def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,2.3),layout="constrained");ax.set(xlim=(0,10),ylim=(0,3));ax.axis('off')
    rows=[(2.4,'equalities',r'$\Delta h_j=0$',r'$-v_j^*$'),(1.5,'untouched active',r'$\Delta g_i=0$',r'$-u_i^*$'),(.6,'moved fence',r'$\Delta g_{\hat\imath}=-\epsilon$',r'$-u_{\hat\imath}^*$')]
    for y,label,change,weight in rows:
        ax.text(.05,y,label,fontsize=12,va='center')
        ax.text(3,y,change,fontsize=14,va='center',bbox=dict(boxstyle='round,pad=.3',facecolor='#E8F2F8',edgecolor='black'))
        ax.annotate('',xy=(7.4,y),xytext=(5.3,y),arrowprops=dict(arrowstyle='->',color='black',lw=1.5))
        ax.text(6.1,y+.2,weight,fontsize=13,ha='center')
    ax.plot([7.5,7.7,7.7,7.5],[.3,.3,2.7,2.7],color='#D55E00',linestyle='--',lw=2)
    ax.text(8,1.5,'sum in\nobjective\nexpansion',fontsize=12,va='center')
    return fig
