import polars as pl
from data_prep import prep
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

st.title("Spillerstatistikk")
df = pl.read_excel("treningsdata.xlsx")

# Transformer dataene
df = prep(df)

# Henter ut sortert liste over måneder
maaned_sort = df.select('Måned nr', 'Måned').unique().sort(by ='Måned nr',descending=False)['Måned'].to_list()

velg_aar = st.selectbox("Velg person:", sorted(df['Navn'].unique()),key="velg_person")


topp_10 = (df
.filter(pl.col('Avlyst trening')=='Nei',
        pl.col('Deltok')=='Ja',
        pl.col('Navn')==st.session_state.velg_person
        )
.group_by('Navn','Måned')
.agg(pl.col('Dato').n_unique().cast(pl.Int64).alias('Antall treninger'))
.sort(by = ['Antall treninger'],descending=True)
)

fig, ax = plt.subplots()
sns.barplot(data=topp_10.to_pandas(), x='Måned', y='Antall treninger',ax = ax,order=maaned_sort)
ax.set_title(f'Antall treninger per måned for {st.session_state.velg_person}')
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.set(ylabel=None) 


# Viser figuren i Streamlit
st.pyplot(fig)