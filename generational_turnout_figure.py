"""Recreate the earlier age comparison from recovered rounded inputs.
Historical illustrative reconstruction, not updated demographic estimates.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
P=Path(__file__).resolve().parent
eligible=np.array([950000,3307000,2380000])
valid=np.array([67000,702000,1131000])
choices=np.array([[32,61,7],[50,46,4],[63,35,2]])
ratio=valid/eligible
model=np.column_stack([choices*ratio[:,None],100*(1-ratio)])
assert np.allclose(model.sum(axis=1),100)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
colors=['#369b77','#2879b9','#e09017','#e1e4e8']
fig,axs=plt.subplots(1,2,figsize=(13,6.6),sharey=True)
fig.subplots_adjust(left=.09,right=.98,top=.70,bottom=.34,wspace=.12)
y=np.arange(3)
for ax,data,title in zip(axs,[choices,model],['Published choice shares\nAmong voters in the reported categories','Earlier constrained reconstruction\nAs shares of the allocated electorate']):
 left=np.zeros(3)
 for j in range(data.shape[1]):
  ax.barh(y,data[:,j],left=left,height=.51,color=colors[j],edgecolor='white',linewidth=0 if j==2 else .9)
  for i,v in enumerate(data[:,j]):
   label=f'{v:.0f}%' if ax is axs[0] else f'{v:.1f}%'
   if v >= (3.5 if ax is axs[0] else 7):ax.text(left[i]+v/2,i,label,ha='center',va='center',color='#263441' if j in (2,3) else 'white',fontsize=10,weight='bold')
  left+=data[:,j]
 ax.set_xlim(0,100);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Share (%)');ax.set_title(title,fontsize=12,pad=16)
 ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
axs[0].set_yticks(y,['18–30 years','31–60 years','Over 60']);axs[0].set_ylim(2.65,-.5)
for i in range(3):
 axs[1].text(0,i+.40,f'Valid-category votes / allocated electorate: {100*ratio[i]:.1f}%',fontsize=9,color='#4b5863')
fig.suptitle('Candidate support and participation by age',x=.09,y=.98,ha='left',fontsize=20,weight='bold')
fig.text(.09,.92,'Historical reconstruction • rebuilt from the earlier rounded inputs',fontsize=12,color='#53616d')
fig.legend(handles=[Patch(color=c,label=l) for c,l in zip(colors,['Yotova','Gyurov','Neither','Residual: non-voters + invalid ballots*'])],loc='upper left',bbox_to_anchor=(.085,.875),ncol=4,frameon=False,fontsize=10)
fig.text(.09,.13,'*Residual within the earlier accounting model; not a verified abstention rate. The later audit withdraws precise turnout claims.\nAllocated electorate: 950,000 / 3,307,000 / 2,380,000; reconstructed valid-category votes: 67,000 / 702,000 / 1,131,000.\nRight-hand candidate shares retain the published within-age choice percentages. Small segments are left unlabelled.',fontsize=9,color='#4b5863',linespacing=1.6)
for ext in ['png','pdf','svg']:fig.savefig(P/f'generational_turnout_en.{ext}',dpi=180)
