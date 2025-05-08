import streamlit as st
import polars as pl
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Beskrivelse av appen
st.markdown(
    """
    ## I denne visningen kan du se på statistikk knyttet til hvilke kombinasjon av deltakere som møter opp
    """
)

df = pl.read_excel("treningsdata.xlsx")


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


# beregner alle trippletter
triplett = (df
.filter(pl.col('Avlyst trening')=='Nei',
        pl.col('Deltok')=='Ja')
.select('Dato','Navn')
.unique()
.group_by('Dato')
.agg(pl.col('Navn').alias('navn_1'),
     pl.col('Navn').alias('navn_2'),
     pl.col('Navn').alias('navn_3')
)

# Finner 3 kombinasjoner
.explode('navn_1')
.explode('navn_2')
.explode('navn_3')

# Skal samle alle navnene i en liste for å telle unike navn. Skal fjerne lister som har kun ett navn        
.with_columns(pl.concat_str(['navn_1', 'navn_2', 'navn_3'], separator=',').str.split(",").alias('kombi'))

# Sorterer liste
.with_columns(pl.col('kombi').list.sort())

# Filtrerer på lister som har 3 unike navn (etter at duplikater er fjernet)
.filter(pl.col('kombi').list.unique().list.n_unique()==3)
.group_by('kombi')
.agg(pl.col('Dato').n_unique().alias('Antall treninger'))
.sort(by = ['Antall treninger'],descending=True)
.with_columns(pl.col('kombi').list.join(",").alias('Kombinasjon'))
.select('Kombinasjon','Antall treninger')
)

st.write("Trippletter som har vært på trening")
st.dataframe(triplett)