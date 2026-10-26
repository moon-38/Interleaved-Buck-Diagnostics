"""Measured budget distributions, simultaneous paired contrasts and joint yield."""
import json,numpy as np,pandas as pd
from scipy.stats import beta
from run_studies import D,atomic_json
from analyze42 import summarise
Q=['late_tone_RMS_mV','late_Vac_mV','late_full_AC_RMS_mV','Qfull_mV','error_pct']
SPECS=[('D',1.,'fixed','N',.8,'fixed'),('D',1.,'fixed','N',.9,'fixed')]+[('D',b,r,'N',b,'fixed') for b in [1/3,2/3] for r in ['fixed','scaled']]+[('D',b,'scaled','D',b,'fixed') for b in [1/3,2/3]]
def sub(g,p,b,r):return g.query('policy==@p and abs(budget-@b)<1e-9 and guard_rule==@r').sort_values('block')
def main():
 new=pd.read_csv(D/'data/continuation45_metrics.csv');a=pd.read_csv(D/'data/article42_metrics.csv').query('tick_ns==1 and policy in ["N","D","B1","B2"]').assign(cohort='first');b=pd.read_csv(D/'data/probe_controls44_metrics.csv').query('study=="confirmation"').assign(cohort='confirmation');base=pd.concat([a,b],ignore_index=True);base['budget']=base.policy.map({'N':1.,'D':1.,'B1':1/3,'B2':2/3});base['policy']=base.policy.replace({'B1':'N','B2':'N'});base['guard_rule']='fixed';g=pd.concat([base,new.query('study=="budget"')],ignore_index=True);assert len(g)==8000 and not g.duplicated(['cohort','block','rho','policy','budget','guard_rule']).any();g.to_csv(D/'data/article45_records.csv',index=False,float_format='%.15g')
 rows=[]
 for (c,r,p,b,s),a in g.groupby(['cohort','rho','policy','budget','guard_rule']):rows.append(dict(cohort=c,rho=r,policy=p,budget=b,guard_rule=s,**summarise(a)))
 pd.DataFrame(rows).to_csv(D/'data/article45_summary.csv',index=False,float_format='%.15g');iv=[];families={}
 for c,seed in [('first',105000045),('confirmation',106000045)]:
  vec=[];keys=[]
  for rho in [.8,.9]:
   a=g.query('cohort==@c and rho==@rho')
   for p,b,r,pr,br,rr in SPECS:
    x=sub(a,p,b,r);y=sub(a,pr,br,rr);assert len(x)==200 and np.array_equal(x.block,y.block)
    for q in Q:vec.append(x[q].to_numpy()-y[q].to_numpy());keys.append(dict(cohort=c,rho=rho,policy=p,budget=b,guard_rule=r,reference=pr,reference_budget=br,reference_guard=rr,quantity=q))
  X=np.array(vec).T;assert X.shape==(200,80);mu=X.mean(0);se=X.std(0,ddof=1)/np.sqrt(200);rng=np.random.default_rng(seed);ix=rng.integers(0,200,(20000,200));w=np.array([np.bincount(t,minlength=200) for t in ix],float);crit=float(np.quantile(np.max(abs(w@X/200-mu)/se,axis=1),.95));families[c]=dict(size=80,seed=seed,replicates=20000,critical=crit)
  iv += [dict(**k,mean=float(mu[i]),lo=float(mu[i]-crit*se[i]),hi=float(mu[i]+crit*se[i]),standard_error=float(se[i]),critical=crit) for i,k in enumerate(keys)]
 pd.DataFrame(iv).to_csv(D/'data/article45_intervals.csv',index=False,float_format='%.15g');rr=[]
 for (rho,k),a in new.query('study=="relative"').groupby(['rho','kappa']):rr.append(dict(rho=rho,kappa=k,**summarise(a),span_guard_mV_mean=float(a.span_guard_mV.mean()),residual_sigma_mV_mean=float(a.residual_sigma_mV.mean())))
 pd.DataFrame(rr).to_csv(D/'data/article45_relative.csv',index=False,float_format='%.15g');ff=[]
 for (c,r,p,b,s),a in g.groupby(['cohort','rho','policy','budget','guard_rule']):
  for am,qm in [(1.,8.),(1.,13.),(1.75,8.)]:
   ok=a.valid.eq(True)&a.positive_CCM.eq(True)&a.error_pct.le(.85)&a.late_tone_RMS_mV.le(am)&a.Qfull_mV.le(qm);k=int(ok.sum());ff.append(dict(cohort=c,rho=r,policy=p,budget=b,guard_rule=s,Emax=.85,Amax=am,Qmax=qm,feasible=k,N=200,lo=float(beta.ppf(.025,k,201-k)) if k else 0.,hi=float(beta.ppf(.975,k+1,200-k)) if k<200 else 1.))
 pd.DataFrame(ff).to_csv(D/'data/article45_feasibility.csv',index=False,float_format='%.15g');atomic_json(D/'review/article45_analysis.json',dict(records=8000,independent_N=[200,200],retained_families=[240,30],extension_families=families,total_retained_run_ledger=28216))
 print(pd.DataFrame(rows).query('cohort=="first"')[['rho','policy','budget','guard_rule','error_pct_mean','error_pct_median','passes','accepted','late_tone_RMS_mV_mean','Qfull_mV_mean']].to_string(index=False));print(pd.DataFrame(rr)[['rho','kappa','accepted','Qfull_mV_mean']].to_string(index=False))
if __name__=='__main__':main()
