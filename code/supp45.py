"""Supporting results: complete current grids and source-identified verification."""
import json
import pandas as pd
from run_studies import D
from build_supplement40 import table
from build_article41 import num
from edit45 import bet
def page(t):return '\n\\clearpage\n\\heading{'+t+'}\n'
def main():
 s=(D/'reference/retained_supplement.tex').read_text();a=s.index(r'\heading{S1.');b=s.index(r'\heading{S1. Actual-component',a)
 intro=r'''\heading{S1. Ensembles and retained execution ledger}
Two independent ensembles each contain 200 converter draws. Component/noise seeds are $91000000+b$/$92000000+b$ and $101000000+b$/$102000000+b$, $b=1,\ldots,200$. A converter/noise history is shared across its ratios and protocols. Repeated settings do not increase independent sample size. Development uses separate $41000000+b$/$42000000+b$ streams.
''';rows=[r'Development & $3200+1280+1248$ & 5728\\',r'Base evaluation & $4800+768+256+576$ & 6400\\',r'Protocol controls & $800+384+384+256$ & 1824\\',r'Amplitude/numerical controls & $2400+1600+1024+384+960+768$ & 7136\\',r'Step-scaled denominator & $32(2\rho)(2\mathrm{starts})(4\mathrm{steps})$ & 512\\',r'Separate reference ensemble & $200(2\rho)(4\mathrm{protocols})$ & 1600\\',r'Denominator-kernel checks & $2\rho(3\mathrm{protocols})(2\mathrm{implementations})$ & 12\\',r'Budget extension & $2\mathrm{ensembles}(200)(2\rho)(6\mathrm{settings})$ & 4800\\',r'Residual-span guard & $32(2\rho)(3\mathrm{steps})$ & 192\\',r'Span-kernel checks & $2\rho(3\mathrm{protocols})(2\mathrm{implementations})$ & 12\\',r'Retained total & $23212+4800+192+12$ & 28216\\'];intro+=table('Retained study/replay executions. Two-kernel checks execute both implementations. Identical recovery reruns are not additional study records. Short closed-loop implementation pairs and sixteen ngspice runs are separate.','Dataset & Factorization & Executions',rows,'llr','tab:ledger')
 intro+=r'''The current 1-ns grid has 4000 records per ensemble: five Nominal budgets and five Tune($-1$) budget/guard points at both ratios. Native points are reused. The extension adds Nominal budgets 0.8/0.9 and four lower-budget tuning settings in 800 ensemble/converter/ratio combinations, giving 4800 executions. Initial amplitude, both learning windows, AGC target and bounds scale together.

The operating-point table has $32(2\rho)(3\mathrm{settings})(2\mathrm{timers})(3\mathrm{protocols})=1152$ records. Only 192 Tune($-1$) records at 10 ns are reused from the environment study, whose two protocols are Informed and Tune($-1$). No probe and Nominal require 384 executions at 10 ns; all three require 576 at 1 ns. Thus 960 executions produce 1152 records. The six environment settings are 19.2/28.8-V targets, 3-$\Omega$ load, zero capacitor ESR, zero ESR with ADC TPDF, and native ESR with ADC TPDF.

Source specifications, individual parameters, unrounded metrics and byte digests accompany the software. Ordinary runs last 1 s (50000 periods); delayed-start controls analyze a shifted second. The execution ledger is distinct from independent sample size.
\clearpage
''';s=s[:a]+intro+s[b:];at=s.index(r'\heading{S3.');r=[];z=pd.read_csv(D/'data/article42_summary.csv')
 for rho in [.8,.9]:
  for pol,label in [('off','No probe'),('F','Opposite'),('N','Nominal'),('K','Informed'),('D',r'Tune($-1$)'),('T','Tune(N)')]:
   x=z.query('tick_ns==1 and rho==@rho and policy==@pol').iloc[0];r.append(f'{rho:.1f} & {label} & '+' & '.join(num(x[q+'_mean'],3) for q in ['late_tone_RMS_mV','late_Vac_mV','late_full_AC_RMS_mV','Qfull_mV'])+' & '+('---' if pol=='off' else num(x.error_pct_mean,3))+r'\\')
 new='\n\\heading{S2. Native-budget references at 1 ns}\n'+table('Complete first-ensemble native means. Output is mV and error is percent; Informed requires actual components.',r'$\rho_0$ & Protocol & Tone & Cycle AC & Full AC & Full $Q$ & $E_L$',r,'clrrrrr','tab:nativefine');s=s[:at]+new+'\n\\clearpage\n'+s[at:]
 a=s.index('Stored-gain and finite-search controls remain');b=s.index('\n\n',a);s=s[:a]+'Coefficient-storage and finite-static-search datasets accompany the software. Float32 and signed Q4.12 affect only stored coefficients. The static in-record search is descriptive, rather than an independently validated online rule.'+s[b:];s=s.replace('The environment CSV also retains','The environment dataset includes')
 at=s.index(r'\heading{S5.');r=[];rel=pd.read_csv(D/'data/article45_relative.csv');old=pd.read_csv(D/'data/article44_guards.csv')
 for _,x in rel.sort_values(['rho','kappa'],ascending=[True,False]).iterrows():
  a=old.query('rho==@x.rho and policy=="T" and abs(kappa-@x.kappa)<1e-8 and guard_rule=="scaled"').iloc[0];r.append(f'{x.rho:.1f} & {abs(x.kappa):.2f} & {int(a.accepted)}/32 & {int(x.accepted)}/32 & {num(x.span_guard_mV_mean,2)} & {num(x.late_tone_RMS_mV_mean,2)} & {num(x.Qfull_mV_mean,2)}'+r'\\')
 new=page('S4. Relative initial signal and perturbation reference')+r'''For Tune(N), $S_1\geq4\sigma_{\rm res}$ uses first-window ADC period-mean RMS after DC and fitted 100/400-Hz terms are removed. The residual includes quantized-feedback distortion and noise; multiplier four is an empirical sensitivity setting, not a Gaussian false-acceptance bound. The denominator guard is $2|\kappa|/0.20$ mV and ratio bounds are unchanged. All rows use the same 32 converters, 1 ns and native amplitude.
'''+table('Relative-span control. Both acceptance columns use the step-scaled denominator guard. Threshold/tone/peak are mean mV.',r'$\rho_0$ & $|\kappa|$ & 8-mV count & Relative count & Threshold & Tone & Full $Q$',r,'rrllrrr','tab:relative')
 new+=r'''The $+0.35$ reference changes $-1$ to $-0.65$ in the second window; amplitude, guards, timing and AGC are otherwise unchanged. Both sign and magnitude differ from $-0.20$, so this is not a sign-only causal test. Its contrast with Informed remains in the 240-comparison family. The table shows its purpose: similar final tone can accompany different acquisition excursion.
''';r=[]
 for tick in [10.,1.]:
  for rho in [.8,.9]:
   for pol,k in [('C',.35),('D',-.2)]:
    x=z.query('tick_ns==@tick and rho==@rho and policy==@pol').iloc[0];r.append(f'{tick:.0f} & {rho:.1f} & {k:+.2f} & {int(x.accepted)}/200 & {num(x.late_tone_RMS_mV_mean,3)} & {num(x.Qfull_mV_mean,2)}'+r'\\')
 new+=table('Perturbation references, first200converters. Tone and excursion are mean mV.',r'ns & $\rho_0$ & Step & Accepted & Tone & Full $Q$',r,'rrrlrr','tab:direction');s=s[:at]+new+'\n\\clearpage\n'+s[at:]
 a=s.index(r'\heading{S5.');b=s.index(r'\heading{S6.',a);new=r'''\heading{S5. Circuit-engine propagation and solver sensitivity}
Four prescribed-gate circuits are executed in ngspice-42 (Ubuntu 42+ds-3build1, KLU). Reference values are unquantized instantaneous voltage and currents from the C99 event-aligned RK4 model, at eight nodes per 20-$\mu$s period. They are model states, not hardware measurements or an analytical solution. Components, saved initial state and gate/deadtime history are shared. External PWL edges are 0.2 ns; RK4 uses ideal switching events.

Cases 01/02/04 last 2 ms with maximum steps 20/10 ns; case03 lasts 20 ms with 100/50 ns. Case01 uses ideal switches; cases02/03 use the conduction/deadtime/ESR law; case04 spans a ratio step. Explicit initial voltages and UIC impose $v_o(0)=[v_c(0)+R_C(i_1(0)+i_2(0))]/(1+R_C/R)$. The engine starts after zero; that unavailable node is excluded without extrapolation. Each eight-run profile compares 20792 positive reference nodes.

Profile T uses trapezoidal integration, \texttt{reltol=1e-9}, \texttt{abstol=1e-12} A, \texttt{vntol=1e-11} V and \texttt{trtol=1}. Profile G uses Gear order2, \texttt{reltol=1e-6}, \texttt{abstol=1e-10} A and \texttt{vntol=1e-8} V. Both disable plot-window decimation and export seventeen-digit values. Version output, input/binary hashes, exact commands, full solver logs and all compared values accompany the software.
''';r=[]
 for file,tag in [('ngspice44_strict_result.json','T'),('ngspice44_result.json','G')]:
  for x in json.loads((D/'review'/file).read_text())['rows']:r.append(f'{tag} & {x["case"][:2]} & {x["step_ns"]} & {x["reference_comparisons"]} & {num(x["max_voltage_error_mV"],6)} & {num(x["max_current_error_mA"],6)}'+r'\\')
 new+=table('Both logged profiles: maximum absolute voltage (mV) and current (mA) differences; current is the larger phase difference.','Profile & Case & Max step, ns & Nodes & Voltage & Current',r,'crrrrr','tab:loggedspice')+r'''Profile T gives maxima 0.002232 mV and 0.012746 mA; G gives 0.147343 mV and 0.389180 mA. The latter is appreciable relative to sub-mV tones. Method and tolerances change together, so a method-only effect is not isolated. No monotone convergence or asymptotic order is inferred from two timesteps. The replays verify prescribed power-stage propagation, not external digital feedback, device validity or hardware.
\clearpage
''';s=s[:a]+new+s[b:];s=s[:s.index(r'\heading{S6.')];z=pd.read_csv(D/'data/article45_summary.csv');meta=json.loads((D/'review/article45_analysis.json').read_text())
 for cohort,label in [('first','first ensemble'),('confirmation','independent ensemble')]:
  s+=page('S6. Measured budget grid: '+label)+r'''Each row has 200 converters at 1 ns. Tune($-1$) uses $\kappa=-0.20$. Fixed guards are2/8 mV; Budget guards are$2\beta$/$8\beta$ mV. Initial/learning-window amplitudes and AGC targets/bounds scale together. Native tuning is shared by both rules. Valid counts apply observer validity and the unrounded1\% threshold. Means and medians describe different features of the error distribution.
''';r=[]
  for _,x in z.query('cohort==@cohort').sort_values(['rho','policy','budget','guard_rule'],ascending=[True,False,True,True]).iterrows():
   lab='Nominal' if x.policy=='N' else r'Tune($-1$)';rule='---' if x.policy=='N' else 'Budget' if x.guard_rule=='scaled' else 'Fixed';acc='---' if x.policy=='N' else f'{int(x.accepted)}/200';r.append(f'{x.rho:.1f} & {lab} & {bet(x.budget)} & {rule} & {num(x.error_pct_mean,3)} & {num(x.error_pct_median,3)} & {int(x.passes)}/200 & {acc} & {num(x.late_tone_RMS_mV_mean,3)} & {num(x.Qfull_mV_mean,3)}'+r'\\')
  s+=table('Error in percent; tone and full excursion are mean mV.',r'$\rho_0$ & Protocol & $\beta$ & Guard & Mean $E_L$ & Median & Valid & Update & Tone & Full $Q$',r,'clrlrrllrr','tab:grid'+cohort);fam=meta['extension_families'][cohort];s+=f'The separate80-contrast family uses20000 shared-converter bootstrap replicates, seed{fam["seed"]}, critical value{fam["critical"]:.6f}. Eight contrasts at two ratios cover four output metrics and continuous error. Unrounded intervals accompany the dataset. The240-and30-contrast reference families remain intact.\n'
 s+=page('S6. Converter-wise joint feasibility')+r'''A feasible converter requires valid positive estimates, positive-current operation, $E_L\leq0.85\%$ and the stated tone/excursion limits. These fixed examples are not application requirements or optimized winner-selection rules. Informed is excluded because it uses actual components. Marginal exact-binomial intervals accompany the dataset; counts are descriptive rather than simultaneous comparison tests.
''';r=[];f=pd.read_csv(D/'data/article45_feasibility.csv')
 for cohort,cl in [('first','First'),('confirmation','Independent')]:
  for (rho,p,b,gr),a in f.query('cohort==@cohort').groupby(['rho','policy','budget','guard_rule']):
   kk=[int(a.query('Amax==@am and Qmax==@qm').iloc[0].feasible) for am,qm in [(1.,8.),(1.,13.),(1.75,8.)]];lab='Nominal' if p=='N' else r'Tune($-1$)';gl='---' if p=='N' else 'B' if gr=='scaled' else 'F';r.append(f'{cl} & {rho:.1f} & {lab} & '+bet(b)+f' & {gl} & '+' & '.join(f'{k}/200' for k in kk)+r'\\')
 s+=table(r'Joint counts with $E_L\leq0.85\%$. Limits are(tone mV, full Q mV); F/B are fixed/budget-scaled guards.',r'Ensemble & $\rho_0$ & Protocol & $\beta$ & Guard & (1,8) & (1,13) & (1.75,8)',r,'lclrrlll','tab:joint')+r'\end{document}'+'\n'
 s=s.replace(page('S4. Step-size controls, continued'),'\n\\heading{S4. Step-size controls, continued}\n')
 for a,b in [('first200','first 200'),('case03','case 03'),('case01','case 01'),('cases02/03','cases 02/03'),('case04','case 04'),('order2','order 2'),('are2/8','are 2/8'),('are$','are $'),('unrounded1','unrounded 1'),('separate80','separate 80'),('uses20000','uses 20000'),('seed105','seed 105'),('seed106','seed 106'),('value3','value 3'),('value4','value 4'),('The240-and30','The 240- and 30')]:s=s.replace(a,b)
 assert all(x not in s for x in ['user-supplied','user-reported','physical reference nodes','parity driver','review/ngspice44_strict']);(D/'output/Interleaved_Buck_Supplementary_Material.tex').write_text(s);print('Revised supplement')
if __name__=='__main__':main()
