import streamlit as st
import polars as pl
from utils import prep
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

antall_treninger = (df
.group_by('Måned','Måned nr')
.agg(pl.col('Dato').filter(pl.col('Avlyst trening')=='Nei').n_unique().alias('Antall treninger'),
     pl.col('Dato').filter(pl.col('Avlyst trening')=='Ja').n_unique().alias('Antall avlyste treninger'))
)

antall_treninger = (antall_treninger
.unpivot(index = ['Måned','Måned nr'],on = ['Antall treninger','Antall avlyste treninger'])
.sort(by=['variable','Måned nr'])
.drop('Måned nr')
)


fig, ax = plt.subplots()
sns.lineplot(data = antall_treninger.to_pandas(), x='Måned', y='value',hue='variable',ax = ax)

# Roter x-labels
ax.tick_params(axis='x', rotation=50)
ax.set_ylabel("")
ax.set_xlabel("")
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_title('Antall treninger per måned')


# Viser figuren i Streamlit
st.pyplot(fig)