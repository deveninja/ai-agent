import streamlit as st
from agent import ask_agent

st.title("🧟 Hi I'm Tata Lino")
st.subheader("Your not so smart AI Agent")

if "messages" not in st.session_state:
  st.session_state.messages = []

def render_card(title, content):
  return f"""
  <div style="
    padding:16px;
    border-radius:12px;
    color:var(--text-color);
    border:1px solid var(--border-color);
    background-color:#555555;
    margin:10px 0;
  ">
    {content}
  </div>
  """

# Render chat history
for role, msg in st.session_state.messages:
  with st.chat_message(role):

    if isinstance(msg, dict) and "time" in msg:

      html = f"""
      <div style="
        padding:15px;
        border-radius:10px;
        background-color:var(--secondary-background-color);
        color:var(--text-color);
        font-size:18px;
      ">
        🕒 <b>Current Time</b><br>
        {msg['time']}<br>
        <small>{msg['timezone']}</small>
      </div>
      """

      st.html(render_card("Current Time", html))

    elif isinstance(msg, list):

      html = "<div style='padding:10px; color:var(--text-color)'>"
      html += "<small>Showing 5-day forecast</small><br>"

      for day in msg:
        html += f"""
        <div style="
          padding:15px;
          border-radius:10px;
          background-color:var(--secondary-background-color);
          color:var(--text-color);
          font-size:18px;
        ">
          📅 {day['date']}<br>
          🌡 {day['temp_min']}°C - {day['temp_max']}°C<br>
          🌧 Rain chance: {day['rain_chance']}%
        </div>
        """

      html += "</div>"

      st.html(render_card("Weather Forecast", html))

    elif isinstance(msg, dict) and "email" in msg:
      if msg["name"]:
        html = f"""
        <div style="
          padding:15px;
          border-radius:10px;
          background-color:var(--secondary-background-color);
          color:var(--text-color);
          font-size:18px;
        ">
          👤 <b>{msg['name']}</b><br>
          📧 {msg['email']}<br>
          🏢 {msg['department']}
        </div>
        """
        st.html(render_card("User Information", html))
      else:
        st.write("User not found.")

    else:
        st.write(msg)

# Persistent typing indicator (above input)
typing_indicator = st.empty()

question = st.chat_input("Ask something")

if question:

  # show typing indicator
  typing_indicator.markdown("💭 **AI is thinking...**")

  # run agent
  response = ask_agent(question)

  # clear typing indicator
  typing_indicator.empty()

  # store conversation
  st.session_state.messages.append(("user", question))
  st.session_state.messages.append(("assistant", response))

  # refresh UI once
  st.rerun()