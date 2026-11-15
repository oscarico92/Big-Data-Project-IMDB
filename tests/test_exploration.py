"""Execute the notebook's exact query functions on synthetic Spark DataFrames."""
import json
import ast
import csv
import os
import sys
import tempfile
from pathlib import Path
from pyspark.sql import SparkSession, functions as F, Window
from pyspark.sql.types import ArrayType, MapType, StructType

os.environ['PYSPARK_PYTHON'] = sys.executable
spark = (SparkSession.builder.master('local[2]').appName('exploration-regression')
         .config('spark.ui.enabled', 'false').config('spark.sql.shuffle.partitions', '2')
         .config('spark.sql.adaptive.enabled', 'false')
         .config('spark.sql.warehouse.dir', str(Path('work/spark-warehouse').resolve()))
         .getOrCreate())
spark.sparkContext.setLogLevel('ERROR')
PROJECT = Path(__file__).resolve().parents[1]
nb = json.loads((PROJECT / 'notebooks/02_data_exploration.ipynb').read_text(encoding='utf-8'))
for c in nb['cells']:
    if any(t.endswith('-definition') for t in c['metadata'].get('tags', [])):
        exec(''.join(c['source']), globals())

# Use SQL literals to keep the fixture independent of Python worker configuration.
def frame(rows, schema):
    def sql(v):
        if v is None: return 'NULL'
        if isinstance(v, bool): return str(v).lower()
        if isinstance(v, list): return 'array(' + ','.join(sql(x) for x in v) + ')'
        if isinstance(v, str): return "'" + v.replace("'", "''") + "'"
        return str(v)
    parts = []
    for row in rows:
        parts.append('SELECT ' + ', '.join(f'CAST({sql(v)} AS {typ}) AS {name}'
                     for v, (name, typ) in zip(row, schema)))
    return spark.sql(' UNION ALL '.join(parts))

movie_schema = [('tconst','string'),('primaryTitle','string'),('originalTitle','string'),('startYear','int'),
                ('runtimeMinutes','int'),('genres','array<string>'),('is_feature_film','boolean'),
                ('is_runtime_suspicious','boolean'),('averageRating','double'),('numVotes','int')]
def movie(t, year=2000, runtime=100, genres=None, rating=7., votes=1000):
    return (t,t,t,year,runtime,genres or ['Drama'],runtime>40, runtime>600,rating,votes)

checks=[]
def passed(label):
    checks.append(label)
    print('PASS:',label,flush=True)

