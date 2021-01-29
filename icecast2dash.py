import streamlit as st
import requests

import json
from urllib.parse import urlparse, urljoin


# session_state: build DB of server info
state_db = st.beta_session_state(servers = {
                "KSTK": "https://kstk.rocks:8443",
                "Mutiny": "http://nthmost.net:8000",
                "(Add a New Server)": "na"} ,)


class IcecastSource:
    def __init__(self, item):
        self.__dict__ = item


def get_icecast2_stats(url):
    if not url.endswith("status-json.xsl"):
        url += "/status-json.xsl"

    response = requests.get(url)
    return response.json()


def get_total_listeners(sources):
    tot = 0
    for src in sources:
        tot += src.listeners
    return tot


st.sidebar.header("Menu")

servers_available = list(state_db.servers.keys())


menu_choice = st.sidebar.selectbox("Servers available:",
        servers_available )

if menu_choice == "(Add a New Server)":

    st.header("Add a new icecast2 server")

    with st.beta_form(submit_label="Submit", key="add_server_form"):
        server_name = st.text_input("Server Name")
        server_url = st.text_input("URL (with port)")

    if server_name and server_url:
        state_db.servers[server_name] = server_url
        st.write(f"Added {server_name} at {server_url} to menu")


else:
    st.title(menu_choice)
    url = state_db.servers[menu_choice]

    with st.spinner(f"Retrieving stats from {menu_choice}"):
        stats = get_icecast2_stats(url)
        # st.write(type(stats))
        # st.write(stats)

    #if stats["icestats"]["host"] == "nthmost.net":
    #    sources = [IcecastSource(item) for item in stats["icestats"]["source"].]

    sources = [IcecastSource(item) for item in stats["icestats"]["source"]]

    st.subheader("Server Stats")
    st.write("Total listeners connected: %i" % get_total_listeners(sources))

   
    for source in sources:
        mountpoint = urljoin(url, urlparse(source.listenurl).path)

        st.header(f"[🗣]({mountpoint})   {source.server_description}")
        st.write("Now playing: %s" % source.title)
        st.audio(mountpoint)
        st.write("Audio format: %s" % source.server_type)
        st.write("Sample rate: %i" % source.samplerate)
        st.write("Listeners: %i" % source.listeners)


