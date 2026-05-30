import pandas as pd
import streamlit as st
import plotly.express as px

#Setting configuration

st.set_page_config(
    page_title="Global Income Inequality Dashboard",
    page_icon="🌍",
    layout="wide")

#Loading data

@st.cache_data
def load_data():
    df = pd.read_excel("GCIPrawdata.xlsx")
    df.columns = df.iloc[1]
    df = df[2:].reset_index(drop=True)
    return df
df = load_data()

#Creating new columns

df["TopBottomRatio"] = (
    df["Decile 10 Income"] /
    df["Decile 1 Income"])
df["Top10Share"] = (
    df["Decile 10 Income"] /
    df.loc[:, 'Decile 1 Income':'Decile 10 Income'].sum(axis=1))
df["Bottom10Share"] = (
    df["Decile 1 Income"] /
    df.loc[:, 'Decile 1 Income':'Decile 1 Income'].sum(axis=1))

#Sidebar editing

st.sidebar.title("Filters")

selected_country = st.sidebar.selectbox("Country",sorted(df["Country"].unique()))

selected_year = st.sidebar.slider(
    "Year",
    int(df["Year"].min()),
    int(df["Year"].max()),
    int(df["Year"].max()))

#Creating a dataset for a chosen country and chosen year

country_df = (df[df["Country"] == selected_country].sort_values("Year"))

chosen_country = (country_df[country_df["Year"] == selected_year].iloc[0])

#Displaying stats exactly for the year chosen

st.subheader('Stats for a Chosen Year')

#KPI Cards

col1, col2, col3, col4 = st.columns(4)

col1.metric("Mean Income", round(chosen_country["Mean Income"], 2))

col2.metric("Population", f"{chosen_country['Population']/1000000:.2f}M")

col3.metric("Top/Bottom Ratio", round(chosen_country["TopBottomRatio"], 1))

col4.metric("Top Decile Share", f"{100*chosen_country['Top10Share']:.2f}%")

#Function for updating font sizes on diagrams

def style_figure(fig):
    fig.update_layout(
        title_font_size=24,
        font_size=15,
        xaxis_title_font_size=18,
        yaxis_title_font_size=18,
        height=600)
    return fig

#Bar chart showing income relative to the income of first decile

deciles = pd.DataFrame({
    "Decile": range(1,11),
    "Ratio": [
         chosen_country[f"Decile {i} Income"] /
         chosen_country["Decile 1 Income"]
        for i in range(1,11)
    ]
})

decile_fig = px.bar(
    deciles,
    x="Decile",
    y="Ratio",
    text_auto=".1f",
    title="Income Relative to the Poorest Decile"
)

decile_fig.update_yaxes(title="Times richer than Decile 1")

decile_fig = style_figure(decile_fig)

st.plotly_chart(decile_fig, use_container_width=True)

#Stats combining all the years for a chosen country

st.subheader('Overall stats')

#Line chart with mean income

fig_mean_income = px.line(
    country_df,
    x="Year",
    y="Mean Income",
    markers=True,
    title="Mean Income Through Time"
)

fig_mean_income = style_figure(fig_mean_income)

st.plotly_chart(fig_mean_income, use_container_width=True)

#Line chart with TopBottomRatio

fig_top_bottom = px.line(
    country_df,
    x="Year",
    y="TopBottomRatio",
    markers=True,
    title="Income Inequality Through Time"
)

fig_top_bottom = style_figure(fig_top_bottom)

fig_top_bottom.update_yaxes(tickformat=",.1f")

st.plotly_chart(fig_top_bottom, use_container_width=True)

#Heatmap with income evolution across deciles relative to the income of 1 decile

heatmap = country_df.copy()

for i in range(1,10):
    heatmap[f"Decile {i} Income (times)"] = (
        heatmap[f"Decile {i} Income"]
        /
        heatmap["Decile 1 Income"]
    )

heatmap_df = pd.concat(
    [heatmap.loc[:, 'Decile 1 Income (times)':'Decile 9 Income (times)'], 
     heatmap[['Year']]], 
     axis=1).set_index('Year')

fig_heatmap = px.imshow(
    heatmap_df.T,
    aspect="auto",
    labels={
        "x":"Year",
        "y":"Decile",
        "color":"Income"
    },
    title="Income Evolution Across Deciles (without the richest one)"
)

fig_heatmap = style_figure(fig_heatmap)

st.plotly_chart(fig_heatmap, use_container_width=True)

#Raw dataset

st.subheader("Full Country Dataset")

st.dataframe(country_df.iloc[:, :-1], use_container_width=True)


