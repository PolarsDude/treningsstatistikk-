import polars as pl
import polars.selectors as cs
from datetime import date

df = pl.read_excel("treningsdata.xlsx")

def prep(df):

# Fikser på dato kolonne
 df = (df
 .with_columns(pl.col('Dato').cast(pl.String).str.slice(0,4).alias('År'),
               pl.col('Dato').cast(pl.String).str.slice(4,2).alias('Måned'),
               pl.col('Dato').cast(pl.String).str.slice(6,2).alias('Dag')
               )
 
 # Gjør dag om k
 .with_columns(pl.concat_str(['År', 'Måned', 'Dag'], separator='-').cast(pl.Date).alias('Dato'),
               pl.col('Måned','Dag').cast(pl.Int64)
               )
 )
 
 
 # Mapper måned nr til navn
 df = (df
     .with_columns(pl.col("Måned").alias('Måned nr'))
     .with_columns(
      pl.when(pl.col("Måned") == 1).then(pl.lit("Januar"))
      .when(pl.col("Måned") == 2).then(pl.lit("Februar"))
      .when(pl.col("Måned") == 3).then(pl.lit("Mars"))
      .when(pl.col("Måned") == 4).then(pl.lit("April"))
      .when(pl.col("Måned") == 5).then(pl.lit("Mai"))
      .when(pl.col("Måned") == 6).then(pl.lit("Juni"))
      .when(pl.col("Måned") == 7).then(pl.lit("Juli"))
      .when(pl.col("Måned") == 8).then(pl.lit("August"))
      .when(pl.col("Måned") == 9).then(pl.lit("September"))
      .when(pl.col("Måned") == 10).then(pl.lit("Oktober"))
      .when(pl.col("Måned") == 11).then(pl.lit("November"))
      .when(pl.col("Måned") == 12).then(pl.lit("Desember"))
      .otherwise(pl.lit("Ukjent"))
      .alias("Måned")
     )
 )

 # Identifiserer årstid
 df = df.with_columns(
    pl.when(pl.col("Måned nr").is_in([12, 1, 2]))
      .then(pl.lit("vinter"))
      .when(pl.col("Måned nr").is_in([3, 4, 5]))
      .then(pl.lit("vår"))
      .when(pl.col("Måned nr").is_in([6, 7, 8]))
      .then(pl.lit("sommer"))
      .when(pl.col("Måned nr").is_in([9, 10, 11]))
      .then(pl.lit("høst"))
      .otherwise(pl.lit("ukjent"))
      .alias("Årstid")
 )

 return df

# Funksjon for å mappe publiseringsdato til treningsdato
def dato_mapping_pub_trening(df):
 
 # Henter ut max og min dato
 aar_max = int(df.select('År').max().item())
 aar_min = int(df.select('År').min().item())

 alle_datoer = pl.DataFrame({'alle_dato':pl.date_range(date(aar_min, 1, 1), date(aar_max, 12, 1), "1d", eager=True)})

 publiseringsdato = df.select('Dato').unique().rename({'Dato':'publiseringsdato'})

 publiseringsdato = (publiseringsdato

 # Kobler på alle datoer som er større enn eller lik publiseringsdato
 .join_where(
 alle_datoer,

 # Denne inequalitien vil sikre at dersom èn har publisert trening samme dag som det skal være trening
 pl.col('publiseringsdato')<=pl.col('alle_dato')
 )

 # Ekstraherer ukedag
 .with_columns(pl.col('alle_dato').dt.weekday().alias('dag'))

 # Identifiserer hva som er den første mandagen ellers onsdag
  .group_by('publiseringsdato')
  .agg(
     
    # Første mandag  
    pl.col('alle_dato').filter(pl.col('dag')==1).min().alias('forste_mandag'),

    # Første onsdag
    pl.col('alle_dato').filter(pl.col('dag')==3).min().alias('forste_onsdag')
    
    )

 # Dersom det er 2024 brukes mandag, hvis ikke brukes onsdag. Må sannsynligvis endre på logikken om flere år inkluderes i datasettet
 .with_columns(pl.when(pl.col('publiseringsdato').dt.year()==2024)
              .then(pl.col('forste_mandag'))
              .otherwise(pl.col('forste_onsdag'))
              .alias('treningsdato')
 )

 # Fjerner forste_ kolonnene
 .select(~cs.starts_with('forste'))

 # Det kan være tilfeller hvor treningsdato har to eller flere publiseringsdato. Dette kan for eksempel forekomme dersom èn har publisert trening to ganger etter første mandagen i uken, som foreksempel
 # 2024-07-25 (torsdag) og 2024-07-28 (søndag). Derfor tas det unike radene av treningsdato
 .unique(subset='treningsdato')

 )



 # Må ta en inner join fordi vi fjerner duplikater av tilfeller hvor treningsdato har 2 eller flere publiseringsdato
 df = (df
 .join(other = publiseringsdato,left_on='Dato',right_on='publiseringsdato',how = 'inner')
 .drop('Dato')
 .rename({'treningsdato':'Dato'})
 )

 return df