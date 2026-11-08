import numpy as np
base=np.array([1.1,2.4,4.4,6.6,9.1,11.3,13.4,15,16.04,18.3,19.8,21.3,22.98])/100
obs=np.array([.8,2.1,4.1,6.8,9.5,12.2,14.9,17.2,19.8,21.5,24])/100
haz=-np.diff(np.log1p(-base))
def run(cut,seed,q,N=40000):
 rng=np.random.default_rng(seed);T=np.full(N,obs[0]);theta=rng.normal(np.log(1.2),.25,N);z=rng.normal(0,.15,N);out={};esslast=None
 for hour in range(9,21):
  for j in range(12):
   a=np.exp(-1/24)
   z=a*z+.15*np.sqrt(1-a*a)*rng.normal(size=N)
   if q:theta+=q*np.sqrt(1/12)*rng.normal(size=N)
   T=1-(1-T)*np.exp(-haz[hour-9]*np.exp(theta+z)/12)
  if hour<=cut:
   lw=-.5*((T-obs[hour-8])/.005)**2;lw-=lw.max();w=np.exp(lw);w/=w.sum();esslast=1/np.sum(w*w)/N
   idx=np.searchsorted(np.cumsum(w),(rng.random()+np.arange(N))/N);T=T[idx];theta=theta[idx];z=z[idx]
  pred=T+rng.normal(0,.005,N) if hour>cut else T
  out[hour]=(np.median(T)*100,np.quantile(pred,[.05,.95])*100)
 return out,esslast
for q in [0,.03,.06,.10]:
 errors=[];covers=[];widths=[];rows=[]
 for cut in [10,12,14,16]:
  rr=[run(cut,s,q) for s in [418,419,420]];h=cut+2
  m=np.mean([r[0][h][0] for r in rr]);ci=np.mean([r[0][h][1] for r in rr],axis=0);actual=obs[h-8]*100
  errors.append(m-actual);covers.append(ci[0]<=actual<=ci[1]);widths.append(ci[1]-ci[0]);rows.append([cut,round(m,3),np.round(ci,3).tolist(),round(np.mean([r[1] for r in rr]),3)])
 rr=[run(18,s,q) for s in [418,419,420]]
 print('q',q,'rows',rows,'MAE',np.mean(np.abs(errors)),'RMSE',np.sqrt(np.mean(np.array(errors)**2)),'coverage',sum(covers),'meanwidth',np.mean(widths),'final',np.mean([r[0][20][0] for r in rr]),np.mean([r[0][20][1] for r in rr],axis=0))

for name in ['scaling', 'linear']:
 predictions=[]
 actual=[]
 for cut in [10,12,14,16]:
  i=cut-8
  predictions.append((obs[i]*base[i+2]/base[i] if name=='scaling' else 2*obs[i]-obs[i-2])*100)
  actual.append(obs[i+2]*100)
 err=np.array(predictions)-actual
 print(name,'predictions',predictions,'MAE',np.mean(abs(err)),'RMSE',np.sqrt(np.mean(err**2)))
