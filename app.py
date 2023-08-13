import pprint
import streamlit as st
import google.generativeai as palm
import pandas as pd
palm.configure(api_key='AIzaSyATRWBWwqP1AYY1gNJEHvKPKSBWorFABv8') # need to remove/hide
df = pd.read_csv("datafinal.csv")

models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name



# Define emission factors (example values, replace with accurate data)
# https://www.scu.edu/media/ethics-center/environmental-ethics/carbon-footprint/Math_and_Methodologies_Behind_This_Calculator.pdf
EMISSION_FACTORS = {
       "Default": {
        "Transportation": 0.40935,  # kgCO2/km
        "Diet": 1.25,  # kgCO2/meal, 2.5kgco2/kg
        "Waste": 0.1  # kgCO2/kg
    }
}

# Set page config
st.set_page_config(layout="wide", page_title="EcoGuide - Carbon Footprint Analysis", page_icon="🌍")

# Set title
st.title("EcoGuide - Carbon Footprint Analysis 🌍")

# input GUI
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
    meals = st.number_input("Meals", 0, key="meals_input", default=3)

# Normalize inputs
if distance > 0:
    distance_yearly = distance * 365  # Convert daily distance to yearly
if electricity > 0:
    electricity_yearly = electricity * 12  # Convert monthly electricity to yearly
if meals > 0:
    meals_yearly = meals * 365  # Convert daily meals to yearly
if waste > 0:
    waste_yearly = waste * 52  # Convert weekly waste to yearly

if distance > 0 and electricity > 0 and meals > 0 and waste > 0:
    # Calculate carbon emissions
    transportation_emissions = EMISSION_FACTORS["Default"]["Transportation"] * distance_yearly
    diet_emissions = EMISSION_FACTORS["Default"]["Diet"] * meals_yearly
    waste_emissions = EMISSION_FACTORS["Default"]["Waste"] * waste_yearly

    # Convert emissions to tons and round off to 2 decimal points
    transportation_emissions = round(transportation_emissions / 1000, 2)
    dfCountry = df[df.Area == country]
    dfCountry = dfCountry[dfCountry.Year == dfCountry['Year'].max()]
    percent_elec_coal = dfCountry.loc[dfCountry['Variable'] == 'Coal', 'Value'].item()
    percent_elec_gas = dfCountry.loc[dfCountry['Variable'] == 'Gas', 'Value'].item()
    percent_elec_oil = dfCountry.loc[dfCountry['Variable'] == 'Other Fossil', 'Value'].item()
    percent_elec_clean = dfCountry.loc[dfCountry['Variable'] == 'Clean', 'Value'].item()
    electricity_emissions_coal = (electricity_yearly * (percent_elec_coal/100) * 1.025)/1000
    electricity_emissions_gas = (electricity_yearly * (percent_elec_gas/100) * 0.443)/1000
    electricity_emissions_oil = (electricity_yearly * (percent_elec_oil/100) * 1.11)/1000
    electricity_emissions_yearly = round(electricity_emissions_coal + electricity_emissions_gas + electricity_emissions_oil, 2)
    # source https://www.eia.gov/tools/faqs/faq.php?id=74&t=11
    # 1.025 kg CO2 per kWh for coal
    # 0.443 kg CO2 per kWh for natural gas
    # 1.11 kg CO2 per kWh for oil

    diet_emissions = round(diet_emissions / 1000, 2)
    waste_emissions = round(waste_emissions / 1000, 2)

    # Calculate total emissions
    total_emissions = round(
        transportation_emissions + electricity_emissions_yearly + diet_emissions + waste_emissions, 2
    )

    if st.button("Calculate CO2 Emissions"):

        # Display results
        st.header("Results")

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Carbon Emissions by Category")
            st.info(f"🚗 Transportation: {transportation_emissions} tons CO2 per year")
            st.info(f"💡 Electricity: {electricity_emissions_yearly} tons CO2 per year")
            st.info(f"🍽️ Diet: {diet_emissions} tons CO2 per year")
            st.info(f"🗑️ Waste: {waste_emissions} tons CO2 per year")

    # https://www.viessmann.co.uk/en/heating-advice/boilers/how-much-co2-does-tree-absorb.html for 1 tree = 20 kg CO2 per year
        with col4:
            st.subheader("Total Carbon Footprint")
            st.success(f"🌍 Your total carbon footprint is: {total_emissions} tons CO2 per year")
            st.warning("Between 1972 and 2021, CO2 emissions per capita of the world grew substantially from 1.3 to 4.8 tons of CO2 per capita rising at an increasing annual rate that reached a maximum of 9.41% in 2021.")

        with st.expander("🌲's needed to offset your carbon footprint", expanded=True):
            st.info(f"You would need to plant {round((total_emissions * 1000)/20)} trees 🌲 to offset your yearly carbon footprint.")

    # Check if all inputs have been filled
        if distance > 0 and electricity > 0 and meals > 0 and waste > 0:
            prompt = f"""
                    Pretend you are an expert environmentalist and lifestyle analyst.
                    Provide detailed actionable suggestions to reduce my carbon footprint.
                    I travel {distance} kilometers daily and my annual electricity consumption is {electricity} kWh.
                    I have {meals} meals per day and I produce {waste} kilograms of waste per week.
                    My calculated carbon footprint is {total_emissions} tons CO2 per year.
                    The electricity in my country is {percent_elec_coal}% coal, {percent_elec_gas}% natural gas, {percent_elec_oil}% oil, and {percent_elec_clean}% clean energy.
                    The electricity emissions generated by me is {electricity_emissions_yearly} tons CO2 per year.
                    The waste emissions generated by me is {waste_emissions} tons CO2 per year.
                    The diet emissions generated by me is {diet_emissions} tons CO2 per year.
                    The transportation emissions generated by me is {transportation_emissions} tons CO2 per year.
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
                
        st.success("Thank you for using our app! Be sure to follow our suggestions! 🌍")

    else:
        st.warning("Please fill in all the inputs to generate suggestions and calculate your emissions.")

