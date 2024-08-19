import streamlit as st
import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
import random

# Define the suits and ranks
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

DECK = [(rank, suit) for suit in SUITS for rank in RANKS]
    
# Updated initial_hand function
def initial_hand(deck, size=2):
    cards = random.sample(deck, size)
    return cards

# Function to display a hand
def display_hand(hand):
    return [f"{card[0]} of {card[1]}" for card in hand]

# Example usage
playing_deck = DECK.copy()
initial_cards = initial_hand(playing_deck, 2)
new_deck = [card for card in playing_deck if card not in initial_cards]
next_card = initial_hand(new_deck, 1)

def calculate_value(cards):
    value = 0
    num_aces = 0

    for card, suit in cards:
        if card in ['Jack', 'Queen', 'King']:
            value += 10
        elif card == 'Ace':
            value += 11
            num_aces += 1
        else:
            value += int(card)
    
    # Adjust Aces if value exceeds 21
    while value > 21 and num_aces > 0:
        value -= 10
        num_aces -= 1
    
    return value

# Define a function to determine the outcome
def determine_outcome(score):
    if score == 21:
        return 'Blackjack'
    elif score > 21:
        return 'Bust'
    else:
        return 'Valid'

# Adding hand in a data frame for simulation
def add_hand(df, initial_cards, next_card):
    initial_score = calculate_value(initial_cards)
    current_hand = initial_cards + next_card
    final_score = calculate_value(current_hand)

    new_row = pd.DataFrame({
            'initial_score': [initial_score],
            'hit_score': [calculate_value(next_card)],
            'final_score': [final_score],
            'outcome': [determine_outcome(final_score)]
        })
    
    return pd.concat([df, new_row], ignore_index=True)


# Function to get user input
def get_user_guess():
    while True:
        try:
            guess = float(input("How often do you think you'll go bust if you hit with this hand? (Enter a percentage): "))
            if 0 <= guess <= 100:
                return guess
            else:
                print("Please enter a percentage between 0 and 100.")
        except ValueError:
            print("Please enter a valid number.")

def create_pretty_plot(df):
    # Set the style for the plot
    sns.set_style("whitegrid")
    sns.set_context("notebook", font_scale=1.2, rc={"lines.linewidth": 2.5})

    # Create the figure and axes
    fig, ax = plt.subplots(figsize=(12, 7))

    # Define a more visually appealing color palette
    color_map = {'Blackjack': '#2ecc71', 'Bust': '#e74c3c', 'Valid': '#3498db'}

    # Create the bar plot
    sns.barplot(x=df['outcome'].value_counts(normalize=True).index,
                y=df['outcome'].value_counts(normalize=True).values * 100,
                palette=color_map,
                hue=df['outcome'].value_counts(normalize=True).index,
                legend=False, 
                ax=ax)

    # Customize the plot
    ax.set_title('Distribution of Outcomes after 1000 simulations', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('Outcome', fontsize=14, fontweight='bold')
    ax.set_ylabel('Percentage', fontsize=14, fontweight='bold')

    # Add percentage labels on top of each bar
    for i, v in enumerate(df['outcome'].value_counts(normalize=True).values):
        ax.text(i, v * 100 + 1, f'{v:.1%}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Adjust y-axis to show percentages
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))

    # Add a subtle grid for better readability
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Remove top and right spines for a cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Adjust layout and display the plot
    plt.tight_layout()
    return fig

# Running the simulation

def simulate(guess,initial_cards,num_sims=100):
    df = pd.DataFrame(columns=['initial_score', 'hit_score','final_score', 'outcome'])
    new_deck = [card for card in playing_deck if card not in initial_cards]
    
    for i in range(num_sims):
        next_card = initial_hand(new_deck, 1)
        df = add_hand(df, initial_cards, next_card)
    
    bust_percentage = (df['outcome'] == 'Bust').mean() * 100
    st.write(f"Actual bust percentage: {bust_percentage:.2f}%")
    st.write(f"Your guess: {guess}%")

    # Plotting with Streamlit
    fig = create_pretty_plot(df)
    st.pyplot(fig)
    plt.close()
    return df

import streamlit as st

# Page config
st.set_page_config(page_title="Predict Bust", layout="wide")

def initialize_state():
    if 'game_active' not in st.session_state:
        st.session_state.game_active = False
    if 'initial_cards' not in st.session_state:
        st.session_state.initial_cards = []
    if 'initial_hand_value' not in st.session_state:
        st.session_state.initial_hand_value = 0
    if 'user_guess' not in st.session_state:
        st.session_state.user_guess = None
    if 'simulation_result' not in st.session_state:
        st.session_state.simulation_result = None

def start_new_game():
    # Generate initial cards and compute their value
    playing_deck = DECK.copy()
    st.session_state.initial_cards = initial_hand(playing_deck, 2)
    st.session_state.initial_hand_value = calculate_value(st.session_state.initial_cards)
    st.session_state.user_guess = None
    st.session_state.simulation_result = None 
    st.session_state.game_active = True

def run_simulation():
    if st.session_state.user_guess is not None:
        # Run the simulation using the existing simulate function
        df = simulate(
            guess=st.session_state.user_guess,
            initial_cards=st.session_state.initial_cards
        )
        
        # Display the DataFrame
        st.write("Simulation Results:")
        st.dataframe(df)
    else:
        st.warning("Please enter your guess before running the simulation.")

def main():
    st.title("Blackjack Trainer")
    st.subheader('Predict the bust probability')
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Blackjack Bust Probability Trainer**

        1. Click 'New Game' for a new hand.
        2. View your cards and hand value.
        3. Estimate the probability of busting if you hit.
           (Bust means hand-value > 21)
        4. Enter your estimated bust percentage.
        5. Click 'Run Simulation' to see results.
        6. Compare your guess with actual outcomes.
        7. Repeat to improve your intuition.
        """)
    
    with col2:
        st.markdown("""
        **Hand Value Calculation:**

        - Number cards (2-10): Face value
        - Face cards (Jack, Queen, King): 10 points each
        - Ace: 11 points, unless it would cause a bust, then 1 point
        - 'Soft hand': Contains an Ace counted as 11
        - 'Hard hand': No Ace, or Ace counted as 1
        """)

    initialize_state()

    if st.button('New Game'):
        start_new_game()

    if st.session_state.game_active:
        hand_str = display_hand(st.session_state.initial_cards)
        st.markdown(f"**Initial hand:** <span style='font-size:20px'>{hand_str}</span>", unsafe_allow_html=True)
    
        st.metric(label="Hand Value", value=st.session_state.initial_hand_value)

        st.session_state.user_guess = st.number_input(
            "Enter your guess for the bust percentage:",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.user_guess if st.session_state.user_guess is not None else 50.0,
            step=0.1
        )

        if st.button('Run Simulation'):
            run_simulation()

        if st.session_state.simulation_result is not None:
            st.write("Simulation Results:")
            st.dataframe(st.session_state.simulation_result)

if __name__ == "__main__":
    main()