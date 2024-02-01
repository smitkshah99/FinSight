import base64

import streamlit as st
import requests
from bs4 import BeautifulSoup
import main as m
from PIL import Image
import gdown
from streamlit_card import card
import time


def set_page_configuration():
    st.set_page_config(
        page_title="FinSight",
        page_icon="🚀",
        layout="wide",
    )


@st.cache_resource
def configure_sidebar():
    st.session_state['side'] = True
    st.sidebar.title("🚀 FinSight")
    st.sidebar.write("Your Financial News Companion!")

    # Project information in the sidebar
    st.sidebar.header("Project Info")
    st.sidebar.write("Get mode details: [Architecture](https://drive.google.com/file/d/1eRKTzuX0-xnYV3OH-ZU9BhE3mWhhh7-4/view?usp=sharing)")
    st.sidebar.markdown("🔍 **Project Name:** FinSight")
    st.sidebar.markdown("📰 **Description:** Analyze financial news headlines")
    st.sidebar.markdown("✨ **Features:**")
    st.sidebar.markdown("- Real-time financial news analysis")
    st.sidebar.markdown("- Interactive user interface")

    st.sidebar.markdown("🤯 **System Design**")
    file_id = '1yGYmDWjzQlgf6SZr5UIspid1Lxpknn91'

    # Download the image using gdown
    url = f'https://drive.google.com/uc?id={file_id}'
    output_path = 'downloaded_image.jpg'
    if "arcimage" not in st.session_state:
        gdown.download(url, output_path, quiet=False)
        st.session_state.arcimage = Image.open(output_path)

    st.sidebar.image(st.session_state.arcimage, use_column_width=True, output_format="auto")

    # Create two columns for logos
    columns = st.sidebar.columns(12)

    # LinkedIn logo
    columns[0].markdown(
        '<a href="https://www.linkedin.com/in/smitkshah/" target="_blank">'
        '<img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width="20"></a>',
        unsafe_allow_html=True
    )

    # Gmail logo
    columns[1].markdown(
        '<a href="mailto:smitkshah99@gmail.com" target="_blank">'
        '<img src="https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg" width="20"></a>',
        unsafe_allow_html=True
    )

@st.cache_resource
def fetch_financial_news():
    print("------------------------------------------"+str(time.time()))
    url = "https://finance.yahoo.com/rss/topfinstories"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        news_items = [
            # (truncate_text(item.title.text, 70),
            (item.title.text,
             item.link.text,
             item.description.text if item.description else '')
            for item in soup.find_all('item')
        ]
        return news_items
    else:
        return []


def truncate_text(text, max_length):
    return text[:max_length] + '...' if len(text) > max_length else text


def display_expander(headline, link, description):
    st.write(f"**{headline}**")
    st.write(f"Link: [{link}]({link})")
    st.write(f"Description: {description}")
    st.write("------")


def display_pagination_buttons(current_page, total_pages):
    col_prev, col_temp, col_temp2, col_next = st.columns(4)

    if current_page > 1:
        if col_prev.button("Previous"):
            current_page -= 1
            st.session_state["current_page"] = current_page

    if current_page < total_pages:
        if col_next.button("Next"):
            current_page += 1
            st.session_state["current_page"] = current_page
            st.empty()  # Clear the previous page number


def show_news(start_index, end_index, headlines, links, descriptions):
    for i in range(start_index, end_index):
        col1, col2 = st.columns(2)

        # Show each news item in a card format
        with col1:
            st.write("### News")
            display_expander(headlines[i], links[i], descriptions[i])

        # You can add more columns for additional information if needed
        with col2:
            st.write("### Additional Info")
            st.write("Add additional information here...")


def display_cards(start_index, news_items, container):
    col1, col2, col3, col4 = container.columns(4)
    for i, col in enumerate([col1, col2, col3, col4]):
        with col:
            col.hasClicked = card(
                title="",
                text=f"{news_items[start_index + i][0]}",
                url=news_items[start_index + i][1],
                key=str(start_index + i + 1),
                styles={
                    "card": {
                        "width": "150px",
                        "height": "150px",
                        "margin": "0",
                        "padding": "0",
                        "background-color": "skyblue",
                    },
                    "text": {
                        "font-family": "serif",
                        "font-size": "14px",
                        "color":"white"
                    }

                },
            )


def main():
    # if 'side' not in st.session_state:
    #     st.session_state.side = False
    set_page_configuration()
    configure_sidebar()

    # Fetch financial news headlines
    print("--------------------------")
    news_items = fetch_financial_news()

    # Main page content
    st.title("Financial News Analysis 🏦")

    # Pagination
    page_number = st.empty()  # Placeholder to dynamically update page number
    current_page = st.session_state.get("current_page", 1)
    total_pages = len(news_items) // 4
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    current_index = 0
    # display_cards(current_index, news_items)
    temp = st.container()
    button_col = st.columns(6)
    if button_col[3].button("Next", disabled=(st.session_state.current_index >= (total_pages-2)*4)) :
        st.session_state.current_index = min((total_pages-2)*4, st.session_state.current_index + 4)
        st.session_state.current_index += 4

    if button_col[2].button("Previous", disabled=st.session_state.current_index == 0):
        st.session_state.current_index = max(0, st.session_state.current_index - 4)
    print("Cur_index", st.session_state.current_index)
    display_cards(st.session_state.current_index, news_items, temp)

    m.main1()


if __name__ == "__main__":
    main()
