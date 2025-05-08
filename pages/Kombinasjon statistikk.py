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


# Funksjon for å få statistikk på kombinasjoner. Dersom antall_kombinasjon er lik 3 betyr det at vi er interessert i tripplett
def kombi_statistikk(antall_kombinasjon):

 # Lager antall navn expr
 navn_init =[f'navn_{i+1}' for i in range(antall_kombinasjon)]
 navn_expr = [pl.col('Navn').alias(f'navn_{i+1}') for i in range(antall_kombinasjon)]
 
 # Initialiserer datasett
 df_init = (df
 .filter(pl.col('Avlyst trening')=='Nei',
         pl.col('Deltok')=='Ja')
 .select('Dato','Navn')
 .unique()
 .group_by('Dato')
 .agg(*navn_expr)
 )
 
 # Exploder df for å finne alle kombinasjoner 
 for i in range(antall_kombinasjon):
    df_init = df_init.explode(navn_init[i])
 
 # Fjerner duplikater 
 df_kombi = (
 
 df_init
 
 # Skal samle alle navnene i en liste for å telle unike navn. Skal fjerne lister som har kun ett navn        
 .with_columns(pl.concat_str(*navn_init, separator=',').str.split(",").alias('kombi'))
 
 # Sorterer liste
 .with_columns(pl.col('kombi').list.sort())
 
 # Filtrerer på lister som har x antall unike navn (etter at duplikater er fjernet)
 .filter(pl.col('kombi').list.unique().list.n_unique()==antall_kombinasjon)
 .group_by('kombi')
 .agg(pl.col('Dato').n_unique().alias('Antall treninger'))
 .sort(by = ['Antall treninger'],descending=True)
 .with_columns(pl.col('kombi').list.join(",").alias('Kombinasjon'))
 .select('Kombinasjon','Antall treninger')
 
 )

 return df_kombi



# Lager valg på antall kombinasjoner
velg_antall_kombi = st.selectbox("Velg antall kombinasjoner (maks 6 kombinasjoner tillatt):", range(1,7),key="velg_antall_kombi")

# Kjør funksjon
df_kombi = kombi_statistikk(st.session_state.velg_antall_kombi)

st.write("Alle kombinasjoner med antall treninger:")
st.dataframe(df_kombi)


# Lager visning slik at èn kan se hvilke kombinasjoner den finnes i 
velg_navn = st.selectbox("Sjekk hvilke kombinasjon du finnes i:", sorted(df['Navn'].unique()),key="velg_navn")

st.write("Alle kombinasjoner med antall treninger:")

# Sorterer for sikkerhetsskyld
st.dataframe(df_kombi.filter(pl.col('Kombinasjon').str.contains(st.session_state.velg_navn)).sort(by = ['Antall treninger'],descending=True))