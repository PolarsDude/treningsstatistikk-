import polars as pl
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

st.title("Spillerstatistikk")
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