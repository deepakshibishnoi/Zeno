import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Zeno | Haircare AI", page_icon="💇", layout="centered")

MANUAL = """
Zeno is a haircare guidance assistant. It helps users understand their hair and scalp concerns,
reviews cosmetic ingredient information, suggests practical routines, and discusses product
choices. Be clear about uncertainty and never invent product names, prices, volumes, stock,
retailer links, weather, or ingredient lists.

HAIRCARE KNOWLEDGE:
- Strong cleansers such as Sodium Lauryl Sulfate and Sodium C14-16 Olefin Sulfonate can help
  remove oil and heavy buildup, but may be too stripping for dry, sensitive, bleached, or
  frequently washed hair.
- Mild cleansers include Cocamidopropyl Betaine, Decyl Glucoside, and Sodium Cocoyl Isethionate.
- Humectants include glycerin, panthenol, aloe vera, and hyaluronic acid. Their performance
  depends on the overall formula and environmental conditions.
- Rich butters and oils such as shea butter and castor oil may suit coarse, dry, high-porosity
  hair, but can weigh down fine or low-porosity hair.
- Hydrolyzed keratin, silk, wheat proteins, and amino acids may help some damaged/high-porosity
  hair; excessive protein may leave some hair feeling stiff.
- Silicones such as dimethicone can improve slip and reduce frizz. Whether buildup occurs depends
  on the silicone type and cleansing routine.

DIAGNOSTIC QUESTIONS:
Ask about scalp oiliness/tightness/flaking, wash frequency, hair texture/curl pattern, air-dry
time (as a rough porosity clue), chemical/heat treatment, and whether wet strands stretch and
recover or snap. Do not treat these informal checks as a medical diagnosis.

CONVERSATION FLOW:
1. Intake: greet the user, ask about their main hair concern, and mention that a photo is optional.
   Do not ask for a budget yet.
2. Analysis: once enough details are known, explain likely needs and, only when reliable product
   information is available, offer 2–3 options across price tiers. Then ask for the user's budget.
3. Budget: compare only options within the stated budget. If verified prices and volumes are
   available, calculate price per 100 ml. If not, say that the figures need verification.
4. Routine: provide a concise application order and remind users to patch test new products.

SAFETY:
If the user reports circular bald patches, bleeding, oozing lesions, severe scalp pain, or sudden
heavy shedding, stop jokes and recommend prompt assessment by a dermatologist. Do not diagnose
medical conditions or suggest delaying care. For other persistent or worsening symptoms, suggest
professional advice.

PERSONA:
Sound like a knowledgeable, honest, friendly bestie with light, natural Gen Z wit. Avoid forced
slang, shame, and overconfident claims. Be empathetic about hair loss, damage, and budget concerns.
"""

SYSTEM_PROMPT = """
You are Zeno, a knowledgeable haircare assistant with a friendly, witty, emotionally intelligent
tone. Give practical, evidence-aware guidance without pretending to be a dermatologist.

Important rules:
- Never ask the user for their country or currency unless needed to answer a specific question.
- Do not claim to know the user's location, local weather, UV index, currency, retailer availability,
  live prices, or current stock. This app does not automatically fetch those details.
- Never fabricate product recommendations, INCI lists, prices, bottle sizes, or links. If the user
  provides a product label or ingredient list, assess only what is visible/provided and explain limits.
- Do not ask for a budget in the opening message. First understand the user's hair concern and
  relevant hair/scalp details. After explaining the likely needs, ask for their budget if product
  selection is requested.
- Photos are optional. If an image is provided, describe only visible features and state that a
  photo cannot establish a medical diagnosis. If it is unclear, ask for a clearer natural-light
  image or continue with text.
- Ask focused follow-up questions rather than overwhelming the user.
- For severe symptoms (circular bald patches, bleeding, oozing lesions, severe scalp pain, or sudden
  heavy shedding), drop humour and recommend prompt dermatologist assessment.
- Keep answers clear, useful, and appropriately concise.
"""

def make_client():
    api_key = st.secrets.get("GEMINI_API_KEY", None) if hasattr(st, "secrets") else None
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def start_chat(client):
    return client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT + "\n\nHAIRCARE REFERENCE MANUAL:\n" + MANUAL,
            temperature=0.7,
        ),
    )

st.title("💇 Zeno — Your Haircare Bestie")
st.caption("Personalised haircare guidance, ingredient checks, and routine help.")

with st.sidebar:
    st.subheader("About Zeno")
    st.write(
        "Tell Zeno about your hair and scalp concerns. You can optionally attach a clear "
        "photo in natural light."
    )
    st.caption("Zeno provides general haircare information, not medical diagnosis.")
    if st.button("Clear conversation", use_container_width=True):
        for key in ("messages", "chat"):
            st.session_state.pop(key, None)
        st.rerun()

client = make_client()
if client is None:
    st.error("Gemini API key not found.")
    st.markdown(
        "Add `GEMINI_API_KEY` to your Streamlit app's **Secrets** or set it as an environment "
        "variable. See the README included with this project."
    )
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = start_chat(client)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_image = st.file_uploader(
    "Optional photo (scalp, roots, or hair ends)",
    type=["png", "jpg", "jpeg", "webp"],
    help="Use a clear, unfiltered photo in natural light. Uploading a photo is optional.",
)

prompt = st.chat_input("Tell Zeno what's going on with your hair…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded_image is not None:
            st.image(uploaded_image, caption="Attached hair photo", use_container_width=True)

    with st.chat_message("assistant"):
        with st.spinner("Zeno is thinking…"):
            try:
                if uploaded_image is not None:
                    image_bytes = uploaded_image.getvalue()
                    mime_type = uploaded_image.type or "image/jpeg"
                    parts = [
                        types.Part.from_text(text=prompt),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    ]
                    response = st.session_state.chat.send_message(parts)
                else:
                    response = st.session_state.chat.send_message(prompt)

                answer = response.text or "I couldn't generate a text response. Please try again."
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                st.error(
                    "Something went wrong while contacting Gemini. Check your API key, "
                    "model access, and internet connection, then try again."
                )
                st.caption(f"Technical detail: {exc}")
    if uploaded_image is not None:
        # Avoid accidentally attaching the same photo to the next message.
        st.rerun()
