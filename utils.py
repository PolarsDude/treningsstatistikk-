import polars as pl
import polars.selectors as cs
from datetime import date

def datoformat_mapping(df):
  # Fikser på dato kolonne
  df = (df
   .with_columns(
             pl.col('Dato').cast(pl.String).str.strptime(pl.Date, "%Y%m%d", strict=False)
               )
   )
  return df



# Funksjon for å mappe publiseringsdato til treningsdato
def dato_mapping_pub_trening(df):

    # Henter ut max og min dato
    aar_max = int(df.select(pl.col("Dato").dt.year()).max().item())
    aar_min = int(df.select(pl.col("Dato").dt.year()).min().item())

    alle_datoer = pl.DataFrame(
        {
            "alle_dato": pl.date_range(
                date(aar_min, 1, 1),
                date(aar_max, 12, 31),
                "1d",
                eager=True,
            )
        }
    )

    publiseringsdato = (
        df.select("Dato")
        .unique()
        .rename({"Dato": "publiseringsdato"})
    )

    publiseringsdato = (
        publiseringsdato

        # Kobler på alle datoer som er større enn eller lik publiseringsdato
        .join_where(
            alle_datoer,
            # Denne inequality-en sikrer at publisering samme dag teller
            pl.col("publiseringsdato") <= pl.col("alle_dato"),
        )

        # Ekstraherer ukedag
        .with_columns(
            pl.col("alle_dato").dt.weekday().alias("dag")
        )

        # Identifiserer første mandag eller onsdag
        .group_by("publiseringsdato")
        .agg(
            # Første mandag
            pl.col("alle_dato")
            .filter(pl.col("dag") == 1)
            .min()
            .alias("forste_mandag"),

            # Første onsdag
            pl.col("alle_dato")
            .filter(pl.col("dag") == 3)
            .min()
            .alias("forste_onsdag"),
        )

        # Dersom 2024 brukes mandag, ellers onsdag
        .with_columns(
            pl.when(pl.col("publiseringsdato").dt.year() == 2024)
            .then(pl.col("forste_mandag"))
            .otherwise(pl.col("forste_onsdag"))
            .alias("treningsdato")
        )

        # Fjerner forste_-kolonnene
        .select(~cs.starts_with("forste"))

        # Tar unike treningsdatoer
        .unique(subset="treningsdato", keep="first")
    )

    # Må ta en left join fordi vi fjerner duplikater der
    # samme treningsdato har flere publiseringsdatoer
    df = (
        df
        .join(
            other=publiseringsdato,
            left_on="Dato",
            right_on="publiseringsdato",
            how="inner",
        )
        .rename({"treningsdato": "Treningsdato"})
    )

    return df


def prep(df):

 # Henter ut div dato kolonner 
 df = (df
       
 # Henter ut år måned dag
 .with_columns(pl.col('Treningsdato').dt.year().alias('År'),
               pl.col('Treningsdato').dt.month().alias('Måned'),
               pl.col('Treningsdato').dt.weekday().alias('Dag')
               )
 )
 
 
 # Mapper måned nr til navn
 df = (df
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
      .alias("Måned navn")
     )
     .with_columns(
     pl.when(pl.col("Måned").is_in([12, 1, 2]))
      .then(pl.lit("vinter"))
      .when(pl.col("Måned").is_in([3, 4, 5]))
      .then(pl.lit("vår"))
      .when(pl.col("Måned").is_in([6, 7, 8]))
      .then(pl.lit("sommer"))
      .when(pl.col("Måned").is_in([9, 10, 11]))
      .then(pl.lit("høst"))
      .otherwise(pl.lit("ukjent"))
      .alias("Årstid")
  )
 )


 return df
