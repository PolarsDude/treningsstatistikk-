import polars as pl
import polars_ds as pds
from utils import prep,dato_mapping_pub_trening,datoformat_mapping
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

st.title("Spillerstatistikk")
df = pl.read_excel("treningsdata.xlsx")

# Transformer dataene
df = (df
.pipe(datoformat_mapping)
.pipe(dato_mapping_pub_trening)
.pipe(prep)
)

# Henter ut sortert liste over måneder
maaned_sort = df.select('Måned', 'Måned navn').unique().sort(by ='Måned',descending=False)['Måned'].to_list()

# Lager valg på person
velg_person = st.selectbox("Velg person:", sorted(df['Navn'].unique()),key="velg_person")

# Lager valg på år 
velg_aar = st.selectbox("Velg år:", df.select('År').unique().to_series().to_list(),key="velg_aar")


topp_10 = (df
.filter(pl.col('Avlyst trening')=='Nei',
        pl.col('Deltok')=='Ja',
        pl.col('Navn')==st.session_state.velg_person,
        pl.col('År')==st.session_state.velg_aar
        )
.group_by('Navn','År','Måned')
.agg(pl.col('Dato').n_unique().cast(pl.Int64).alias('Antall treninger'))
.sort(by = ['År','Måned','Antall treninger'],descending=[True,False,False])
)

fig, ax = plt.subplots()
sns.barplot(data=topp_10.to_pandas(), x='Måned', y='Antall treninger',ax = ax,order=maaned_sort)
ax.set_title(f'Antall treninger per måned for {st.session_state.velg_person}')
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.set(ylabel=None) 

# Roter x-labels
ax.tick_params(axis='x', rotation=50)


# Viser figuren i Streamlit
st.pyplot(fig)

######## Lager statistikk for treningsstreak ##


# Beskrivelse av appen
st.markdown(
    """
    Denne tabellen viser ulike nøkkeltall for en valgt spiller
    * Totalt antall treninger viser hvor mange treninger spilleren har deltatt på totallt
    * Første trening og siste trening viser henholdsvis første og siste trening spilleren har deltatt på
    * Treningsstreak viser hvor mange treninger på rad en deltaker har møtt opp på uten å ha noen fravær mellom. 
    Hver gang en deltaker ikke møter, nullstilles streaken, og den starter på nytt neste gang vedkommende møter opp.
    """
)

treningsstreak = (df
.filter(pl.col('Avlyst trening')=='Nei',
        pl.col('Navn')==st.session_state.velg_person,
        pl.col('År')==st.session_state.velg_aar
        )       
.group_by('Navn')
.agg(pl.col('Dato').filter(pl.col('Deltok')=='Ja').n_unique().alias('Totalt antall treninger'),
     pl.col('Dato').filter(pl.col('Deltok')=='Ja').min().cast(pl.Date).alias('Første trening'),
     pl.col('Dato').filter(pl.col('Deltok')=='Ja').max().cast(pl.Date).alias('Siste trening'),
     pds.query_longest_streak(pl.col('Deltok')=='Ja').alias('Lengste treningsstreak')
     )
)

st.write("Antall treninger per måned")
st.dataframe(treningsstreak)