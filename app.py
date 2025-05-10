import streamlit as st
import pandas as pd
import random

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

# Streamlit app layout
st.title("Food Recommender System")

# Chatbot-like conversation
user_input = st.text_input("You: ", "Hi!")

if any(keyword in user_input.lower() for keyword in RECOMMEND_KEYWORDS):
    st.write("Bot:", get_response(["Sure! What type of cuisine are you in the mood for?", "Absolutely! What cuisine would you like to try?"]))
    cuisine_input = st.text_input("You: ", "")

    if not cuisine_input.strip():
        st.write("Bot:", get_response(FALLBACK_RESPONSES))
    else:
        st.text("Bot: And in which city are you located?")
        city_input = st.text_input("", "")
        if not city_input.strip():
            st.write("Bot:", get_response(FALLBACK_RESPONSES))
        else:
            st.write("Bot:", get_response(["Got it! Let me find some restaurants for you."]))

            # Perform recommendation based on user preferences
            preferred_cuisines = [cuisine.strip() for cuisine in cuisine_input.split(",")]
            preferred_restaurants = features[(features[preferred_cuisines].any(axis=1)) & (features['Location'].str.lower() == city_input.lower())]
            if len(preferred_restaurants) > 0:
                st.write("Bot:", get_response(CONFIRMATION_RESPONSES), f"Here are some top restaurants for {', '.join(preferred_cuisines)} in {city_input}:")
                st.write(preferred_restaurants[['Restaurant Name', 'Rating', 'Average Price', 'Location']][:5])
            else:
                st.write("Bot:", "Sorry, I couldn't find any restaurants matching your preferences in", city_input + ".")

elif any(keyword in user_input.lower() for keyword in BEST_FOOD_KEYWORDS):
    st.write("Bot:", get_response(["Sure! What type of cuisine are you interested in?"]))
    cuisine_input = st.text_input("You: ", "")
    if not cuisine_input.strip():
        st.write("Bot:", get_response(FALLBACK_RESPONSES))
    else:
        st.text("Bot: And in which city are you located?")
        city_input = st.text_input("", "")
        if not city_input.strip():
            st.write("Bot:", get_response(FALLBACK_RESPONSES))
        else:
            st.write("Bot:", get_response(["Got it! Let me find the best food items for you in", city_input + "."]))

            # Perform recommendation based on city and cuisine
            top_restaurants_city_cuisine = features[(features['Location'].str.lower() == city_input.lower()) & (features[cuisine_input.strip()].astype(bool))].nlargest(5, 'Rating')
            if not top_restaurants_city_cuisine.empty:
                st.write("Bot:", f"Here are the top-rated restaurants for {cuisine_input} cuisine in {city_input}:")
                st.write(top_restaurants_city_cuisine[['Restaurant Name', 'Rating', 'Average Price', 'Location']])
            else:
                st.write("Bot:", f"Sorry, I couldn't find any top-rated restaurants for {cuisine_input} cuisine in {city_input}.")

elif any(keyword in user_input.lower() for keyword in BYE_KEYWORDS):
    st.write("Bot:", get_response(GOODBYE_RESPONSES))
else:
    if user_input.strip() != "":
        st.write("Bot:", get_response(FALLBACK_RESPONSES))
