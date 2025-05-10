import streamlit as st
import pandas as pd
import random
import sqlite3

# Load the preprocessed dataset
features = pd.read_csv("updated_features.csv")

# Define bot responses
GREETING_RESPONSES = ["Hi! I'm your restaurant recommendation bot.", "Hello! I'm here to help you find delicious restaurants."]
CONFIRMATION_RESPONSES = ["Great choice!", "Excellent!", "Awesome!"]
FALLBACK_RESPONSES = ["I'm sorry, I didn't understand that. Can you please rephrase?", "Could you please provide more details?", "I'm not sure I follow. Let's try again."]
GOODBYE_RESPONSES = ["Goodbye! Enjoy your meal!", "See you later!"]

# Keywords for different actions
RECOMMEND_KEYWORDS = ["recommend", "suggest", "find", "show"]
BEST_FOOD_KEYWORDS = ["best food", "top dishes", "recommended items"]
BYE_KEYWORDS = ["bye", "goodbye", "see you", "exit"]

# Function to select a random response
def get_response(responses):
    return random.choice(responses)

# Connect to SQLite database
conn = sqlite3.connect('user_credentials.db')
c = conn.cursor()

# Create table for user credentials
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT)''')

# Streamlit app layout
st.title("Food Recommender System")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Registration
st.sidebar.title("User Registration")
new_username = st.sidebar.text_input("New Username", key="new_username")
new_password = st.sidebar.text_input("New Password", type="password", key="new_password")

if st.sidebar.button("Register"):
    if new_username and new_password:
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, new_password))
            conn.commit()
            st.sidebar.success("Registration successful!")
        except sqlite3.IntegrityError:
            st.sidebar.error("Username already exists. Please choose a different one.")
    else:
        st.sidebar.error("Username and password are required!")

# Login
st.sidebar.title("User Login")
username = st.sidebar.text_input("Username", key="username")
password = st.sidebar.text_input("Password", type="password", key="password")

if st.sidebar.button("Login"):
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    if user:
        st.sidebar.success(f"Welcome back, {username}!")
        st.sidebar.info("You're logged in!")
        st.session_state.logged_in = True  # Set login status to True
    else:
        st.sidebar.error("Incorrect username or password.")

# Chatbot-like conversation
if st.session_state.logged_in:  # Display recommendation system only if user is logged in
    user_input = st.text_input("You: ", "Hi!!")

    if any(keyword in user_input.lower() for keyword in RECOMMEND_KEYWORDS):
        st.write("FoodBRO:", get_response(["Sure! What type of cuisine are you in the mood for?", "Absolutely! What cuisine would you like to try?"]))
        cuisine_input = st.text_input("You: ", "")

        if not cuisine_input.strip():
            st.write("FoodBRO:", get_response(FALLBACK_RESPONSES))
        else:
            st.text("FoodBRO: And in which city are you located?")
            city_input = st.text_input("", "")
            if not city_input.strip():
                st.write("FoodBRO:", get_response(FALLBACK_RESPONSES))
            else:
                st.write("FoodBRO:", get_response(["Got it! Let me find some restaurants for you."]))

                # Perform recommendation based on user preferences
                preferred_cuisines = [cuisine.strip() for cuisine in cuisine_input.split(",")]
                preferred_restaurants = features[(features[preferred_cuisines].any(axis=1)) & (features['Location'].str.lower() == city_input.lower())]
                if len(preferred_restaurants) > 0:
                    st.write("FoodBRO:", get_response(CONFIRMATION_RESPONSES), f"Here are some top restaurants for {', '.join(preferred_cuisines)} in {city_input}:")
                    st.write(preferred_restaurants[['Restaurant Name', 'Rating', 'Average Price', 'Location']].reset_index(drop=True)[:5])
                else:
                    st.write("FoodBRO:", "Sorry, I couldn't find any restaurants matching your preferences in", city_input + ".")

    elif any(keyword in user_input.lower() for keyword in BEST_FOOD_KEYWORDS):
        st.write("FoodBRO:", get_response(["Sure! What type of cuisine are you interested in?"]))
        cuisine_input = st.text_input("You: ", "")
        if not cuisine_input.strip():
            st.write("FoodBRO:", get_response(FALLBACK_RESPONSES))
        else:
            st.text("FoodBRO: And in which city are you located?")
            city_input = st.text_input("", "")
            if not city_input.strip():
                st.write("FoodBRO:", get_response(FALLBACK_RESPONSES))
            else:
                st.write("FoodBRO:", get_response(["Got it! Let me find the best food items for you in", city_input + "."]))

                # Perform recommendation based on city and cuisine
                top_restaurants_city_cuisine = features[(features['Location'].str.lower() == city_input.lower()) & (features[cuisine_input.strip()].astype(bool))].nlargest(5, 'Rating')
                if not top_restaurants_city_cuisine.empty:
                    st.write("FoodBRO:", f"Here are the top-rated restaurants for {cuisine_input} cuisine in {city_input}:")
                    st.write(top_restaurants_city_cuisine[['Restaurant Name', 'Rating', 'Average Price', 'Location']].reset_index(drop=True))
                else:
                    st.write("FoodBRO:", f"Sorry, I couldn't find any top-rated restaurants for {cuisine_input} cuisine in {city_input}.")

    elif any(keyword in user_input.lower() for keyword in BYE_KEYWORDS):
        st.write("FoodBRO:", get_response(GOODBYE_RESPONSES))
    else:
        if user_input.strip() != "":
            st.write("FoodBRO:", get_response(FALLBACK_RESPONSES))
else:
    st.write("Please log in to access the recommendation system.")
