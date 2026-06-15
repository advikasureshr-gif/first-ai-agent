import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="Teal Feline Agent", page_icon="🐱", layout="wide")

# =========================================================
# 2. DESIGN LAYER: Custom CSS Injection for Themes
# =========================================================
st.markdown("""
    <style>
    /* 1. Import the custom font from Google Fonts (Identical twin to Google Sans) */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

    /* 2. Apply the font globally across all Streamlit components */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', 'Google Sans', sans-serif !important;
    }

    /* A. The Main Content Area - Dynamic Teal Gradient */
    .stApp {
        background-image: linear-gradient(135deg, #006064 0%, #008080 50%, #00ACC1 100%);
        color: white; /* Global text color to white for contrast */
    }

    /* B. The Sidebar - Solid Forest Green */
    [data-testid="stSidebar"] {
        background-color: #1B5E20 !important; /* A deep dark green */
        border-right: 2px solid #fff3; /* Subtle divider */
    }

    /* C. Fix Sidebar Text Readability (Make everything white) */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* D. Make the chat input text visible (so it doesn't default to white on white) */
    .stChatInput input {
        color: black !important;
    }

    /* E. Styling the Chat Messages (Semi-transparent for blending) */
    /* User Message - Blueish translucent */
    [data-testid="stChatMessageUser"] {
        background-color: rgba(0, 150, 136, 0.4) !important;
        border-radius: 15px 15px 0px 15px;
        padding: 1rem;
    }
    
    /* Assistant Message - White translucent */
    [data-testid="stChatMessageAssistant"] {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-radius: 15px 15px 15px 0px;
        padding: 1rem;
    }

    /* G. Headers styling */
    h1, h2, h3 {
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 3. AI Setup
# =========================================================
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# =========================================================
# 4. Sidebar Controls (Green Zone)
# =========================================================
with st.sidebar:
    st.title("⚙️ Cat Filter Controls")
    st.write("Tune these controls to pre-filter your search!")
    
    coat_preference = st.selectbox(
        "Preferred Coat Type:",
        ["No Preference", "Short Sleek", "Long Fluffy", "Hairless"]
    )
    
    energy_level = st.select_slider(
        "Desired Energy Level:",
        options=["Low", "Medium", "High"],
        value="Medium"
    )
    
    vocal_ok = st.checkbox("Vocal is OK 🗣️", value=True)
    
    st.divider()
    
    # Crucial UX Feature: Reset Button
    if st.button("🧹 Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# =========================================================
# 5. Main Content Area (Teal Zone)
# =========================================================
st.title("Feline Agent Muehehehehehe")
st.write("Wantcha know bout a CAT? Search no further, people!")

# Main Knowledge Base
cat_knowledge_base = """
- **Maine Coon**: Very large, long shaggy coat. Friendly, playful, "gentle giant", highly affectionate. Medium-high energy. Quiet.
- **Siamese**: Medium, short sleek coat, blue eyes. Incredibly vocal, chatty, deeply affectionate, highly intelligent. High energy.
- **Sphynx**: Medium, completely hairless. High energy, massive attention-seeker, acts like a dog, needs regular baths.
- **Bengal**: Medium-large, short spotted coat (leopard look). Highly energetic, athletic, highly intelligent, loves climbing.
- **Persian**: Medium-large, extremely long fluffy coat. Quiet, docile, sweet-tempered, low energy.
- **Ragdoll**: Large, long silky coat, blue eyes. Extremely docile, calm, patient, loves being a lap cat. Low-medium energy.
- **British Shorthair**: Medium-large, dense plush short coat. Independent, calm, easygoing, quiet. Medium energy.
- **Siberian**: Medium to large size, incredibly dense water-resistant triple coat, bushy tail. Extremely playful, loyal, "dog-like" personality, loves following humans around. Highly energetic, exceptional jumpers, loves playing with water. Hypoallergenic bonus (produces less Fel d 1 protein, great for mild allergy sufferers). Relatively quiet, communicates via soft chirps.
"""

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History Container
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# =========================================================
# 6. Handling the Hybrid Logic
# =========================================================
if user_input := st.chat_input("Ask a question about cats..."):
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # SYSTEM PROMPT (Injecting UI Context)
    system_prompt = f"""
    You are a friendly, Gen-Z expert hybrid Cat Agent that combines user UI settings with text prompts.
    Respond in markdown with concise, formatted, bulleted text. Don't use excess of emojis!
    
    Here is the official cat database:
    {cat_knowledge_base}
    
    CURRENT UI FILTER SETTINGS (Sidebar):
    - Preferred Coat: {coat_preference}
    - Energy Level Preference: {energy_level}
    - Vocal OK?: {"Yes" if vocal_ok else "No"}
    
    Instructions:
    Look at both the UI filter settings AND the user's text input.
    Provide matching breeds or breed information based on all context. 
    Do not mention filter settings again in the answer.
    """
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing metrics..."):
                response = model.generate_content(f"{system_prompt}\n\nUser Message: {user_input}")
                st.markdown(response.text)
                
    st.session_state.messages.append({"role": "assistant", "content": response.text})