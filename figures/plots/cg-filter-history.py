"""Lecture 22 prepared analytic diagram. Single shared public figure source.
Distinct styles/markers/direct labels retain meaning in greyscale.
These are specified analytic toy inputs, not independent notebook result solves.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    from matplotlib.patches import Rectangle
    fig,ax=plt.subplots(figsize=(7.1,3.3))
    history=[(.5,4),(1,3),(2,2),(3,1)]
    for i,(v,f) in enumerate(history):
        ax.add_patch(Rectangle((.9*v,f-.2*v),3.3-.9*v,4.7-f+.2*v,facecolor='0.8',alpha=.22,hatch=['/','\\','..','xx'][i],edgecolor='0.5',lw=.7))
        ax.plot(v,f,'ko',ms=5);ax.annotate(f'F{i+1}',(v,f),xytext=(4,7),textcoords='offset points',fontsize=9)
    for label,v,f,marker in [('A',.4,4.2,'^'),('B',2.2,1.05,'s'),('C',2.8,.5,'X')]:
        ax.scatter(v,f,marker=marker,s=75,color='#0072B2' if label!='C' else '#D55E00');ax.annotate(label,(v,f),xytext=((.12,4.45) if label=='A' else (2.85,.1) if label=='C' else (2.25,1.25)),fontsize=12,arrowprops=dict(arrowstyle='-',lw=.7,color='black'))
    ax.plot(1.7,1.7,'k*',ms=11);ax.annotate('current',(1.7,1.7),xytext=(1.1,1.15),fontsize=9,arrowprops=dict(arrowstyle='-',lw=.7,color='black'))
    ax.plot([0,3.3],[3.4,.1],'k--',lw=1.5,label='current merit level f + violation = 3.4')
    ax.set(xlabel='constraint violation',ylabel='objective f',xlim=(0,3.3),ylim=(0,4.7));ax.legend(fontsize=9,loc='upper right')
    fig.tight_layout();return fig
