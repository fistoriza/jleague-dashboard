import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
import pandas as pd
import time
from datetime import datetime
import pytz

# st_autorefresh(interval=60000, key="autorefresh")

API_KEY = "HbrDmsYhYjDBKF7Z"
SECRET = "ytzv9WWaSohrEXrm8TZvmYMlipW2431D"

url = f"https://livescore-api.com/api-client/fixtures/matches.json?competition_id=28&key={API_KEY}&secret={SECRET}"

def convert_to_perth(date, time):
    try:
        utc = pytz.utc
        perth = pytz.timezone("Australia/Perth")
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        dt_utc = utc.localize(dt)
        dt_perth = dt_utc.astimezone(perth)
        return dt_perth.strftime("%H:%M")
    except:
        return time

response = requests.get(url)
data = response.json()

matches = data["data"]["fixtures"]

df = pd.DataFrame(matches)

st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B;'>⚽ J-League Dashboard</h1>
    <hr style='border: 1px solid #FF4B4B;'>
""", unsafe_allow_html=True)

st.subheader("Live Scores")

live_url = f"https://livescore-api.com/api-client/matches/live.json?competition_id=28&key={API_KEY}&secret={SECRET}"

live_response = requests.get(live_url)
live_data = live_response.json()

live_matches = live_data["data"]["match"]

if len(live_matches) == 0:
    st.info("No live matches at the moment.")
else:
    df_live = pd.DataFrame(live_matches)
    df_live = df_live[["home_name", "away_name", "score", "time"]]
    df_live.rename(columns={
        "home_name": "Home Team",
        "away_name": "Away Team",
        "score": "Score",
        "time": "Time"
    }, inplace=True)    
    st.dataframe(df_live, hide_index=True)

st.metric("Total Upcoming Fixtures", len(df))
st.subheader("Upcoming Fixtures")

df["time"] = df.apply(lambda row: convert_to_perth(row["date"], row["time"]), axis=1)
df = df[["date", "time", "home_name", "away_name", "location"]]

df.rename(columns={
    "date": "Date",
    "time": "Time",
    "home_name": "Home Team",
    "away_name": "Away Team",
    "location": "Location"
}, inplace=True)

search = st.text_input("Search by team name")
if search:
    df = df[df["Home Team"].str.contains(search, case=False) | df["Away Team"].str.contains(search, case=False)]

st.dataframe(df, hide_index=True)

standings_url = f"https://livescore-api.com/api-client/leagues/table.json?competition_id=28&key={API_KEY}&secret={SECRET}"

standings_response = requests.get(standings_url)
standings_data = standings_response.json()

standings = standings_data["data"]["table"]
df_standings = pd.DataFrame(standings)

df_standings = df_standings[["rank", "name", "matches", "won", "drawn", "lost", "goals_scored", "goals_conceded", "goal_diff", "points", "group_name"]]
df_standings.rename(columns={
    "rank": "Rank",
    "name": "Team",
    "matches": "M",
    "won": "W",
    "drawn": "D",
    "lost": "L",
    "goals_scored": "GS",
    "goals_conceded": "GC",
    "goal_diff": "GD",
    "points": "Pts",
    "group_name": "Div"}, inplace=True)

st.subheader("J-League Standings")

east = df_standings[df_standings["Div"] == "East"]
west = df_standings[df_standings["Div"] == "West"]

st.markdown("**East Division**")
st.dataframe(east.drop(columns=["Div"]), hide_index=True)

st.markdown("**West Division**")
st.dataframe(west.drop(columns=["Div"]), hide_index=True)

results_url = f"https://livescore-api.com/api-client/scores/history.json?competition_id=28&key={API_KEY}&secret={SECRET}"

results_response = requests.get(results_url)
results_data = results_response.json()

matches = results_data["data"]["match"]
df_results = pd.DataFrame(matches)

df_results = df_results[["date", "home_name", "away_name", "score", "ht_score", "status"]]
df_results.rename(columns={
    "date": "Date",
    "home_name": "Home Team",
    "away_name": "Away Team",
    "score": "FT Score",
    "ht_score": "HT Score",
    "status": "Status"
}, inplace=True)

st.subheader("Recent Results")

results_url = f"https://livescore-api.com/api-client/scores/history.json?competition_id=28&from=2025-08-01&to=2026-02-19&key={API_KEY}&secret={SECRET}"
results_response = requests.get(results_url)
results_data = results_response.json()
total_pages = results_data["data"]["total_pages"]

# Fetch last page only for speed
last_url = f"https://livescore-api.com/api-client/scores/history.json?competition_id=28&from=2025-08-01&to=2026-02-19&page={total_pages}&key={API_KEY}&secret={SECRET}"
last_response = requests.get(last_url)
last_data = last_response.json()

matches = last_data["data"]["match"]
df_results = pd.DataFrame(matches)
df_results = df_results.sort_values("date", ascending=False).head(10)
df_results = df_results[["date", "home_name", "away_name", "score", "ht_score", "status"]]
st.dataframe(df_results, hide_index=True)