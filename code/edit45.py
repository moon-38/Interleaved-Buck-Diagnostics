"""Concise IEEE-style revision from retained sources and unrounded results."""
import re,json
import pandas as pd
from run_studies import D
from build_article41 import table,num,ci
def bet(b):return r'$1/3$' if abs(b-1/3)<1e-8 else r'$2/3$' if abs(b-2/3)<1e-8 else f'${b:g}$'
def swap(s,label,new):
 a=s.index(r'\label{'+label+'}');l=s.rfind(r'\begin{table',0,a);env='table*' if s.startswith(r'\begin{table*}',l) else 'table';end=r'\end{'+env+'}';r=s.index(end,a)+len(end);return s[:l]+new+s[r:]
def main():
 s=(D/'reference/retained_main.tex').read_text();z=pd.read_csv(D/'data/article45_summary.csv');iv=pd.read_csv(D/'data/article45_intervals.csv')
 abstract=r'''\begin{abstract}
Online converter observation requires excitation that can introduce output-voltage tones and transient excursions. This simulation study compares fixed nominal probes with two-window phase-ratio tuning in a two-phase buck converter, using two independent ensembles of 200 component draws. Current budget and acceptance guards are varied. At nominal inductance ratio $L_{1,n}/L_{2,n}=0.8$ and 1-ns pulse-width modulation, native-budget Tune($-1$) and a two-thirds-budget nominal probe have mean maximum inductance errors of 0.80\% and 0.79\%, but valid 1\% observation counts of 133/200 and 140/200. Tuning reduces tone root-mean-square (RMS) output from 1.74 to 0.40 mV while increasing the full cycle-mean excursion from 5.90 to 12.38 mV. Its running excursion after 0.14 s is smaller; the preceding post-update interval retains a transient. Measured intermediate nominal budgets at ratio 0.9 distinguish mean error from threshold success. Lower-budget tuning demonstrates that the acquisition penalty depends on amplitude and guards. Starting at $-1$ imposes an entry-excursion floor, whereas nominal-start tuning is sensitive to step size and the initial-signal guard. A signal-to-residual guard tests this acceptance effect at a fixed start. Separate-ensemble comparisons and logged circuit-engine replays support the numerical assessment. The contribution is a budget-dependent comparison of tone, observation-error distributions and acquisition versus running excursions, with converter-wise joint-feasibility examples. Hardware validation remains necessary.
\end{abstract}'''
 s=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:abstract,s,flags=re.S)
 s=s.replace('at three current budgets','at five current budgets').replace('The comparison separates an acquisition excursion from the output cost of continued observation and tests whether amplitude reduction offers the same error level. It provides a probe-selection assessment with a fixed observer.','The comparison distinguishes acquisition from running excursions and assesses amplitude reduction with the same observer.')
 s=s.replace('Learning windows use $\\alpha=1$.','Native-budget learning windows use $\\alpha=1$.').replace('The additional $+0.35$ reference uses the same $-1$ start, windows and guards with $\\kappa=+0.35$.','The $+0.35$ reference starts at $-1$ with the same native amplitude, windows and guards. Its response is reported in Supplement S4, and its contrast is retained in the statistical family.')
 at=s.index('At native amplitude, phase-1 tones');s=s[:at]+r'''At 1 ns, Nominal budgets are $\beta\in\{1/3,2/3,0.8,0.9,1\}$. Tune($-1$) uses $\beta\in\{1/3,2/3,1\}$, scaling both learning-window amplitudes, initial amplitude, AGC target and bounds. Lower-budget tuning is tested with fixed voltage guards (2/8 mV) and budget-scaled guards ($2\beta$/$8\beta$ mV). The ratio step remains $-0.20$.

'''+s[at:]
 s=s.replace('It tests Nominal at budgets 1/3, 2/3 and 1, and Tune($-1$), at 1 ns and both ratios, without selecting new parameters.','It tests the same 1-ns budget/guard grid at both ratios. Settings are fixed across converters.')
 a=s.index('The first ensemble contains $200');b=s.index('Tables report arithmetic means',a);s=s[:a]+r'''The 1-ns budget grid has 4000 records per ensemble, with independent sample size 200 in each. Repeated budgets and ratios do not increase this size. The retained internal study/replay ledger contains 28216 executions (Supplement S1); short implementation checks and sixteen circuit-engine runs are separate.

'''+s[b:]
 s=s.replace('Confirmation uses its own 30-contrast family: Tune($-1$) minus each Nominal budget, at two ratios, for the four output outcomes and continuous $E_L$. The families are not pooled.','Confirmation has its own 30-contrast family. Budget extensions add a separate 80-contrast family per ensemble: eight contrasts, two ratios and five outcomes (four output metrics and continuous $E_L$). Shared converter-index resampling preserves dependence. Ensembles and families are not pooled.')
 s=s.replace('Table~\\ref{tab:main} shows the 1-ns comparison; the complete 10-ns counterpart is Table S3 in Supplement S2.','Table~\\ref{tab:main} gives the 1-ns budget grid. Supplement S2 gives native-budget references and the complete 10-ns comparison.')
 rows=[]
 for rho in [.8,.9]:
  for _,x in z.query('cohort=="first" and rho==@rho').sort_values(['policy','budget','guard_rule'],ascending=[False,True,True]).iterrows():
   label='Nominal' if x.policy=='N' else r'Tune($-1$)';rule='---' if x.policy=='N' else 'Budget' if x.guard_rule=='scaled' else 'Fixed';rows.append(f'{rho:.1f} & {label} & {bet(x.budget)} & {rule} & '+num(x.late_tone_RMS_mV_mean)+' & '+num(x.late_full_AC_RMS_mV_mean)+' & '+num(x.error_pct_mean,2)+' & '+num(x.error_pct_median,2)+f' & {int(x.passes)}/200 & '+num(x.Qfull_mV_mean,2)+r'\\')
 s=swap(s,'tab:main',table(r'1-ns budget grid, first 200 converters. Output is mean mV; $E_L$ mean/median are percent. Valid counts enforce the unrounded 1\% threshold. Fixed guards are 2/8 mV; Budget guards scale with $\beta$. Nominal has no update guard. Percent changes use unrounded data.',r'$\rho_0$ & Protocol & $\beta$ & Guard & $A$ & Full AC & Mean $E_L$ & Median $E_L$ & Valid & Full $Q$',rows,'clrlrrrrlr','tab:main'))
 a=s.index(r'\subsection{Amplitude, observation error and acquisition margin}');b=s.index(r'\subsection{Where the excursion occurs',a)
 part=r'''\subsection{Current budget and observation-error distribution}
Figure~\ref{fig:budget} shows the measured budget responses. At $\rho_0=0.8$, native Tune($-1$) and 2/3-budget Nominal have mean $E_L=0.80\%$ and $0.79\%$, but medians 0.85\% and 0.77\% and valid counts 133/200 and 140/200. Tone RMS is 0.398 versus 1.743 mV and full $Q$ is 12.38 versus 5.90 mV. Similar means do not imply equal distributions or equal information. Against 1/3-budget Nominal, the native learned tone change is $-0.49$ [$-0.59,-0.39$] mV at ratio 0.8 and $-0.17$ [$-0.35,+0.02$] mV at 0.9; only the latter interval includes zero.

At ratio 0.9, measured Nominal budgets 0.8/0.9 have mean $E_L=1.174/1.094\%$, versus 1.150\% for native tuning. Valid counts are 103/200, 107/200 and 105/200, respectively. Tune($-1$) minus 0.8-budget Nominal changes mean error by @@E@@ percentage points, tone by @@A@@ mV and full $Q$ by @@Q@@ mV. These points do not establish statistical equivalence.

\begin{figure*}[!t]\centering\includegraphics[width=\textwidth]{fresh_physical.pdf}
\caption{Measured 1-ns budget grid. Mean error versus tone and full $Q$ versus budget are shown on the first ensemble. Fixed and budget-scaled guards coincide at $\beta=1$. Lines connect tested points and are not a Pareto frontier or interpolated accuracy match.}\label{fig:budget}\end{figure*}

At 1/3 budget, fixed guards accept 0/200 and 2/200 updates at ratios 0.8 and 0.9; budget-scaled guards accept 199/200 and 197/200. At 0.8 the latter gives mean $E_L=0.98\%$, 121/200 valid results, 0.369-mV tone and full $Q=5.44$ mV. Same-budget Nominal gives 0.99\%, 128/200, 0.888 mV and 4.28 mV. Amplitude reduction changes both excitation and update success.

The independent ensemble retains the tone--excursion tradeoff (Table~\ref{tab:confirmation}). At ratio 0.9, native tuning minus 0.8-budget Nominal changes mean error by @@CE@@ percentage points, again with an interval including zero. Complete distributions, counts and intervals are in Supplement S6.
@@TABLE@@
Joint feasibility is evaluated per converter. With illustrative limits $E_L\leq0.85\%$, $A\leq1$ mV and full $Q\leq8$ mV, budget-scaled 1/3-budget tuning satisfies all limits in 94/200 and 65/200 converters; 1/3-budget Nominal gives 80/200 and 33/200. Native tuning gives 0/200 and 9/200. These fixed examples are not application requirements. Supplement S6 gives all fractions and marginal intervals. Informed is excluded because it requires actual components.

Fixed-$\alpha$ controls without AGC retain tone reduction (Supplement S3); different AGC gains alone do not explain the ratio effect. Current-budget matching does not equate Fisher information.

'''
 def interval(c,q):return iv.query('cohort==@c and rho==.9 and budget==1 and abs(reference_budget-.8)<1e-8 and quantity==@q').iloc[0]
 for k,q in [('E','error_pct'),('A','late_tone_RMS_mV'),('Q','Qfull_mV')]:part=part.replace('@@'+k+'@@',ci(interval('first',q),2))
 part=part.replace('@@CE@@',ci(interval('confirmation','error_pct'),2));rr=[]
 for rho in [.8,.9]:
  for pol,bb in [('N',2/3),('N',.8),('N',.9),('D',1.)]:
   x=z.query('cohort=="confirmation" and rho==@rho and policy==@pol and abs(budget-@bb)<1e-8 and guard_rule=="fixed"').iloc[0];rr.append(f'{rho:.1f} & '+('Nominal' if pol=='N' else r'Tune($-1$)')+' & '+bet(bb)+' & '+num(x.error_pct_mean,2)+f' & {int(x.passes)}/200 & '+num(x.late_tone_RMS_mV_mean,2)+' & '+num(x.Qfull_mV_mean,2)+r'\\')
 small=table('Independent 200-converter ensemble, 1 ns. Mean error (percent), tone and full excursion (mV); counts enforce valid 1 percent. Complete grid: Supplement S6.',r'$\rho_0$ & Protocol & $\beta$ & $E_L$ & Valid & $A$ & Full $Q$',rr,'clrrlrr','tab:confirmation',wide=False).replace(r'\centering',r'\centering\setlength{\tabcolsep}{2pt}');s=s[:a]+part.replace('@@TABLE@@',small)+s[b:]
 a=s.index('Figure~\\ref{fig:step} compares');b=s.index(r'\begin{figure*}',a);s=s[:a]+r'''Figure~\ref{fig:step} uses the same 32 converters. Full $Q\geq Q_{\rm entry}$ in every run, so Tune($-1$) retains an entry floor as its step shrinks; nominal-start tuning exposes a different step cost.

For Tune(N), an initial-span rule $S_1\geq4\sigma_{\rm res}$ increases acceptance at $|\kappa|=0.20$ from 18/32 to 25/32 at ratio 0.8 and from 21/32 to 28/32 at 0.9. Here $S_1$ is reconstructed two-tone peak-to-peak span and $\sigma_{\rm res}$ is first-window ADC RMS after removing DC and fitted tones. The denominator guard is $2|\kappa|/0.20$ mV. At $|\kappa|=0.05$, 25/32 updates are accepted at each ratio, with full $Q=7.92/7.68$ mV. Thus smaller excursion is not explained only by rejection (Supplement S4).

The post-update interval, 0.10--0.14 s, still has larger $Q$ for native Tune($-1$) than 2/3-budget Nominal: 5.67 versus 5.26 mV at 0.8 and 6.51 versus 5.11 mV at 0.9. Only the running interval, 0.14--1.00 s, reverses this ranking (Table~\ref{tab:windows}).

'''+s[b:]
 a=s.index(r'\caption{Step-size sensitivity');b=s.index(r'\label{fig:step}',a);s=s[:a]+r'''\caption{Starting-ratio and span-guard controls at 1 ns on the same 32 converters. Top: full $Q$ versus negative-step magnitude with step-scaled denominator guard; the horizontal reference is the entry excursion on those same converters. Bottom: native-budget draw 1, with entry/step windows shaded and update at 0.10 s.}'''+s[b:]
 a=s.index('Sensor and ADC effects are substantial.');b=s.index(r'\FloatBarrier',a);s=s[:a]+r'''Sensing and quantization materially affect observation counts. Correcting true gains/offsets gives Nominal/Tune($-1$) counts 198/192 of 200 at ratio 0.8 and 147/148 at 0.9; corrected pre-ADC samples give 200/200 throughout. These are offline diagnostics. Random sensor signs do not ensure an unbiased nonlinear phasor ratio: a shared voltage perturbation contributes $\delta\widehat L_k=-\omega^{-1}\operatorname{Im}(\delta V/I_k)$. Nearly opposite currents can yield opposite-signed errors; the pattern alone does not identify carrier reconstruction as the sole cause (Supplement S3).

'''+s[b:]
 a=s.index('These are same-model implementation checks.');b=s.index('\n\n',a);s=s[:a]+r'''These are same-model implementation checks. Separate ngspice-42 batch runs replay four prescribed-gate circuits at two maximum timesteps. Reference samples are unquantized states at eight nodes per period from the C99 event-aligned RK4 model, with the same gates and initial state. Tight trapezoidal runs differ by at most 0.00223 mV and 0.01275 mA at available positive reference nodes. Gear2 with relative tolerance $10^{-6}$ gives larger maxima, 0.147 mV and 0.389 mA. This sensitivity matters for sub-mV tones; both profiles, complete settings and logs are retained in Supplement S5 and the software. The replays check power-stage propagation with prescribed feedback commands, rather than external digital feedback or hardware.'''+s[b:]
 s=s.replace('The illustrative mean-budget example is a selection rule within this model, not a demonstrated application requirement.','The joint-feasibility limits are illustrative rather than demonstrated application requirements.')
 a=s.index(r'\section{Conclusion}');b=s.index(r'\section*{Data Availability}',a);s=s[:a]+r'''\section{Conclusion}\label{sec:conclusion}
The output cost of required two-tone probing depends on current budget, starting ratio and acceptance guards. At ratio 0.8 and 1 ns, native Tune($-1$) reduces tone against a 2/3-budget Nominal probe with similar mean error, but has fewer valid 1\% observations and larger acquisition excursion. Its smaller running excursion applies after 0.14 s; the preceding post-update interval retains a transient. Lower-budget tuning reduces the excursion, with update success and error distribution dependent on guard scaling. Tune($-1$) has an entry-excursion floor; nominal-start tuning exposes step and initial-signal choices. The separate ensemble supports this conditional tradeoff. Probe selection should therefore combine observation-error, tone and time-window excursion requirements. Measured sensing, external full-feedback implementation and hardware tests remain necessary for deployment.

'''+s[b:]
 a=s.index(r'\section*{Data Availability}');b=s.index(r'\section*{Acknowledgment}',a);s=s[:a]+r'''\section*{Data Availability}
Supporting code, seeds, unrounded converter metrics, numerical comparisons and circuit-engine inputs/logs are available at \url{https://github.com/moon-38/Interleaved-Buck-Diagnostics}. Supplement S1--S6 contains the supporting definitions and results. Citation and reproduction metadata accompany the code/data package.

\Needspace{9\baselineskip}
'''+s[b:];s=s.replace('\\FloatBarrier\n','',1).replace(r'\section{Conclusion}','\\FloatBarrier\n'+r'\section{Conclusion}',1)
 assert '@@' not in s and all(x not in s for x in ['user-supplied','user-reported','now reproduced']);(D/'manuscript/Interleaved_Buck_IEEE_Access_Manuscript.tex').write_text(s);print('Revised main source')
if __name__=='__main__':main()
