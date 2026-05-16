import streamlit as st

st.title("Weather Test")

weather = {
    "City": ["Santiago", "Lima", "Cartagena"],
    "Temperature": [72, 81, 88]
}

st.write(weather)