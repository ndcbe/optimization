"""The exact equality-restricted objective and interval x1 >= sqrt(2)."""
import numpy as np
import matplotlib.pyplot as plt
def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,2.3),layout="constrained")
    t=np.linspace(.65,1.92,350);f=lambda z:9*z*z-18*z+9-np.log(2)-2*np.log(z)
    a=np.sqrt(2);root=(9+np.sqrt(117))/18
    ax.axvspan(a,1.92,facecolor='#56B4E9',alpha=.17,hatch='//',edgecolor='0.7')
    ax.plot(t,f(t),color='black',lw=1.6);ax.axvline(a,color='#0072B2',ls='--',lw=1.3)
    ax.plot(root,f(root),'o',color='black',ms=5);ax.plot(a,f(a),'s',color='black',ms=5)
    ax.annotate(r'$18t-18-2/t=0$',xy=(root,f(root)),xytext=(.69,2.0),fontsize=12,arrowprops=dict(arrowstyle='-',color='black'))
    ax.text(1.48,-1.20,r'$4-2t^2\leq0$',fontsize=12)
    ax.text(.70,3.3,r'$f(t,2t)=9t^2-18t+9-\ln2-2\ln t$',fontsize=12)
    ax.axhline(0,color='black',lw=.7,zorder=0)
    ax.set(xlim=(.65,1.92),ylim=(-1.6,4.1),xlabel=r'$t=x_1>0,\quad x_2=2t$',ylabel=r'$f(t,2t)$')
    return fig
