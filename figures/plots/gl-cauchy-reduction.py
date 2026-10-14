"""Cauchy reduction certificate on a ray: B=diag(2,8), g=(2,1), radius=1."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    g=np.array([2.,1.]);B=np.diag([2.,8.]);D=1.;a=np.linalg.norm(g);b=(g@B@g)/(g@g)
    t0=min(D,a/np.linalg.norm(B,2));tc=min(D,a/b)
    model=lambda t:-a*t+.5*b*t*t
    assert -model(tc)>=-model(t0)>=.5*a*t0-1e-12
    t=np.linspace(0,1.05,220)
    fig,ax=plt.subplots(figsize=(6.,2.8),layout='constrained')
    ax.plot(t,model(t),color='black',linestyle='-',linewidth=2,label=r'$m(-t\mathbf{g}/\|\mathbf{g}\|)-m(0)$')
    ax.plot(t0,model(t0),'s',color='#0072B2',ms=7,label=r'guaranteed trial $t_0$')
    ax.plot(tc,model(tc),'o',color='#D55E00',ms=7,label=r'Cauchy minimum $t_C$')
    ax.axvline(D,color='black',linestyle='--',linewidth=1)
    ax.axhline(0,color='black',linewidth=.7)
    ax.text(.88,-.32,r'$\Delta=1$',fontsize=11)
    ax.set(xlim=(0,1.05),ylim=(-.93,.25),xlabel='distance $t$ along the ray',ylabel='model change')
    ax.text(.025,.12,r'$m(-t\mathbf{g}/\|\mathbf{g}\|)-m(0)$',fontsize=10)
    ax.annotate(r'trial $t_0$',xy=(t0,model(t0)),xytext=(.055,-.73),arrowprops=dict(arrowstyle='->'),fontsize=10)
    ax.annotate(r'Cauchy $t_C$',xy=(tc,model(tc)),xytext=(.62,-.43),arrowprops=dict(arrowstyle='->'),fontsize=10)
    return fig
