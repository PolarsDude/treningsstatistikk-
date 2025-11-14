import marimo

__generated_with = "0.10.6"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import polars as pl
    import marimo as mo
    import numpy as np
    import polars_ds as pds
    from great_tables import GT 
    from plotnine import ggplot,geom_col, geom_hline,aes, geom_bar,geom_line,scale_y_continuous ,labs, coord_flip, theme_bw,theme
    import polars_xdt as xdt
    import polars.selectors as cs
    import seaborn as sns
    from utils import prep,dato_mapping_pub_trening,datoformat_mapping
    import matplotlib.pyplot as plt
    from datetime import date
    import altair as alt
    return (
        GT,
        aes,
        alt,
        coord_flip,
        cs,
        date,
        dato_mapping_pub_trening,
        datoformat_mapping,
        geom_bar,
        geom_col,
        geom_hline,
        geom_line,
        ggplot,
        labs,
        mo,
        np,
        pds,
        pl,
        plt,
        prep,
        scale_y_continuous,
        sns,
        theme,
        theme_bw,
        xdt,
    )


@app.cell(hide_code=True)
def _(dato_mapping_pub_trening, datoformat_mapping, pl, prep):
    # Les dataene
    df = pl.read_excel("treningsdata.xlsx")

    # Kjør dataprep 
    df = (df
    .pipe(datoformat_mapping)
    .pipe(dato_mapping_pub_trening)
    .pipe(prep)
    )


    df_sub = (df
    .filter(pl.col('År').eq(2025)
     .or_(
        pl.col('År').eq(2024)
       .and_(pl.col('Måned')<=6)
        )
      )
    )
    return df, df_sub


@app.cell
def _(mo):
    mo.md(
        r"""
        # Introduksjon
        Det første halvåret i 2025 har vist en eksploderende interesse for å delta på treninger. Nytt for i år er at treninger nå arrangeres hver onsdag, og ikke mandag. I tillegg til dette har det blitt satset på å "dulte" i folk. Disse endringene har hatt en effekt. Vi vil denne statistikkrapporten vise frem spennende statistikk.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        # Nøkkeltall

        I dette kapittelet presenterer vi nøkkeltall for inneværende halvår, sammenlignet med samme periode i fjor. Den første tabellen viser antall gjennomførte treninger. Totalt er det arrangert flere treninger i år enn i fjor. Dette tallet inkluderer både avlyste og gjennomførte treninger. Ca. 90% av alle arrangerte treninger ble gjennomført. Denne prosentandelen var omtrent halvert i fjor.
        """
    )
    return


@app.cell(hide_code=True)
def _(GT, cs, df, pl):
    GT(df
    .filter(pl.col('År').eq(2025)
     .or_(
        pl.col('År').eq(2024)
       .and_(pl.col('Måned')<=6)
        )
      )
    .group_by('År')
    .agg(

     pl.col('Dato')
      .n_unique()
      .alias('Totalt antall treninger'),

     pl.col('Dato')
     .filter(pl.col('Deltok')=='Ja',
             pl.col('Avlyst trening')=='Nei'
     )
     .n_unique()
     .alias('Antall arrangerte treninger')

    )

    .sort(by =['År'],descending = False)
    .with_columns(cs.contains(" ").shift(1).name.suffix(" forrige år"))
    .drop_nulls()
    .select('Totalt antall treninger',
    'Totalt antall treninger forrige år',
    'Antall arrangerte treninger',
    'Antall arrangerte treninger forrige år'
    )
    #.with_columns(pl.col('Totalt antall treninger').sub()
    )
    return


@app.cell
def _(mo):
    mo.md("""Både stemmeaktiviteten og antall personer som har vært på trening har økt.""")
    return


@app.cell(hide_code=True)
def _(GT, cs, df, pl):
    GT(df
    .filter(pl.col('År').eq(2025)
     .or_(
        pl.col('År').eq(2024)
       .and_(pl.col('Måned')<=6)
        )
      )
    .group_by('År')
    .agg(

     pl.col('Navn')
     .n_unique()
     .alias('Antall personer som har stemt'),

     pl.col('Navn')
     .filter(pl.col('Deltok')=='Ja',
             pl.col('Avlyst trening')=='Nei'
     )
     .n_unique()
     .alias('Antall personer som har deltatt på trening')


    )

    .sort(by =['År'],descending = False)
    .with_columns(cs.contains(" ").shift(1).name.suffix(" forrige år"))
    .drop_nulls()
    .select('Antall personer som har stemt',
    'Antall personer som har stemt forrige år',
    'Antall personer som har deltatt på trening',
    'Antall personer som har deltatt på trening forrige år'
    )
    )
    return