try:
    m=frame([movie('regular'+str(i)) for i in range(30)] + [movie('outlier',runtime=300)] +
            [movie('zero'+str(i),genres=['Constant']) for i in range(30)] +
            [movie('short',runtime=20),movie('suspicious',runtime=10000)],movie_schema)
    result=unusual_runtimes(m).collect()
    assert len(result)==1 and result[0].tconst=='outlier' and result[0].genre_movies==31
    passed('Q1: outlier, feature-length restriction, zero variance, suspicious runtime exclusion')

    gm=frame([movie('a',genres=['A','A','B'],votes=100),movie('b',genres=['C'],votes=50),
              movie('c',genres=['D'],votes=50),movie('d',genres=['E'],rating=None,votes=None),
              movie('outside',year=1979,votes=999999)],movie_schema)
    stats=genre_rankings(gm).cache()
    rows={r.genre:r for r in stats.collect()}
    assert rows['A'].total_votes==100 and rows['A'].movie_count==1
    assert [r.genre for r in stats.orderBy('popularity_rank').limit(3).collect()]==['A','B','C']
    assert rows['E'].rated_movie_count==0 and rows['E'].total_votes==0
    passed('Q2: duplicate genres, stable ties, missing ratings, year bounds')
    by_genre,by_movie=compare_genres(stats,gm)
    groups={r.group:r for r in by_movie.collect()}
    assert groups['has_top3_genre'].movie_count==2 and groups['other_genres_only'].movie_count==2
    assert sum(r.total_votes for r in groups.values())==200
    assert abs(sum(r.movie_share_pct for r in groups.values())-100)<1e-8
    assert len(by_genre.collect())==2
    passed('Q3: disjoint films and votes, shares sum to 100')
    stats.unpersist()

    cm=frame([movie('hit',rating=8.),movie('low1',rating=5.),movie('low2',rating=7.),
              movie('unknown',rating=None,votes=None),movie('hit2',rating=9.)],movie_schema)
    cr=frame([('hit',['yes','no'],['yes']),('low1',['yes','no'],[]),
              ('low2',['yes','no'],[]),('unknown',['yes'],[]),('hit2',['no'],[])],
             [('tconst','string'),('directors','array<string>'),('writers','array<string>')])
    nm=frame([('yes','Eligible'),('no','Two hits')],[('nconst','string'),('primaryName','string')])
    r=exceptional_directors(cr,cm,nm).collect()
    assert len(r)==1 and r[0].nconst=='yes' and r[0].other_mean_rating==6 and r[0].unrated_movies==1
    assert exceptional_directors(cr,cm,nm,min_votes=1001).count()==0
    assert exceptional_directors(cr,cm,nm,other_rating=5.9).count()==0
    passed('Q4: exact single hit, mean of other ratings, unobserved ratings')

    ts=frame([(x,x,'tvSeries',False) for x in ['valid','short_last','unknown_season','unrated_last']],
             [('tconst','string'),('primaryTitle','string'),('titleType','string'),('is_unreleased','boolean')])
    ep=[]; rt=[]
    for series in ['valid','short_last','unknown_season','unrated_last']:
        for season in range(1,4):
            for number in range(1,11):
                t=f'{series}_{season}_{number}'
                ep.append((t,series,season,number))
                if series=='unrated_last' and season==3: continue
                note=9. if (season in [1,2] and number==1) else (2. if season==3 and number==1 else 7.)
                rt.append((t,note,100))
    ep += [(f'short_s4_{i}','short_last',4,i) for i in range(1,7)]
    ep += [('unknown_s','unknown_season',None,None)]
    rt += [(f'short_s4_{i}',1. if i==1 else 7.,100) for i in range(1,7)]
    e=frame(ep,[('tconst','string'),('parentTconst','string'),('seasonNumber','int'),('episodeNumber','int')])
    rts=frame(rt,[('tconst','string'),('averageRating','double'),('numVotes','int')])
    result,evidence=qualifying_series(ts,e,rts)
    q=result.collect(); ev=evidence.collect()
    by_series={r.parentTconst:r for r in q}
    assert set(by_series)=={'valid','short_last','unknown_season'}
    assert by_series['valid'].episode_count==30 and by_series['valid'].rated_episode_pct==100
    assert by_series['short_last'].full_seasons==3 and by_series['short_last'].last_season==4
    assert by_series['short_last'].episode_count==36 and len(ev)==9
    assert qualifying_series(ts,e,rts,min_votes=101)[0].count()==0
    passed('Q5: three full seasons plus a short last season, unnumbered special, tied best episodes, vote threshold')

    lm=frame([movie('french'),movie('english'),movie('german'),movie('unknown'),movie('failure',rating=6.9)],movie_schema)
    cast=frame([(t,'actor') for t in ['french','english','german','unknown','failure']], [('tconst','string'),('nconst','string')])
    ln=frame([('actor','Actor')],[('nconst','string'),('primaryName','string')])
    ak=frame([('french',' french ','FR',None,0),('english','english','US',None,0),
              ('english','english','DE','en',0),('english','english','DE','de',0),
              ('german','german','DE','de',0),('english','translated','JP','ja',0),
              ('english','english','JP','ja',1),('unknown','unknown','IN',None,0),
              ('failure','failure','IT','it',0)],
             [('titleId','string'),('title','string'),('region','string'),('language','string'),('isOriginalTitle','int')])
    summary,evidence,coverage,languages=multilingual_candidates(cast,lm,ak,ln)
    r=summary.collect()
    assert len(r)==1 and r[0].language_count==3 and r[0].successful_movie_count==3
    assert len(evidence.collect())==3 and coverage.first().coverage_pct==75
    english=languages.filter(F.col('tconst')=='english').first()
    assert english.language=='en' and english.supporting_akas==2 and english.total_candidate_akas==3
    original_rows_only=ak.withColumn('isOriginalTitle',F.lit(1))
    empty,_,cov,_=multilingual_candidates(cast,lm,original_rows_only,ln)
    assert empty.count()==0 and cov.first().with_estimated_language==0
    tied=ak.filter((F.col('titleId')=='english') & F.col('language').isin('en','de'))
    estimate=estimate_languages(lm,tied).first()
    assert estimate.language=='de' and estimate.tied_top_languages==2 and estimate.support_share_pct==50
    passed('Q6: originalTitle matching, regional fallback, explicit-language priority, plurality, ties, coverage, unmapped regions')

    career_movies=[]; career_cast=[]
    for person in ['early','tied','short']:
        for i in range(15):
            year=1980+i*2
            rating=9. if i==0 else (8. if i<4 else 5.)
            if person=='tied' and i==14: rating=9.
            if person=='short': year=2000+i
            tid=f'{person}_{i}'
            career_movies.append(movie(tid,year=year,rating=rating))
            career_cast.append((tid,person))
    ca=frame(career_cast,[('tconst','string'),('nconst','string')])
    mm=frame(career_movies,movie_schema)
    nn=frame([(x,x) for x in ['early','tied','short']],[('nconst','string'),('primaryName','string')])
    result,peaks=early_peak_actors(ca,mm,nn)
    r=result.collect()
    assert len(r)==1 and r[0].nconst=='early' and r[0].dated_movies==15 and r[0].career_years==28
    assert peaks.first().tconst=='early_0'
    passed('Q7: long career, movie threshold, early peak, late tie exclusion')

    p=frame([('hit','yes','actress'),('hit','yes','actor'),('low1','yes','actor'),
             ('hit','yes','director'),('hit','no','actor')],
            [('tconst','string'),('nconst','string'),('category','string')])
    people,projects,comparison,paired,overall=multitalented_professionals(p,cr,cm,nm)
    hit=projects.filter((F.col('nconst')=='yes') & (F.col('tconst')=='hit')).first()
    assert hit.role_count==3 and hit.project_roles==['actor','director','writer']
    yes={r.role_mode:r for r in comparison.filter(F.col('nconst')=='yes').collect()}
    assert yes['multiple'].movies==2 and yes['single'].movies==2 and yes['single'].rated_movies==1
    assert abs(yes['multiple'].mean_rating-6.5)<1e-8
    pair=paired.filter(F.col('nconst')=='yes').first()
    assert pair.multiple_minus_single==-0.5
    assert overall.first().comparable_people>=1
    passed('Q8: deduplicated roles, crew/principal union, paired performance, missing ratings')
    load_cell=next(c for c in nb['cells'] if 'load' in c['metadata'].get('tags',[]))
    export_function=next(n for n in ast.parse(''.join(load_cell['source'])).body
                         if isinstance(n,ast.FunctionDef) and n.name=='save_result')
    exec(compile(ast.Module(body=[export_function],type_ignores=[]),'notebook-export','exec'),globals())
    (PROJECT/'data').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=PROJECT/'data',prefix='export-test-') as folder:
        RESULTS_DIR=Path(folder)/'results'
        PARQUET_DIR=Path(folder)/'parquet'
        RESULTS_DIR.mkdir()
        first=spark.sql("SELECT 1 AS id, array('a','b') AS labels UNION ALL SELECT 2,array('c')")
        save_result(first,'fixed_result',['id'],preview=1)
        with (RESULTS_DIR/'fixed_result.csv').open(encoding='utf-8',newline='') as handle:
            rows=list(csv.DictReader(handle))
        assert len(rows)==2 and json.loads(rows[0]['labels'])==['a','b']
        save_result(first.filter('id = 2'),'fixed_result',['id'],preview=1)
        with (RESULTS_DIR/'fixed_result.csv').open(encoding='utf-8',newline='') as handle:
            rows=list(csv.DictReader(handle))
        assert len(rows)==1 and rows[0]['id']=='2'
        assert list(RESULTS_DIR.iterdir())==[RESULTS_DIR/'fixed_result.csv']
        assert spark.read.parquet(str(PARQUET_DIR/'fixed_result')).count()==1
    passed('Exports: one fixed CSV, JSON arrays, complete rows, safe overwrite on rerun')
    result_path=PROJECT / 'data' / 'test_results.json'
    result_path.parent.mkdir(parents=True,exist_ok=True)
    result_path.write_text(json.dumps({'status':'passed','spark':spark.version,
        'checks':checks,'data':'synthetic only; no IMDb dataset execution'},indent=2),encoding='utf-8')
    print('ALL EIGHT QUESTION TESTS PASSED',flush=True)
finally:
    spark.stop()
