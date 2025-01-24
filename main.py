import streamlit as st
import random
import string
import pymongo
from uuid import uuid4
from datetime import datetime


st.set_page_config(
    page_title="CollabHub",
    page_icon=":arrow_right:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
    </style>       
    """, unsafe_allow_html=True)



with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


@st.cache_resource
def MongoOperations():
    class Mongo:
        def __init__(self):
            self.client = pymongo.MongoClient(st.secrets['MONGO_URI'])
            self.db = self.client[st.secrets['MONGO_DB']]

        def get_textpads(self, room):
            items = list(self.db.text_pads.find({"room": room}, {"_id": 0}, sort=[("last_modified_at", -1)]))
            st.session_state.textPads = items

        def check_room_existance(self, room):
            temp = self.db.text_pads.find_one({"room": room})
            return True if temp else False

        def add_textpad(self, data):
            self.db.text_pads.insert_one(data)
        
        def delete_textpad(self, room, unique_id):
            self.db.text_pads.delete_one({"room": room, "unique_id": unique_id})
        
        def update_textpad(self, room, unique_id, data):
            self.db.text_pads.update_one({"room": room, "unique_id": unique_id}, {"$set": data})


    obj = Mongo()
    return obj

mongo = MongoOperations()


@st.cache_data
def get_textpads(room):
    print("<get_textpads> Fetching data from DB")
    mongo.get_textpads(room)

def addTextPad():
    temp_data = {
        "room": st.query_params.get("room_code"),
        "content": "",
        "editable": False,
        "unique_id": str(uuid4()).split("-")[-1],
        "last_modified_at": datetime.now()
    }
    mongo.add_textpad(temp_data)
    temp_data["editable"] = True
    st.session_state.textPads.append(temp_data)

def toggle_edit_mode(index, save=False):
    if save:
        mongo.update_textpad(st.query_params.get("room_code"), st.session_state.textPads[index]["unique_id"], {"content": st.session_state.textPads[index]["content"]})
    st.session_state.textPads[index]["editable"] = not st.session_state.textPads[index]["editable"]

def deleteTextpadFunction(index):
    mongo.delete_textpad(st.query_params.get("room_code"), st.session_state.textPads[index]["unique_id"])
    st.session_state.textPads.pop(index)





if "currentPage" not in st.session_state:
    st.session_state.currentPage = "Home"

if 'textPads' not in st.session_state: 
    st.session_state.textPads = []

if "joinStatus" not in st.session_state:
    st.session_state.joinStatus = False

with st.sidebar:
    with st.container(key="profile", border=True):
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center;">
            <h1>🤵</h1>
        </div>
        <h3 style="text-align: center;">Hello!</h3>
        """, unsafe_allow_html=True)

    with st.container(key="menu", border=False):
        if st.query_params.get("room_code"):
            # Calendar = st.button("Calendar", key="calendar", on_click=lambda: st.session_state.update({"currentPage": "Calendar"}))
            TextShare = st.button("Text Share", key="text-share", on_click=lambda: st.session_state.update({"currentPage": "Text-Share"}))
        


if st.session_state.currentPage == "Home":
    st.markdown("""
        <h1 style='text-align: center; color: black; margin-bottom: 5%; padding: 0;'>
            Collab
            <span style='color: #4A55A2; font-size: 1.3em'>
                Hub
            </span>
            <hr style='padding:0; margin:0; width: 50%; left:25%; position:absolute; border: none; border-top: 2px solid black;'>
        </h1>""", unsafe_allow_html=True)

    st.markdown("""
        <h3 style='text-align: center; color: black; margin-bottom: 5%;'>
            Collaborate with Purpose, Share with Ease
        </h3>""", unsafe_allow_html=True)
    
    if st.query_params.get("room_code"):
        st.markdown(f"""
        <h5 style='text-align: center; color: black; margin-top: 5%;'>
            You are now connected to room<br>{st.query_params.get("room_code")}
        </h5>
        """, unsafe_allow_html=True)



    else:
        CreateRoom = st.button("Create Room", key="createRoom")
        if CreateRoom: 
            st.query_params["room_code"] = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
            st.rerun()
        
        st.markdown("""
                <h1 style='text-align: center; color: Black; margin: 0%;'>
                    OR
                </h1>""", unsafe_allow_html=True)
        
        st.markdown("""
                <h5 style='text-align: center; color: Black; margin-top: 1%;'>
                    Enter The Code To Join Room
                </h5>""", unsafe_allow_html=True)
        
        _, subcol, _ = st.columns([1, 2, 1])
        with subcol:
            JoinRoom = st.text_input("Enter Code", placeholder="Enter Code", max_chars=6, label_visibility="collapsed")
        JoinButton = st.button("Join the Room", key="join-room")

        if JoinButton:
            if mongo.check_room_existance(JoinRoom):
                st.query_params["room_code"] = JoinRoom
                st.rerun()
            else:
                st.error("Room Not Found")

       
elif st.session_state.currentPage == "Text-Share":
    with st.container(key="text-share-container", border=False):
        if not st.session_state.textPads:
            get_textpads.clear()
            get_textpads(st.query_params.get("room_code"))

        with st.container(key=f"tab-heading"):
            st.markdown("""
                <p style='text-align: center; color: black; font-size: 2em; font-weight: bolder;'>
                    Text Pads
                </p>""", unsafe_allow_html=True)
            st.button("➕", on_click=addTextPad)


        for i, section in enumerate(st.session_state.textPads):
            with st.container(key=f"container-textpad-{i}", border=True):
                st.button("✖️", on_click=lambda idx=i: deleteTextpadFunction(idx), key=f"delete-textpad-{i}")
                if section["editable"]:
                    new_content = st.text_area(f"Edit TextPad {i + 1}", section["content"], key=f"textpad-{i}", height=200)
                    st.session_state.textPads[i]["content"] = new_content
                    st.button("💾", on_click=lambda idx=i: toggle_edit_mode(idx, save=True), key=f"edit-textpad-{i}")
                else:
                    st.markdown(section["content"])
                    st.button("✏️", on_click=lambda idx=i: toggle_edit_mode(idx), key=f"edit-textpad-{i}")
