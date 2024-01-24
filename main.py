import streamlit as st
from PIL import Image
from pathlib import Path
import zipfile
import os
from bs4 import BeautifulSoup
import pandas as pd
import shutil


F_AND_F_FOLDER = "connections/followers_and_following"
FOLLOWERS_FILE = "followers_1.html"
FOLLOWINGS_FILE = "following.html"
extracted_folder = "extract"

ig1_path = Path(__file__).parents[0] / "img/ig_1.png"
ig2_path = Path(__file__).parents[0] / "img/ig_2.png"
ig3_path = Path(__file__).parents[0] / "img/ig_3.png"
ig4_path = Path(__file__).parents[0] / "img/ig_4.png"
image_urls = [ig1_path, ig2_path, ig3_path, ig4_path]


def display_images(image_urls):
    st.subheader("Images:")
    col1, col2, col3, col4 = st.columns(4)

    for i, url in enumerate(image_urls):
        image = Image.open(url)
        with locals()[f"col{i + 1}"]:
            st.image(image, use_column_width=True)


def extract_followers_and_following(zip_file_path, extracted_folder):
    os.makedirs(extracted_folder, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extracted_folder)

    followers_path = os.path.join(extracted_folder, F_AND_F_FOLDER, FOLLOWERS_FILE)
    followings_path = os.path.join(extracted_folder, F_AND_F_FOLDER, FOLLOWINGS_FILE)

    if os.path.exists(followers_path) and os.path.exists(followings_path):
        with open(followers_path, "r", encoding="utf-8") as html_file:
            followers_html = html_file.read()
        with open(followings_path, "r", encoding="utf-8") as html_file:
            followings_html = html_file.read()
    else:
        print(f"Files not found in the specified structure.")
        return None, None

    followers = BeautifulSoup(followers_html, "html.parser")
    following = BeautifulSoup(followings_html, "html.parser")

    total_following = {u.text: u["href"] for u in following.find_all("a")}
    total_followers = {u.text: u["href"] for u in followers.find_all("a")}

    return total_following, total_followers


def find_unmatched_followers(total_following, total_followers):
    unmatched_users = {
        u: total_following[u] for u in total_following if u not in total_followers
    }
    unmatched_df = pd.DataFrame(
        list(unmatched_users.items()), columns=["Username", "Instagram"]
    )
    return unmatched_df


st.set_page_config(page_title="FollowBack", layout="wide", page_icon=":bar_chart:")

## Web App Format ##

st.markdown(
    "<h1 style='text-align: center; color: white;'>Instagram Follow Back</h1>",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

"""
[![Star](https://img.shields.io/github/stars/lautaropacella/datathon2023.svg?logo=github&style=social)](https://github.com/lautaropacella/datathon2023)
"""

# st.image(logo, width=500)

st.markdown("<br>", unsafe_allow_html=True)

"""
### **Check which of your followers is not following you back**
"""

instagram_zip = st.file_uploader(
    "Drop Zip File", type="zip", label_visibility="visible"
)

if instagram_zip is not None:
    total_following, total_followers = extract_followers_and_following(
        instagram_zip, extracted_folder
    )

    if total_following is not None and total_followers is not None:
        not_following = find_unmatched_followers(total_following, total_followers)
    st.dataframe(not_following, use_container_width=True)
    shutil.rmtree(extracted_folder)

display_images(image_urls)
