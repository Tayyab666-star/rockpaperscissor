import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Rock, Paper, Scissors Arena",
    page_icon="🎮",
    layout="wide"
)

# --- Game Rules & Asset Map ---
CHOICES = {
    "Rock": {"icon": "🪨", "beats": "Scissors", "color": "#E74C3C"},
    "Paper": {"icon": "📄", "beats": "Rock", "color": "#3498DB"},
    "Scissors": {"icon": "✂️", "beats": "Paper", "color": "#F1C40F"}
}

# --- State Management ---
if "user_score" not in st.session_state:
    st.session_state.user_score = 0
if "bot_score" not in st.session_state:
    st.session_state.bot_score = 0
if "ties" not in st.session_state:
    st.session_state.ties = 0
if "rounds_played" not in st.session_state:
    st.session_state.rounds_played = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "streak" not in st.session_state:
    st.session_state.streak = 0


def resolve_winner(user_pick, bot_pick):
    if user_pick == bot_pick:
        return "Tie"
    elif CHOICES[user_pick]["beats"] == bot_pick:
        return "User"
    else:
        return "Bot"


def update_game_state(user_pick):
    bot_pick = random.choice(list(CHOICES.keys()))
    outcome = resolve_winner(user_pick, bot_pick)

    st.session_state.rounds_played += 1

    if outcome == "User":
        st.session_state.user_score += 1
        st.session_state.streak = st.session_state.streak + \
            1 if st.session_state.streak > 0 else 1
    elif outcome == "Bot":
        st.session_state.bot_score += 1
        st.session_state.streak = st.session_state.streak - \
            1 if st.session_state.streak < 0 else -1
    else:
        st.session_state.ties += 1
        st.session_state.streak = 0

    st.session_state.history.append({
        "Round": st.session_state.rounds_played,
        "Player": f"{CHOICES[user_pick]['icon']} {user_pick}",
        "Opponent": f"{CHOICES[bot_pick]['icon']} {bot_pick}",
        "Result": outcome
    })
    return bot_pick, outcome


# --- Layout: Header & Metrics ---
st.title("⚔️ Rock, Paper, Scissors: Dynamic Arena")
st.caption("A stateful Python implementation using Streamlit and Plotly")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Player Wins", st.session_state.user_score)
m2.metric("Bot Wins", st.session_state.bot_score)
m3.metric("Ties", st.session_state.ties)
m4.metric("Rounds", st.session_state.rounds_played)

streak_display = f"🔥 {st.session_state.streak}W" if st.session_state.streak > 0 else (
    f"❄️ {abs(st.session_state.streak)}L" if st.session_state.streak < 0 else "0"
)
m5.metric("Current Streak", streak_display)

st.divider()

# --- Layout: Main Arena ---
col_action, col_visual = st.columns([1, 1.2], gap="large")

with col_action:
    st.subheader("Choose Your Move")

    btn_cols = st.columns(3)
    user_selection = None

    for idx, (move, data) in enumerate(CHOICES.items()):
        with btn_cols[idx]:
            if st.button(f"{data['icon']}\n\n**{move}**", use_container_width=True, key=f"btn_{move}"):
                user_selection = move

    if user_selection:
        # Visual countdown effect
        with st.status("Simulating bot selection...", expanded=False) as status:
            time.sleep(0.3)
            status.update(label="Resolving outcome!", state="complete")

        bot_choice, result = update_game_state(user_selection)

        # Display match cards
        card_p, card_vs, card_b = st.columns([1, 0.4, 1])
        with card_p:
            st.markdown(
                f"<div style='text-align: center; border: 2px solid #3498DB; border-radius: 10px; padding: 15px;'>"
                f"<h4>You</h4><h1 style='font-size: 55px;'>{CHOICES[user_selection]['icon']}</h1>"
                f"<p><b>{user_selection}</b></p></div>",
                unsafe_allow_html=True
            )
        with card_vs:
            st.markdown(
                "<h2 style='text-align: center; padding-top: 35px;'>VS</h2>", unsafe_allow_html=True)
        with card_b:
            st.markdown(
                f"<div style='text-align: center; border: 2px solid #E74C3C; border-radius: 10px; padding: 15px;'>"
                f"<h4>Bot</h4><h1 style='font-size: 55px;'>{CHOICES[bot_choice]['icon']}</h1>"
                f"<p><b>{bot_choice}</b></p></div>",
                unsafe_allow_html=True
            )

        st.write("")
        if result == "User":
            st.success(f"**Victory!** {user_selection} beats {bot_choice}!")
            st.balloons()
        elif result == "Bot":
            st.error(f"**Defeat!** {bot_choice} beats {user_selection}!")
        else:
            st.warning("**Tie Game!** Both chose the same move.")

    st.write("")
    if st.button("Reset Game State", type="secondary"):
        st.session_state.user_score = 0
        st.session_state.bot_score = 0
        st.session_state.ties = 0
        st.session_state.rounds_played = 0
        st.session_state.history = []
        st.session_state.streak = 0
        st.rerun()

# --- Layout: Visualization & History ---
with col_visual:
    st.subheader("Performance Analytics")

    if st.session_state.rounds_played > 0:
        # Donut Chart for Win/Loss/Tie Distribution
        labels = ["Player Wins", "Bot Wins", "Ties"]
        values = [st.session_state.user_score,
                  st.session_state.bot_score, st.session_state.ties]
        colors = ["#2ECC71", "#E74C3C", "#95A5A6"]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker_colors=colors,
            textinfo="label+percent",
            hoverinfo="value+percent"
        )])
        fig.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=260
        )
        st.plotly_chart(fig, use_container_width=True)

        # Round Log Table
        st.caption("Match History (Recent rounds first)")
        df = pd.DataFrame(st.session_state.history[::-1])
        st.dataframe(df, use_container_width=True, hide_index=True, height=180)
    else:
        st.info("Make a move to generate real-time game statistics and telemetry.")
