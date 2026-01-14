import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(
    page_title="Netflix Data Analysis Dashboard",
    layout="wide"
)


@st.cache_data
def load_data():
    df = pd.read_csv("netflix.csv", encoding="latin1")
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    return df

df = load_data()

st.title("Netflix Data Analysis Dashboard")
st.markdown("An interactive dashboard to analyze Netflix movies and TV shows.")

st.sidebar.header("Filters")

type_filter = st.sidebar.multiselect(
    "Content Type",
    options=df['type'].unique(),
    default=df['type'].unique()
)

year_filter = st.sidebar.slider(
    "Year Added",
    int(df['year_added'].min()),
    int(df['year_added'].max()),
    (2016, 2021)
)

rating_filter = st.sidebar.multiselect(
    "Rating",
    options=df['rating'].dropna().unique(),
    default=df['rating'].dropna().unique()
)

search_query = st.sidebar.text_input("Search by Title")

sort_option = st.sidebar.selectbox(
    "Sort Results By",
    ["Release Year", "Title"]
)

filtered_df = df[
    (df['type'].isin(type_filter)) &
    (df['year_added'].between(year_filter[0], year_filter[1])) &
    (df['rating'].isin(rating_filter))
]

if search_query:
    filtered_df = filtered_df[
        filtered_df['title'].str.contains(search_query, case=False, na=False)
    ]

if sort_option == "Release Year":
    filtered_df = filtered_df.sort_values("release_year", ascending=False)
else:
    filtered_df = filtered_df.sort_values("title")

col1, col2, col3 = st.columns(3)
col1.metric("Total Titles", filtered_df.shape[0])
col2.metric("Movies", filtered_df[filtered_df['type'] == 'Movie'].shape[0])
col3.metric("TV Shows", filtered_df[filtered_df['type'] == 'TV Show'].shape[0])

st.subheader("Movies vs TV Shows")

fig1, ax1 = plt.subplots()
sns.countplot(x='type', data=filtered_df, ax=ax1)
ax1.set_xlabel("")
ax1.set_ylabel("Count")
st.pyplot(fig1)

st.subheader("Content Added Over Years")

year_data = filtered_df['year_added'].value_counts().sort_index()
fig2, ax2 = plt.subplots()
ax2.plot(year_data.index, year_data.values, marker='o')
ax2.set_xlabel("Year")
ax2.set_ylabel("Number of Titles")
st.pyplot(fig2)

st.subheader("Top Genres")

genres = filtered_df.copy()
genres['listed_in'] = genres['listed_in'].str.split(', ')
genres = genres.explode('listed_in')

top_genres = genres['listed_in'].value_counts().head(10)
fig3, ax3 = plt.subplots()
top_genres.plot(kind='bar', ax=ax3)
ax3.set_xlabel("Genre")
ax3.set_ylabel("Count")
st.pyplot(fig3)

st.subheader("Top Content Producing Countries")

top_countries = filtered_df['country'].value_counts().head(10)
fig4, ax4 = plt.subplots()
top_countries.plot(kind='barh', ax=ax4)
ax4.set_xlabel("Count")
ax4.set_ylabel("Country")
st.pyplot(fig4)

st.subheader("Content Details")

for _, row in filtered_df.head(10).iterrows():
    with st.expander(row['title']):
        st.write("Type:", row['type'])
        st.write("Country:", row['country'])
        st.write("Rating:", row['rating'])
        st.write("Duration:", row['duration'])
        st.write("Description:", row['description'])

st.download_button(
    label="Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_netflix_data.csv",
    mime="text/csv"
)
