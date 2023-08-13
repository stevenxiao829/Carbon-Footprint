import pprint
import streamlit as st
import google.generativeai as palm
import pandas as pd
palm.configure(api_key='AIzaSyATRWBWwqP1AYY1gNJEHvKPKSBWorFABv8')
df = pd.read_csv("datafinal.csv")

models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name



# Define emission factors (example values, replace with accurate data)
EMISSION_FACTORS = {
    "India": {
        "Transportation": 0.14,  # kgCO2/km
        "Electricity": 0.82,  # kgCO2/kWh
        "Diet": 1.25,  # kgCO2/meal, 2.5kgco2/kg
        "Waste": 0.1  # kgCO2/kg
    }
     ,"United States": {
        "Transportation": 0.14,  # kgCO2/km
        "Electricity": 0.82,  # kgCO2/kWh
        "Diet": 2,  # kgCO2/meal, 2.5kgco2/kg
        "Waste": 0.1  # kgCO2/kg
    }
     , "Default": {
        "Transportation": 0.14,  # kgCO2/km
        "Electricity": 0.82,  # kgCO2/kWh
        "Diet": 1.25,  # kgCO2/meal, 2.5kgco2/kg
        "Waste": 0.1  # kgCO2/kg
    }
}

# Set wide layout and page name
st.set_page_config(layout="wide", page_title="Personal Carbon Calculator", page_icon="🌍")

# Streamlit app code
st.title("Personal Carbon Calculator App ⚠️")

# User inputs
st.subheader("🌍 Your Country")
country = st.selectbox("Select", list(df.Area.unique()), index=203)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Daily commute distance (in km)")
    distance = st.slider("Distance", 0.0, 100.0, key="distance_input")

    st.subheader("💡 Monthly electricity consumption (in kWh)")
    electricity = st.slider("Electricity", 0.0, 1000.0, key="electricity_input")

with col2:
    st.subheader("🍽️ Waste generated per week (in kg)")
    waste = st.slider("Waste", 0.0, 100.0, key="waste_input")

    st.subheader("🍽️ Number of meals per day")
    meals = st.number_input("Meals", 0, key="meals_input")

# Normalize inputs
if distance > 0:
    distance = distance * 365  # Convert daily distance to yearly
if electricity > 0:
    electricity = electricity * 12  # Convert monthly electricity to yearly
if meals > 0:
    meals = meals * 365  # Convert daily meals to yearly
if waste > 0:
    waste = waste * 52  # Convert weekly waste to yearly

# Calculate carbon emissions
transportation_emissions = EMISSION_FACTORS["Default"]["Transportation"] * distance
electricity_emissions = EMISSION_FACTORS["Default"]["Electricity"] * electricity
diet_emissions = EMISSION_FACTORS["Default"]["Diet"] * meals
waste_emissions = EMISSION_FACTORS["Default"]["Waste"] * waste

# Convert emissions to tons and round off to 2 decimal points
transportation_emissions = round(transportation_emissions / 1000, 2)
electricity_emissions = round(electricity_emissions / 1000, 2)
diet_emissions = round(diet_emissions / 1000, 2)
waste_emissions = round(waste_emissions / 1000, 2)

# Calculate total emissions
total_emissions = round(
    transportation_emissions + electricity_emissions + diet_emissions + waste_emissions, 2
)

if st.button("Calculate CO2 Emissions"):

    # Display results
    st.header("Results")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Carbon Emissions by Category")
        st.info(f"🚗 Transportation: {transportation_emissions} tons CO2 per year")
        st.info(f"💡 Electricity: {electricity_emissions} tons CO2 per year")
        st.info(f"🍽️ Diet: {diet_emissions} tons CO2 per year")
        st.info(f"🗑️ Waste: {waste_emissions} tons CO2 per year")

    with col4:
        st.subheader("Total Carbon Footprint")
        st.success(f"🌍 Your total carbon footprint is: {total_emissions} tons CO2 per year")
        st.warning("Between 1972 and 2021, CO2 emissions per capita of the world grew substantially from 1.3 to 4.8 tons of CO2 per capita rising at an increasing annual rate that reached a maximum of 9.41% in 2021.")

# Check if all inputs have been filled
if distance > 0 and electricity > 0 and meals > 0 and waste > 0:
    prompt = f"""
            Pretend you are an expert environmentalist and lifestyle analyst.
            Provide detailed actionable suggestions to reduce my carbon footprint.
            I travel {distance} kilometers daily and my annual electricity consumption is {electricity} kWh.
            I have {meals} meals per day and I produce {waste} kilograms of waste per week.
            My calculated carbon footprint is {total_emissions} tons CO2 per year.
            My country is {country}. Compare my carbon footprint to the average {country} citizen and suggest actionable advise relevant to my country.
            Make sure to include suggestions in all of the categories and provide a detailed explanation for each suggestion.
            """


    with st.spinner("Generating suggestions... You are on your way to make a positive impact on the environment! 🌍"):
        # Start generating the text
        completion = palm.generate_text(
            model=model,
            prompt=prompt,
            temperature=0.1,  # You can adjust the temperature for more diverse responses
            max_output_tokens=1024,  # You can adjust the length of the response
        )

        # Update the output container with the generated text
        st.markdown(completion.result)

else:
    st.warning("Please fill in all the inputs to generate suggestions.")

