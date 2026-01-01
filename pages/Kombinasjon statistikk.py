import streamlit as st
import polars as pl
from utils import prep,dato_mapping_pub_trening,datoformat_mapping
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


# Transformer dataene
df = (df
.pipe(datoformat_mapping)
.pipe(dato_mapping_pub_trening)
.pipe(prep)
#.drop_nulls()
)

# Funksjon for å få statistikk på kombinasjoner. Dersom antall_kombinasjon er lik 3 betyr det at vi er interessert i tripplett
def kombi_statistikk(antall_kombinasjon,aar):

 # Lager antall navn expr
 navn_init =[f'navn_{i+1}' for i in range(antall_kombinasjon)]
 navn_expr = [pl.col('Navn').alias(f'navn_{i+1}') for i in range(antall_kombinasjon)]
 
 # Initialiserer datasett
 df_init = (df
 .filter(pl.col('Avlyst trening')=='Nei',
         pl.col('Deltok')=='Ja',
         pl.col('År')==aar)
 .select('År','Dato','Navn')
 .unique()
 .group_by('Dato','År')
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
 .group_by('kombi','År')
 .agg(pl.col('Dato').n_unique().alias('Antall treninger'))
 .sort(by = ['År','Antall treninger'],descending=[True,True])
 .with_columns(pl.col('kombi').list.join(",").alias('Kombinasjon'))
 .select('Kombinasjon','Antall treninger')
 
 )

 return df_kombi


# Lager valg på år 
velg_aar = st.selectbox("Velg år:", df.select('År').unique().to_series().to_list(),key="velg_aar")

# Lager valg på antall kombinasjoner
velg_antall_kombi = st.selectbox("Velg antall kombinasjoner (maks 6 kombinasjoner tillatt):", range(1,7),key="velg_antall_kombi")

# Kjør funksjon
df_kombi = kombi_statistikk(st.session_state.velg_antall_kombi,st.session_state.velg_aar)

st.write("Alle kombinasjoner med antall treninger:")
st.dataframe(df_kombi)


# Lager visning slik at èn kan se hvilke kombinasjoner den finnes i 
velg_navn = st.selectbox("Sjekk hvilke kombinasjon du finnes i:", sorted(df['Navn'].unique()),key="velg_navn")

st.write("Alle kombinasjoner med antall treninger:")

# Sorterer for sikkerhetsskyld
st.dataframe(df_kombi.filter(pl.col('Kombinasjon').str.contains(st.session_state.velg_navn)).sort(by = ['Antall treninger'],descending=True))