@app.cell(hide_code=True)
def _(df_sub, pl):
    antall_deltakere =  (df_sub
    .filter(
     pl.col('Avlyst trening')=='Nei',
     pl.col('Deltok')=='Ja'
     )
    .group_by('Dato','År')
    .agg(pl.col('Navn').n_unique().alias('Antall deltakere'))

    .with_columns(pl.col('År').cast(pl.Utf8),
    pl.col('Antall deltakere').mean().over('År').alias('Snitt per periode'))
    .sort(by = ['Dato'])

    )
    return (antall_deltakere,)


@app.cell(hide_code=True)
def _(antall_deltakere, pl, plt, sns):
    ax = sns.lineplot(data=antall_deltakere.to_pandas(),x = 'Dato',y = 'Antall deltakere')

    ax.tick_params(axis='x', rotation=50)
    ax.axhline(y = antall_deltakere.select('År','Snitt per periode').filter(pl.col('År')=='2024').drop('År').unique().to_series()[0],color = 'red',linewidth=2,linestyle = '--')

    ax.axhline(y = antall_deltakere.select('År','Snitt per periode').filter(pl.col('År')=='2025').drop('År').unique().to_series()[0],color = 'blue',linewidth=2,linestyle = '--')

    ax.set_title('Antall deltakere fordelt på dato og periode.\nBlå horisontal linje er gjennomsnittlig antall deltakere\nfor 2025, mens rød er for 2024.')

    ax.set_xlabel("")

    plt.gca()
    return (ax,)


@app.cell
def _(mo):
    mo.md(""" """)
    return


@app.cell(hide_code=True)
def _(df, pl, plt, sns):
    antall_treninger_per_maaned = (df
    .filter(pl.col('År').eq(2025)
     .or_(
        pl.col('År').eq(2024)
       .and_(pl.col('Måned')<=6)
        ),
             pl.col('Avlyst trening')=='Nei'
            )
    .group_by('År','Måned navn','Måned')
    .agg(pl.col('Treningsdato').n_unique().alias('Antall treninger'))
    .sort(by = ['Måned','År'])
    .with_columns(pl.col('År').cast(pl.Utf8),
    pl.col('Måned navn').cast(pl.Categorical))

    )

    ax_1 = sns.barplot(data = antall_treninger_per_maaned.to_pandas(),x = 'Måned navn',y = 'Antall treninger',hue = 'År')
    ax_1.set_xlabel("")
    plt.gca()
    return antall_treninger_per_maaned, ax_1


@app.cell
def _(mo):
    mo.md(
        r"""
        # Spillerstatistikk

        Mange spillere har flere treninger i år sammenlignet med i fjor. Dette kan være en effekt av at daglig leder har benyttet metoden "dulting" for å få spillere til å komme på trening.
        """
    )
    return


@app.cell(hide_code=True)
def _(GT, df_sub, pl):
    totalt_antall_treninger = (df_sub
    .group_by('Navn','År')
    .agg(



     pl.col('Dato')
     .filter(pl.col('Deltok')=='Ja',
             pl.col('Avlyst trening')=='Nei'
     )
     .n_unique()
     .alias('Antall treninger')
    )

    .pivot(index = ['Navn'],on = 'År',values = ['Antall treninger'])
    .fill_null(0)
    .with_columns(pl.all().exclude('Navn').cast(pl.Int64))
    .rename({'2024':'Antall treninger første halvår i 2024','2025':'Antall treninger første halvår i 2025'})
    .sort(by = ['Antall treninger første halvår i 2025'],descending = True)
    .with_columns(
    pl.col('Antall treninger første halvår i 2025').sub(pl.col('Antall treninger første halvår i 2024')).alias('Differanse'),
    pl.mean_horizontal(pl.all().exclude('Navn').alias('Gjennomsnittlig antall treninger første halvår')))

    )

    (GT(totalt_antall_treninger)
    )
    return (totalt_antall_treninger,)


@app.cell
def _(mo):
    mo.md(r"""Denne tabellen viser den lengste treningsstreaken per spiller. Igjen ser vi at det er Stian Nyheim som har knallgode tall. Det er også verdt nevne at nysegnineringen Jonas Tron Hatlem har imponerende tall.""")
    return


@app.cell(hide_code=True)
def _(GT, df_sub, pds, pl):
    GT(df_sub
    .filter(pl.col('Avlyst trening')=='Nei')
    .group_by('Navn','År')
    .agg(


     pds.query_longest_streak(pl.col('Deltok')=='Ja').alias('Lengste treningsstreak')

    )

    .pivot(index = ['Navn'],on = 'År',values = ['Lengste treningsstreak'])
    .fill_null(0)
    .sort('2025',descending = True)
    .rename({'2024':'Lengste treningsstreak i 2024','2025':'Lengste treningsstreak i 2025'})
    )
    return


if __name__ == "__main__":
    app.run()
