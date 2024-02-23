import configparser
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pathlib
from bs4 import BeautifulSoup
import logging
import shutil


def initialize_firebase():

    config = configparser.ConfigParser()
    config.read('config/config.ini')
    key = config.get('firebase', 'key')
    keypath = "config/"+key
    collection = config.get('firebase', 'collection')
    password = config.get('streamlit_analytics', 'password')

    if not firebase_admin._apps:
        cred = credentials.Certificate(keypath)
        firebase_admin.initialize_app(cred)

    return keypath, collection, password

def initialize_openai():

    config = configparser.ConfigParser()
    config.read('config/config.ini')
    key = config.get('openai', 'key')
    model = config.get('openai', 'model')
    return (key, model)

def expanders():

    config_file_path = "data/expanders.json"

    with open(config_file_path, "r") as file:
        config_data = json.load(file)

    is_first_expander = True
    for key in config_data.keys():
        q,a = config_data[key]["question"], config_data[key]["answer"]
        with st.sidebar.expander(q, expanded = is_first_expander):
            st.markdown(a)
            is_first_expander = False

def check_site_availability():

    try:
        config = configparser.ConfigParser()
        config.read('config/config.ini')
        config_collection = config.get('firebase', 'config_collection')
        db = firestore.client()
        isWebsiteUp = db.collection(config_collection).document("isWebsiteUp").get().to_dict()["isWebsiteUp"]
        statusMessage = None
        if not isWebsiteUp:
            statusMessage = db.collection(config_collection).document("statusMessage").get().to_dict()["statusMessage"]
        return (isWebsiteUp, statusMessage, None)

    except Exception as e:
        return (False, None, e)

def inject_google_analytics():

    GA_ID = "google_analytics"
    GA_JS = """
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=AW-11392666853">
        </script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'AW-11392666853');
        </script>

        <!-- Event snippet for Page view conversion page -->
        <script>
        gtag('event', 'conversion', {'send_to': 'AW-11392666853/U9LaCNH7uPEYEOWZubgq'});
        </script>
    """

    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID):  # if cannot find tag
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # recover from backup
        else:
            shutil.copy(index_path, bck_index)  # keep a backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)
