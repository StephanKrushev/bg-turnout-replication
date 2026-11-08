"""Build the November 6 observation ledger and closing-forecast comparison."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D1 = 'https://dariknews.bg/novini/bylgariia/goliama-razlika-v-izbiratelnata-aktivnost-kakvo-pokazvat-dannite-kym-1900-chasa-2470058'
D2 = 'https://dariknews.bg/novini/bylgariia/vizhte-izbiratelnata-aktivnost-na-balotazha-kym-1900-chasa-2470764'
BNR = 'https://bnrnews.bg/sofia/post/551376/611percent-aktivnost-otchete-tsik-kam-11-chasa'
BNT = 'https://bntnews.bg/news/cik-izbiratelnata-aktivnost-v-stranata-kam-1600-ch-e-1933-1420026news.html'
R1_CLOSE = 'https://www.bnrnews.bg/izbori/post/549194/aktivnostta-na-parviya-tur-na-prezidentskite-izbori-e-2298percent'
TREND_CLOSE = 'https://darik.bg/kakvo-pokazvat-dannite-na-trend-pri-100-paralelnoto-prebroavane~550181.html'

def read(name):
    with (ROOT / name).open() as f:
        return list(csv.DictReader(f))

def write(name, rows):
    with (ROOT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

ledger = []
def record(r, h, pct, agency, role, url, *, denominator='undocumented', voters='',
           stamp='', evidence='', note=''):
    ledger.append(dict(round=r, date='2026-10-25' if r == 1 else '2026-11-01',
                       observation_time=h, percent=pct, source=agency, role=role,
                       denominator=denominator, participant_count=voters,
                       source_url=url, documented_report_by_local=stamp,
                       timing_evidence=evidence, note=note))

# Independently transcribed from each Darik report; compare with the frozen model file.
hourly = {1:[1.1,2.4,4.4,6.6,9.1,11.3,13.4,15,16.04,18.3,19.8,21.3],
          2:[.8,2.1,4.1,6.8,9.5,12.2,14.9,17.2,19.8,21.5,24]}
working = read('working_turnout.csv')
for r, values in hourly.items():
    for h, value in enumerate(values,8):
        assert value == float(working[h-8][f'round{r}_percent'])
        agency = 'Trend' if h % 2 == 0 or h == 19 else 'Myara'
        note = 'First public timestamp for this individual value unresolved.'
        if (r,h)==(1,16):
            note += ' Report also attributes 16.04 to CIK; CIK table gives 15.95.'
        record(r,f'{h:02}:00',value,agency,'reference' if r==1 else 'runoff input',
               D1 if r==1 else D2, stamp='2026-10-25 19:29' if r==1 else '2026-11-01 19:12',
               evidence='rolling report last-update timestamp',note=note)
for r,v,agency in [(1,21.2,'Myara'),(2,26.0,'Trend'),(2,25.5,'Myara')]:
    record(r,'19:00',v,agency,'excluded alternative or holdout',D1 if r==1 else D2,
           stamp='2026-10-25 19:29' if r==1 else '2026-11-01 19:12',
           evidence='rolling report last-update timestamp')
record(2,'17:30',25.1,'unattributed','excluded conflicting graphic','user-supplied graphic',
       note='Incompatible with treating the subsequent 24.0 as an exact monotone observation.')
official = {}
for row in read('official_turnout_audit.csv'):
    r,h=int(row['round']),int(row['hour'])
    official[r,h]=float(row['turnout_percent'])
    stamp,evidence={ (1,20):('2026-10-28 09:24',R1_CLOSE),
                     (2,11):('2026-11-01 12:50',BNR),
                     (2,16):('2026-11-01 17:03',BNT),
                     (1,11):('2026-11-01 12:50',BNR),
                     (1,16):('2026-11-01 17:03',BNT)}.get((r,h),('',''))
    record(r,f'{h:02}:00',official[r,h],'CIK',
           'reference endpoint' if (r,h)==(1,20) else 'official evaluation' if h==20 else 'official benchmark input',
           f'https://results.cik.bg/pvr202610/tur{r}/aktivnost/index.html',
           denominator=row['eligible_reported'],voters=row['voted_reported'],stamp=stamp,evidence=evidence)
record(2,'close',27.5,'Trend','agency evaluation',TREND_CLOSE,stamp='2026-11-01 21:04',
       evidence='parallel-count article time')
write('observation_ledger.csv',ledger)
assert official[1,20] == float(working[-1]['round1_percent'])
end=official[2,20]
stochastic=json.loads((ROOT/'forecast_figure_results.json').read_text())['cutoffs']
rows=[]
def score(cut,latest,model,pred,clock='',lo='',hi=''):
    rows.append(dict(cutoff_hour=cut,last_observation=latest,model=model,
                     documented_by=clock,closing_forecast=round(pred,6),
                     error_vs_CIK_pp=round(pred-end,6),error_vs_Trend_pp=round(pred-27.5,6),
                     reported_p05=lo,reported_p95=hi))

for h in (12,14,16,18):
    y=hourly[2][h-8]
    score(h,h,'recent two-hour slope',y+(20-h)*(y-hourly[2][h-10])/2)
    score(h,h,'mixed proportional',y*official[1,20]/hourly[1][h-8])
    _,_,median,_,lo,hi=stochastic[str(h)]['path'][-1]
    score(h,h,'stochastic q=0',median,lo=round(lo,6),hi=round(hi,6))
for h,clock in [(11,'12:50'),(16,'17:03')]:
    score(h,h,'official proportional',official[2,h]*official[1,20]/official[1,h],clock)
write('closing_benchmark_by_cutoff.csv',rows)
with (ROOT/'working_paper_table.tex').open('w') as f:
    for h in (12,14,16,18):
        slope,scale,stoch=[r for r in rows if r['cutoff_hour']==h and r['model']!='official proportional']
        f.write(f"{h}:00 & {slope['closing_forecast']:.2f} & {scale['closing_forecast']:.2f} & {stoch['closing_forecast']:.2f} & {stoch['reported_p05']:.2f}--{stoch['reported_p95']:.2f} "+r"\\"+"\n")
