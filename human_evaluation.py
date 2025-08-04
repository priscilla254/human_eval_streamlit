import os
import random
import pandas as pd
import streamlit as st
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Human_Evaluation_Results").sheet1

# === Config ===
image_dir = "human_eval_subset"
metadata_path = os.path.join(image_dir, "human_eval_subset_metadata.csv")
# results_csv = "evaluation_results.csv"
IMAGES_PER_USER = 30

# === Load metadata ===
df = pd.read_csv(metadata_path)

# === UI: Title and Login ===
st.title("🧠 Human Evaluation of Synthetic Faces")
st.markdown("""
This study aims to assess the **realism**, **age appropriateness**, and **ethnic consistency** of AI-generated human faces.  
Your input helps evaluate how well current generative models align with human expectations across different demographic groups.

Please rate **30 images**. Your responses will remain anonymous and are critical for improving fairness and accuracy in synthetic face generation. 
            Each question uses a 1 to 5 scale, where 1 means “not at all” or “very unlikely,” and 5 means “very accurate” or “looks good.” 
            Enter your name and press enter to start the evaluation.
""")

user_id = st.text_input("🔐 Enter your name:", max_chars=30)

# === Proceed once user ID is entered ===
if user_id:
    st.session_state.setdefault("user_id", user_id)

    if "user_images" not in st.session_state:
        all_filenames = df["filename"].tolist()
        random.shuffle(all_filenames)
        st.session_state.user_images = all_filenames[:IMAGES_PER_USER]
        st.session_state.current_index = 0

    if st.session_state.current_index >= IMAGES_PER_USER:
        st.success("✅ You’ve completed all 30 images. Thank you!")
        st.progress(100)
        st.stop()

    # === Get current image and metadata ===
    current_filename = st.session_state.user_images[st.session_state.current_index]
    row = df[df["filename"] == current_filename].iloc[0]
    image_path = os.path.join(image_dir, current_filename)

    # === Progress bar and counter ===
    progress = (st.session_state.current_index + 1) / IMAGES_PER_USER
    st.progress(progress)
    st.markdown(f"**Image {st.session_state.current_index + 1} of {IMAGES_PER_USER}**")

    # === Layout ===
    left_col, right_col = st.columns([1, 1.2])

    with left_col:
        if os.path.exists(image_path):
            st.image(image_path, width=300)
            st.markdown(f"**Ethnicity:** {row['ethnicity']}")
            st.markdown(f"**Age Group:** {row['age_group']}")
        else:
            st.error(f"❌ Image not found: {current_filename}")
            st.stop()

    with right_col:
        realism = st.slider("1️⃣ Realism", 1, 5, 3, help="Does this look like a real human?")
        age_match = st.slider("2️⃣ Age Appropriateness", 1, 5, 3, help="Does this match the labeled age group?")
        ethnicity_match = st.slider("3️⃣ Ethnic Consistency", 1, 5, 3, help="Does this match the labeled ethnicity?")

        submitted = st.button("✅ Submit Rating")

        if submitted:
            result = {
                "user_id": st.session_state.user_id,
                "filename": current_filename,
                "ethnicity": row["ethnicity"],
                "age_group": row["age_group"],
                "realism": realism,
                "age_appropriateness": age_match,
                "ethnic_consistency": ethnicity_match,
                "timestamp": datetime.now().isoformat()
            }

            sheet.append_row([
                result["user_id"],
                result["filename"],
                result["ethnicity"],
                result["age_group"],
                result["realism"],
                result["age_appropriateness"],
                result["ethnic_consistency"],
                result["timestamp"]
            ])

            st.session_state.current_index += 1
            st.rerun()
