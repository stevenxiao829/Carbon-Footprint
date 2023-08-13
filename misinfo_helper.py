import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development

import google.generativeai as palm
palm.configure(api_key='AIzaSyATRWBWwqP1AYY1gNJEHvKPKSBWorFABv8')

st.set_page_config(
    page_title="EcoGuide - Climate Change Information",
    page_icon="🌍",
    layout="wide",
)

def get_data() -> pd.DataFrame:
    return pd.read_csv('Annual_Surface_Temperature_Change.csv')

df = get_data()

# dashboard title
st.title("EcoGuide - Climate Change Information 🌍")

# top-level filters
country_filter = st.selectbox("Select the country", pd.unique(df["Country"]))

# creating a single-element container
placeholder = st.empty()

# Row of years
years = []
years_no_f = []
for i in range(61):
    years.append('F' + str(1961 + i))
    years_no_f.append(1961 + i)

# dataframe filter
df = df[df["Country"] == country_filter]
temperature_list = df[years]

# plotly chart with labels
fig = px.line(
    df,
    x=years_no_f,
    y=np.array(temperature_list)[0],
    title=f"Annual Surface Temperature Change in {country_filter}",
    labels={"x": "Year", "y": "Temperature Change (°C)"},
)

# Make chart animated

fig.update_traces(mode="lines+markers")
fig.update_layout(hovermode="x")

# plotly chart update
placeholder.plotly_chart(fig)

# Change in temperature for country from 1961 to 2022
change_in_temp = df[years].sum(axis=1)

models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name

# Get input from the user
inp = st.text_input('Do you have any questions about climate change to ask?')
# Add a submit button
if st.button('Submit'):
    # Add a placeholder
    placeholder = st.empty()
    # Add a loading indicator
    with st.spinner('Generating your response...'):
        # Generate the text
        prompt = (
        "Pretend you are an expert on climate change."
        "Please respond to this question " + inp
        )
        completion = palm.generate_text(
            model=model,
            prompt=prompt,
            temperature=0.7,  # You can adjust the temperature for more diverse responses
            max_output_tokens=200,  # You can adjust the length of the response
        )
        # Remove the loading indicator
        placeholder.empty()
        # Update the output container with the generated text
        st.markdown(completion.result)