import streamlit as st
import polars as pl
from data_prep import prep
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# Beskrivelse av appen
st.markdown(
    """
    ## Generell treningsstatistikk
    """
)

df = pl.read_excel("treningsdata.xlsx")

# Transformer dataene
df = prep(df)

# Antall treninger per måned
antall_treninger_per_mnd = (df
.group_by('År','Måned','Måned nr')
.agg(pl.col('Dato')
     .filter(pl.col('Avlyst trening')=='Nei')
     .n_unique()
     .alias('Antall treninger'),

     pl.col('Dato')
     .filter(pl.col('Avlyst trening')=='Ja')
     .n_unique()
     .alias('Antall avlyste treninger'),

     pl.col('Dato')
     .filter(pl.col('Avlyst trening')=='Nei')
     .n_unique()
     .truediv(pl.col('Navn').filter(pl.col('Deltok')=='Ja').n_unique())
     .alias('Antall per trening')
     
     )
.sort(by=['År','Måned nr'])
.drop('Måned nr')
)


st.write("Antall treninger per måned")
st.dataframe(antall_treninger_per_mnd)


#df = pl.read_excel("../treningsdata.xlsx")
#df.head()

#df.group_by('År','Måned','Måned nr').agg(pl.col())