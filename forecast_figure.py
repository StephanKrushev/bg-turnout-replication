"""16:00 frozen forecast; exact hourly RNG compatibility with q=0 reproduction.
Intermediate report draws use a separate RNG. Bands are pointwise conditional
quantiles, averaged across seeds, not calibrated confidence bands.
"""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from turnout_filter import P, base, obs, run
results={};closing=[]
for cut in [12,14,16,18]:
 runs=[run(cut,seed) for seed in [418,419,420]]
 rows=np.mean([r[0] for r in runs],axis=0);sc=np.mean([r[1] for r in runs],axis=0)
 results[str(cut)]={'path':rows.tolist(),'scale_quantiles':sc.tolist()};closing.append([cut,*rows[-1,1:]])
# Saved q=0 result at 18:00 from 16:00, same particle/RNG protocol.
r16=np.array(results['16']['path']);i=np.argmin(abs(r16[:,0]-18))
assert abs(r16[i,2]-23.8149)<.002
assert np.all(r16[:,1]<=r16[:,2]) and np.all(r16[:,2]<=r16[:,3])
assert np.all(np.diff(r16[:,2])>=-1e-10)
(P/'forecast_figure_results.json').write_text(json.dumps({'model':'q=0 baseline','seeds':[418,419,420],'particles_per_seed':40000,'conditional_on_fixed_reference':True,'columns':['hour','latent_p05','latent_median','latent_p95','report_p05','report_p95'],'cutoffs':results},indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
fig=plt.figure(figsize=(13,9),facecolor='white');gs=fig.add_gridspec(2,2,width_ratios=[3.1,1.5],height_ratios=[2.1,1],hspace=.48,wspace=.27)
ax=fig.add_subplot(gs[0,0]);mini=fig.add_subplot(gs[1,0]);info=fig.add_subplot(gs[:,1]);info.axis('off')
blue='#236aa0';gold='#aa5821'
ax.plot(np.arange(8,21),100*base,color='#92999f',lw=1.7,label='Round 1: timing reference')
ax.fill_between(r16[:,0],r16[:,4],r16[:,5],color='#cfe3f2',label='90%: future reported observation')
ax.fill_between(r16[:,0],r16[:,1],r16[:,3],color='#78aed2',alpha=.9,label='90%: latent turnout')
ax.plot(r16[:,0],r16[:,2],color=blue,lw=2.3,label='Median forecast from 16:00')
ax.scatter(np.arange(8,17),100*obs[:9],c='#172c3a',s=30,label='Round 2: assimilated observations',zorder=5)
ax.scatter([17,18],100*obs[9:],facecolors='white',edgecolors=gold,s=58,lw=1.8,label='Later estimates (not assimilated)',zorder=6)
ax.scatter([20],[28.67],marker='D',color=gold,s=65,zorder=7,label='CIK: published closing turnout')
ax.axvline(16,color=blue,ls='--',lw=1)
ax.text(15.88,1,'Data cutoff: 16:00',rotation=90,ha='right',va='bottom',color=blue,fontsize=10)
ax.set(xlim=(7.8,20.5),ylim=(0,33),xticks=np.arange(8,21,2),ylabel='Turnout (%)',xlabel='Hour',title='Round 2 forecast using data only through 16:00')
ax.legend(loc='upper left',fontsize=8.2,framealpha=.96);ax.grid(alpha=.18)
c=np.array(closing)
mini.vlines(c[:,0],c[:,4],c[:,5],color='#bfd9ed',lw=12,label='90% reported observation')
mini.vlines(c[:,0],c[:,1],c[:,3],color='#5a98c3',lw=5,label='90% latent turnout')
mini.plot(c[:,0],c[:,2],'o-',color=blue,ms=5,label='Median')
mini.axhline(28.67,color=gold,ls='--',lw=1.3)
mini.text(18.22,28.67,'CIK\n28.67%',va='center',fontsize=9,color=gold)
mini.set(xlim=(11.5,19.2),xticks=[12,14,16,18],xlabel='Last observation hour used',ylabel='Forecast for 20:00 (%)',title='Closing forecast as observations arrive',ylim=(20,32));mini.grid(alpha=.18)
end=r16[-1];sc=results['16']['scale_quantiles']
info.text(0,1,'MODEL AND PARAMETERS',weight='bold',fontsize=12,va='top',color='#172c3a')
text=("dT = (1 − T) h dt\nh = h₁(t) exp(X)\ndX = (θ − X) dt/τ + s√(2/τ) dW\n\n"
      "Round 1 determines h₁(t).\nThe reference is treated as exact.\n\n"
      "ASSUMED, NOT ESTIMATED\nFROM ROUND 1\n"
      "• Correlation time τ = 2 h\n• Stationary SD of X given θ: 0.15\n  Var(X | θ) = 0.0225\n• Reporting-error SD:\n  0.5 percentage points\n• q = 0: constant θ\n\n"
      "INITIAL DISTRIBUTIONS\nθ ~ N(log(1.2), 0.25²)\nX(08) | θ ~ N(θ, 0.15²)\nT(08) = 0.8%\n\n"
      f"UPDATED THROUGH 16:00\nBaseline multiplier exp(θ): {sc[1]:.2f}\n90% range: {sc[0]:.2f}–{sc[2]:.2f}\n\n"
      f"FORECAST FOR 20:00\nMedian: {end[2]:.2f}%\nLatent: {end[1]:.2f}–{end[3]:.2f}%\nReported: {end[4]:.2f}–{end[5]:.2f}%")
info.text(0,.94,text,va='top',fontsize=10,linespacing=1.45,color='#243746')
fig.suptitle('Turnout forecast and conditional uncertainty',x=.08,ha='left',y=.98,weight='bold',fontsize=19)
fig.text(.08,.936,'Bulgaria • Round 2 • retrospective reconstruction using observations through 16:00',fontsize=11,color='#53616d')
fig.subplots_adjust(left=.08,right=.98,top=.88,bottom=.16)
fig.text(.08,.085,'Bands are pointwise 5–95% quantiles conditional on the model, not empirically calibrated confidence intervals.\nThey exclude round-1 uncertainty, systematic agency differences and coverage differences relative to CIK.\n40,000 particles × 3 random seeds; 5-minute steps. Quantiles are averaged across the three runs.',fontsize=9,color='#53616d',va='top',linespacing=1.5)
fig.savefig(P/'turnout_forecast_16h_en.png',dpi=180)
fig.savefig(P/'turnout_forecast_16h_en.svg')
print('Forecast16 final:',end.tolist());print('closing by cutoff:',closing)

fig.savefig(P/'turnout_forecast_16h_en.pdf')
