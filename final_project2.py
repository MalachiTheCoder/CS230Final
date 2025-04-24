"""
Name:       Hunter Malachi S.
CS230:      Section 6
Data:       Skyscraper Dataset
URL:        [Your Streamlit Cloud URL Here]

"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk

# [PY1] - [PY2]
def get_top_buildings(data, column, n=10):
    sorted_df = data.sort_values(column, ascending=False).head(n)
    names = list(sorted_df['name'])
    heights = list(sorted_df[column])
    return sorted_df, names, heights

# [PY3]
try:
    df = pd.read_csv("skyscrapers.csv")
except FileNotFoundError:
    st.error("Data file not found. Please make sure 'skyscrapers.csv' is in the same directory.")

# [DA1]
df["location.country"] = df["location.country"].replace({
    "US": "United States",
    "U.S.": "United States"
})

# [DA9]
df["status.completed.year"] = pd.to_numeric(df["status.completed.year"], errors="coerce")
df = df[df["status.completed.year"] >= 1800]
df["Decade"] = (df["status.completed.year"] // 10) * 10

# [DA2] - [DA8]
df = df.dropna(subset=[
    "location.country",
    "location.city",
    "location.latitude",
    "location.longitude",
    "statistics.height",
    "status.completed.year"
])
df_demo = df[["name", "location.city", "statistics.height"]]  # [DA7] subset
continent_df = df[["location.country", "location.country id"]].drop_duplicates()
df = pd.merge(df, continent_df, on="location.country", how="left")  # [DA8] mock merge

# [ST1] - [ST3]
st.sidebar.title("Skyscraper Explorer")
tab = st.sidebar.radio("Select View:", ["Cities by Total Skyscraper Height", "Tallest in United States", "Construction Trends"])

if tab == "Cities by Total Skyscraper Height":
    st.title("Cities by Total Skyscraper Height")
    city_sum = df.groupby("location.city")["statistics.height"].sum().reset_index()
    city_sum["formatted"] = city_sum["statistics.height"].apply(lambda x: f"{x:.0f} meters") # [DA1]
    city_sum = city_sum.sort_values("statistics.height", ascending=False).head(10)

    st.subheader("Top 10 Cities by Total Skyscraper Height")
    fig, ax = plt.subplots()
    ax.barh(city_sum["location.city"], city_sum["statistics.height"], color="steelblue")
    ax.invert_yaxis()
    ax.set_xlabel("Total Height (meters)")
    st.pyplot(fig)

elif tab == "Tallest in United States":
    st.title("Tallest Skyscrapers by Country")
    country = st.sidebar.selectbox("Select Country", sorted(df["location.country"].dropna().unique()))
    df_country = df[df["location.country"] == country]
    top_df, names, heights = get_top_buildings(df_country, "statistics.height")

    st.subheader(f"Top 10 Tallest Buildings in {country}")
    fig, ax = plt.subplots()
    ax.barh(names, heights, color="skyblue")
    ax.invert_yaxis()
    ax.set_xlabel("Height (meters)")
    st.pyplot(fig)

    st.subheader("Map of Cities with the Top Skyscrapers")
    map_data = top_df[["location.latitude", "location.longitude", "name"]]
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=map_data["location.latitude"].mean(),
            longitude=map_data["location.longitude"].mean(),
            zoom=4,
            pitch=45,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position='[location.longitude, location.latitude]',
                get_radius=10000,
                get_color='[200, 30, 0, 160]',
                pickable=True,
            )
        ],
        tooltip={"text": "{name}"},
    ))

elif tab == "Construction Trends":
    st.title("Skyscraper Construction Trends Since 1800")
    filter_type = st.sidebar.radio("Filter by:", ["Country", "City"])
    if filter_type == "Country":
        value = st.sidebar.selectbox("Select Country", sorted(df["location.country"].dropna().unique()))
        df_filtered = df[df["location.country"] == value]
    else:
        value = st.sidebar.selectbox("Select City", sorted(df["location.city"].dropna().unique()))
        df_filtered = df[df["location.city"] == value]

    trend = df_filtered.groupby("Decade").size().reset_index(name="Count")
    trend["Decade"] = trend["Decade"].apply(lambda x: f"{int(x)}s")
    st.subheader(f"Skyscrapers Built per Decade in {value}")

    fig, ax = plt.subplots()
    ax.plot(trend["Decade"], trend["Count"], marker="o", color="green")
    ax.tick_params(axis='x', labelrotation=45)
    ax.set_xlabel("Decade")
    ax.set_ylabel("Number of Skyscrapers")
    ax.set_title("Construction Trends Over Time")
    st.pyplot(fig)
