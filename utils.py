import polars as pl

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

 return df