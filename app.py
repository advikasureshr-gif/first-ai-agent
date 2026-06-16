import streamlit as st
import google.generativeai as genai
import json
import re

# 1. Page Configuration
st.set_page_config(
    page_title="Teal Cat Finder",
    page_icon="🐱",
    layout="wide"
)

# Initialize persistent session states
if "last_recommendations" not in st.session_state:
    st.session_state.last_recommendations = []

if "last_comparison" not in st.session_state:
    st.session_state.last_comparison = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# Design Layer Styling Customizations
st.markdown("""
<style>

html, body, [class*="css"], .stMarkdown {
    font-family: 'Courier New', monospace !important;
}

.stApp {
    background: linear-gradient(135deg, #006064, #008080, #00ACC1);
    color: white;
}

[data-testid="stSidebar"] {
    background: #1B5E20 !important;
}

[data-testid="stSidebar"] .stMarkdown p, 
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1 {
    color: white !important;
}

[data-testid="stChatMessageAssistant"],
[data-testid="stChatMessageUser"] {
    backdrop-filter: blur(18px);
    background: rgba(255, 255, 255, 0.12) !important;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 16px;
}

.stChatInput input {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

CAT_DB = """
Maine Coon|Long Fluffy|Medium|Low|Friendly giant
Siamese|Short Sleek|High|High|Very vocal and smart
Sphynx|Hairless|High|Medium|Attention seeker
Bengal|Short Sleek|High|Medium|Athletic and energetic
Persian|Long Fluffy|Low|Low|Quiet lap cat
Ragdoll|Long Fluffy|Low|Low|Extremely docile
British Shorthair|Short Sleek|Medium|Low|Independent and calm
Siberian|Long Fluffy|High|Low|Playful and hypoallergenic
"""

# Left-hand Filter Control Sidebar (Green)
with st.sidebar:
    st.title("🐱 Cat Finder")

    coat = st.radio(
        "Coat",
        ["No Preference", "Short Sleek", "Long Fluffy", "Hairless"],
        horizontal=True
    )

    energy = st.radio(
        "Energy",
        ["Low", "Medium", "High"],
        horizontal=True
    )

    vocal_ok = st.toggle("Vocal Cats OK", value=True)

    if st.button("🎯 Recommend For Me", use_container_width=True):
        st.session_state.auto_prompt = "Recommend the best cat breeds based on my sidebar filters."

    if st.button("🧹 Reset", use_container_width=True):
        st.session_state.messages = []
        st.session_state.favorites = []
        st.session_state.last_recommendations = []
        st.session_state.last_comparison = ""
        st.rerun()

    st.divider()

    # Cleaned up Favorites component relocated to the sidebar zone
    st.subheader("⭐ Favorites")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"🐾 {fav}")
            with col2:
                if st.button("❌", key=f"remove_{fav}"):
                    st.session_state.favorites.remove(fav)
                    st.rerun()
    else:
        st.caption("No favorites yet")

# Right-hand Main Chat App Workspace (Teal)
st.title("🐱 Teal Cat Finder AI")
st.caption("Find your perfect feline companion using a structural hybrid agent layout")

if not st.session_state.messages:
    st.info("Try: Best cat for allergies? • Compare Siberian vs Maine Coon • Quiet lap cat")

# Direct-click Shortcut Query Buttons
cols = st.columns(4)
suggestions = [
    "Best cat for allergies?",
    "Quiet lap cat",
    "Compare Siamese vs Bengal",
    "Most intelligent breed"
]

for c, s in zip(cols, suggestions):
    if c.button(s, use_container_width=True):
        st.session_state.auto_prompt = s

# Render historical communication log loops
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Collect fresh inputs
if "auto_prompt" in st.session_state:
    user_input = st.session_state.pop("auto_prompt")
else:
    user_input = st.chat_input("Ask about cats...")

# =========================================================
# Execution Layer: Process logic strings safely
# =========================================================
if user_input:
    # Append the user's message to the display list
    st.session_state.messages.append({"role": "user", "content": user_input})

    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    You are a Gen Z cat breed expert assistant.
    Respond in valid JSON matching the exact key types requested.
    Use a normal amount of emojis, don't go overboard.

    Database:
    {CAT_DB}

    Filters:
    Coat={coat}
    Energy={energy}
    Vocal OK={vocal_ok}

    Return JSON format:
    {{
      "recommended_breeds":[
        {{
          "name":"",
          "match_score":0,
          "reason":""
        }}
      ],
      "summary":"",
      "comparison":""
    }}
    """

    with st.chat_message("assistant"):
        with st.spinner("Analyzing metrics..."):
            try:
                response = model.generate_content(f"{prompt}\nUser: {user_input}")
                txt = response.text

                # Parse data structures out cleanly
                try:
                    data = json.loads(txt)
                except Exception:
                    match = re.search(r"\{.*\}", txt, re.S)
                    data = json.loads(match.group()) if match else None

                if data:
                    # FIX: Only overwrite last_recommendations when a fresh API
                    # response is successfully parsed — never reset them at the
                    # top of the input block, so st.rerun() from the Save button
                    # leaves the breed cards intact.
                    st.session_state.last_recommendations = data.get("recommended_breeds", [])
                    st.session_state.last_comparison = data.get("comparison", "")
                    full_text = data.get("summary", "Matches generated successfully!")
                else:
                    full_text = txt

            except Exception as e:
                full_text = f"Error capturing response logic: {e}"

        st.markdown(full_text)

    # Save output summary straight to chat history arrays
    st.session_state.messages.append({"role": "assistant", "content": full_text})
    st.rerun()

# =========================================================
# UI Rendering Layer: Stably mounted outside conditionals
# =========================================================
if st.session_state.last_recommendations:
    st.write("### 🎯 Best Matching Profiles")

    for breed in st.session_state.last_recommendations:
        score = breed.get("match_score", 0)
        breed_name = breed.get("name", "Unknown Breed")

        with st.container(border=True):
            st.subheader(f"🐾 {breed_name}")
            st.progress(min(score, 100) / 100)
            st.write(f"**Match Metric:** {score}%")
            st.write(breed.get("reason", ""))

            # FIX: Restore st.rerun() so the sidebar re-renders immediately
            # to show the newly added favorite. This is safe now because
            # last_recommendations is no longer wiped at the top of the
            # input block — it only changes when a new API response arrives.
            if st.button(f"⭐ Save {breed_name}", key=f"save_{breed_name}"):
                if breed_name not in st.session_state.favorites:
                    st.session_state.favorites.append(breed_name)
                    st.toast(f"Added {breed_name} to your favorites panel!")
                    st.rerun()

    if st.session_state.last_comparison:
        st.info(st.session_state.last_comparison)