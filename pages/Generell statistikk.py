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
    ## Generell treningsstatistikk
    """
)

df = pl.read_excel("treningsdata.xlsx")

# Transformer dataene
df = (df
.pipe(datoformat_mapping)
.pipe(dato_mapping_pub_trening)
.pipe(prep)
)

# Antall treninger per måned
antall_treninger_per_mnd = (df
.group_by('År','Måned navn','Måned')
.agg(pl.col('Treningsdato')
     .filter(pl.col('Avlyst trening')=='Nei')
     .n_unique()
     .alias('Antall treninger'),

     pl.col('Dato')
     .filter(pl.col('Avlyst trening')=='Ja')
     .n_unique()
     .alias('Antall avlyste treninger'),
     
     pl.col('Navn')
     .filter(pl.col('Deltok')=='Ja')
     .len()
     .truediv(pl.col('Treningsdato').filter(pl.col('Avlyst trening')=='Nei').n_unique())
     .alias('Antall per trening')
     
     )
.sort(by=['År','Måned'])
.drop('Måned')
)


st.write("Antall treninger per måned")
st.dataframe(antall_treninger_per_mnd)

antall_treninger = (df
.group_by('År','Måned navn','Måned')
.agg(
     
     pl.col('Treningsdato').filter(pl.col('Avlyst trening')=='Nei').n_unique().alias('Antall treninger'),
     
     pl.col('Treningsdato').filter(pl.col('Avlyst trening')=='Ja').n_unique().alias('Antall avlyste treninger'),

     pl.col('Navn')
     .filter(pl.col('Deltok')=='Ja')
     .len()
     .truediv(pl.col('Treningsdato').filter(pl.col('Avlyst trening')=='Nei').n_unique())
     .alias('Antall per trening'))
)

#  Lager gjenbrukbar expression. Kjeder sammen år, måned og den første dagen. 
dato_expr = pl.when(
    pl.col('Måned').cast(pl.String).str.len_chars() > 1
).then(
    pl.concat_str(
        [pl.col('År'), pl.col('Måned'), pl.lit('01')],
        separator="-"
    )
).otherwise(
    pl.concat_str(
        [
            pl.col('År'),
            pl.concat_str([pl.lit('0'), pl.col('Måned')]),
            pl.lit('01')
        ],
        separator="-"
    )
).cast(pl.Date).alias('d')  # valgfritt: gir navnet 'd' til kolonnen


# Skal plotte fra den første dagen per måned
antall_treninger = (
    antall_treninger
    .with_columns(
        dato_expr
    )
)

# Pivoterer
antall_treninger_piv = (antall_treninger
.unpivot(index = ['År','Måned navn','Måned'],on = ['Antall treninger','Antall avlyste treninger'])
.sort(by=['variable','År','Måned'])
)


# Skal plotte fra den første dagen per måned
antall_treninger_piv = (
    antall_treninger_piv
    .with_columns(
       dato_expr
    )
)

######## Plotter antall treninger mot antall avlyste ############
fig, ax = plt.subplots()
sns.lineplot(data = antall_treninger_piv.to_pandas(), x='d', y='value',hue='variable',ax = ax)

# Roter x-labels
ax.tick_params(axis='x', rotation=50)
ax.set_ylabel("")
ax.set_xlabel("")
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_title('Antall treninger per måned')


# Viser figuren i Streamlit
st.pyplot(fig)

#################################
 
############# Plotter antall treninger mot antall avlyste ##############################
fig, ax = plt.subplots()
sns.lineplot(data = antall_treninger.to_pandas(), x='d', y='Antall per trening',ax = ax)

# Roter x-labels
ax.tick_params(axis='x', rotation=50)
ax.set_ylabel("")
ax.set_xlabel("")
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_title('Gjennomsnittlig antall deltakere per trening')

# Viser figuren i Streamlit
st.pyplot(fig)

#########################################################################################