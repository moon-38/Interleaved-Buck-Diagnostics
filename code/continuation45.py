"""Fixed current-budget and measured-residual guard comparisons."""
from pathlib import Path
import ctypes,subprocess,hashlib,json,time,concurrent.futures
import numpy as np,pandas as pd
from engine import PKEYS,POLICIES,default_params
from probe_controls42_engine import kernel as native_kernel,run as native_run
from probe_controls42 import configure,extra
from evaluation40 import plant as firstplant,make_noise
from fresh_evidence import plant as generator
from run_studies import D,atomic_json
HERE=D/'code';CACHE=D/'data/continuation45_cells';FN=None
def kernel():
 global FN
 if FN is not None:return FN
 native_kernel();s=(HERE/'probe_controls42_kernel.c').read_text()
 residual='''double mean_a=0,rss=0;
   for(int j=a0;j<a1;j++)mean_a+=out[(size_t)j*NC+5];mean_a/=(a1-a0);
   for(int j=a0;j<a1;j++){double y=0;for(int f=0;f<2;f++)y+=creal(a[f])*basis[(size_t)j*4+2*f]-cimag(a[f])*basis[(size_t)j*4+2*f+1];double e=out[(size_t)j*NC+5]-mean_a-y;rss+=e*e;}
   stats[12]=1000*sqrt(rss/(a1-a0));stats[13]=p[57]<0?-p[57]*stats[12]:p[57];
   if(stats[5]<stats[13])safe=0;'''
 for a,b in [('int simulate_probe42(','int simulate_cont45('),('cabs(b[f]-a[f])<.002','cabs(b[f]-a[f])<p[56]'),('if(stats[5]<8)safe=0;',residual)]:assert s.count(a)==1;s=s.replace(a,b)
 src=HERE/'continuation45_kernel.c';src.write_text(s);lib=HERE/'continuation45_kernel.so';subprocess.run(['gcc','-O2','-std=c99','-shared','-fPIC',str(src),'-o',str(lib),'-lm'],check=True)
 FN=ctypes.CDLL(str(lib)).simulate_cont45;FN.argtypes=[ctypes.c_int]*4+[ctypes.c_void_p]*6;FN.restype=ctypes.c_int;return FN
def run(p,pol,noise,warm,den,span):
 p={**default_params(),**p};noise=np.ascontiguousarray(noise,dtype=np.float64);N=len(noise);init=p.get('initial_state',[p['Vref']/(2*p['Rload']),p['Vref']/(2*p['Rload']),p['Vref']+p['initial_v_delta']]);g=p.get('nominal_gamma',[-1+0j]*2)
 values=[p[k] for k in PKEYS]+[p.get('calibration_scale',1.),p.get('fixed_early_scale',-1.)]+list(init)+[p.get('initial_prev2',-1.)]+[v for c in g for v in [complex(c).real,complex(c).imag]]+[p.get('Vin_observed',p['Vin']),float(warm),0.,0.,p.get('alpha_min',.45),p.get('alpha_max',1.8),den,span]
 ar=np.array(values,float);out=np.zeros((N,32));stats=np.zeros(14);jitter=np.zeros((N,2));ptr=lambda x:x.ctypes.data_as(ctypes.c_void_p);rc=kernel()(N,8,POLICIES[pol],1,ptr(ar),ptr(noise),ptr(out),ptr(stats),ctypes.c_void_p(),ptr(jitter));assert rc==0;return dict(p=p,out=out,stats=stats)
def tasks():
 a=[dict(study='budget',cohort=c,block=b,rho=r) for c in ['first','confirmation'] for r in [.8,.9] for b in range(1,201)];a += [dict(study='relative',cohort='first',block=b,rho=r,kappa=-k) for r in [.8,.9] for b in range(1,33) for k in [.05,.10,.20]];a += [dict(study='parity',cohort='first',block=1,rho=r,policy=p) for r in [.8,.9] for p in ['N','D','T']]
 for i,t in enumerate(a):t['case_id']=f'c45_{i:04d}'
 return a
def job(t):
 path=CACHE/(t['case_id']+'.json')
 if path.exists():return json.loads(path.read_text())['executions']
 b,r,c=t['block'],t['rho'],t['cohort'];p=firstplant(b,r) if c=='first' else generator(60000000+b,r);p['tick_ns']=1.
 if c=='first':noise=make_noise(p,b)
 else:
  noise=np.random.default_rng(102000000+b).standard_normal((50000,3,8));noise[:,0]*=p['noiseV'];noise[:,1:]*=p['noiseI']
 spec=[('N',.8,'fixed'),('N',.9,'fixed')]+[('D',beta,g) for beta in [1/3,2/3] for g in ['fixed','scaled']] if t['study']=='budget' else [('T',1.,'relative')] if t['study']=='relative' else [(t['policy'],1.,'fixed')]
 rows=[];n=0
 for label,beta,rule in spec:
  kap=t.get('kappa',-.20);q,pol,warm=configure(p,label,r,kap);q.update(alpha0=beta,fixed_early_scale=beta,calibration_scale=beta,target=.145*beta,alpha_min=.45*beta,alpha_max=1.8*beta);den=.002*beta if rule=='scaled' else .002*abs(kap)/.2 if rule=='relative' else .002;span=-4. if rule=='relative' else 8*beta if rule=='scaled' else 8.
  res=run(q,pol,noise,warm,den,span);n+=1;v=extra(res,dict(t,tick_ns=1.,variant='base'),label);v.update(budget=beta,guard_rule=rule,kappa=kap,denominator_guard_mV=1000*den,residual_sigma_mV=float(res['stats'][12]),span_guard_mV=float(res['stats'][13]));v['denominator_guard']=bool(v.get('deltaVmin_mV',float('inf'))>=1000*den);v['firstspan_guard']=bool(v.get('first_span_mV',0)>=res['stats'][13])
  if t['study']=='parity':
   old=native_run(q,pol,noise,warm=warm);n+=1;assert np.array_equal(res['out'],old['out']) and np.array_equal(res['stats'][:12],old['stats']);v['full_native_parity']=True
  rows.append(v)
 atomic_json(path,dict(meta=t,parameters=p,executions=n,metrics=rows));return n
def main():
 deps=['continuation45.py','probe_controls42.py','probe_controls42_engine.py','evaluation40.py','fresh_evidence.py','engine.py','closed_loop_kernel.c'];plan=dict(date='2026-10-26',tasks=tasks(),source_sha256={f:hashlib.sha256((HERE/f).read_bytes()).hexdigest() for f in deps},executions=5004,records=4998,budgets='Nominal.8/.9;Tune(-1)1/3and2/3 withfixed2/8mV or budget-scaled2beta/8beta guards;both existing independent200converterensembles,1ns,two ratios;all amplitudes/AGCbudgets scaled;step-.20.',relative='Same32,Tune(N),three negative steps. Initialspan>=4times firstwindow ADC residualRMS with DC/100/400Hz removed;denominator2abs(kappa)/.20mV. Empirical guard,not Gaussian false-acceptance bound.',statistics='Retain240/30originalfamilies;separate80budgetcontrastsperensemble,20000sharedconverterbootstrap,seeds105000045/106000045;no pooledN,equalinformationorstatisticalequivalence claim.')
 f=D/'review/continuation45_protocol.json'
 if f.exists():assert json.loads(f.read_text())==plan
 else:atomic_json(f,plan)
 kernel();CACHE.mkdir(exist_ok=True);tic=time.monotonic();n=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for i,k in enumerate(pool.map(job,plan['tasks']),1):
   n+=k
   if i%64==0:print(i,'/',len(plan['tasks']),n,'executions',round(time.monotonic()-tic,1),'s',flush=True)
 rows=[]
 for t in plan['tasks']:rows+=json.loads((CACHE/(t['case_id']+'.json')).read_text())['metrics']
 z=pd.DataFrame(rows);assert n==5004 and len(z)==4998 and z.positive_CCM.all();z.to_csv(D/'data/continuation45_metrics.csv',index=False,float_format='%.15g');atomic_json(D/'review/continuation45_execution.json',dict(new_executions=n,total_internal=28216,metric_records=len(z),seconds=time.monotonic()-tic));print('COMPLETED',n,flush=True)
if __name__=='__main__':main()
