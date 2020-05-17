import streamlit as st
import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
from geopy.geocoders import Nominatim
import geocoder
from geopy.distance import geodesic
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import googlemaps
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import time
import sqlite3
from sqlite3 import Error
import os
import sqlite3, datetime
import streamlit.server.SessionState as SessionState

#from streamlit.server.session_states import get_state
# class MyState:
#     a: int
#     b: str
#
#     def __init__(self, a: int, b: str):
#         self.a = a
#         self.b = b
#
#
# def setup(a: int, b: str) -> MyState:
#     print('Running setup')
#     return MyState(a, b)
#
#
# state = get_state(setup, a=3, b='bbb')
#
#
# st.title('Test state')
# if st.button('Increment'):
#     state.a = state.a + 1
#     print(f'Incremented to {state.a}')
# st.text(state.a)


sessionId = None
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

local_css("style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

@st.cache(allow_output_mutation=True)
def getCovid19Cases():
    # URL = "https://coronavirus-ph-api.herokuapp.com/cases"
    # headers = {'content-type': 'application/json'}
    # response = requests.get(URL, headers=headers)
    # covid_19_json = response.json()
    # #get data values from json
    # covid_19_json_data = covid_19_json['data']
    # #convert json data to dataframe
    # df_covid_19_cases = pd.DataFrame.from_dict(covid_19_json_data, orient='columns')
    # return df_covid_19_cases
    with open('covid_19_ph.json') as json_file:
        covid_19_json = json.load(json_file)
        #get data values from json
        covid_19_json_data = covid_19_json['data']
        #convert json data to dataframe
        df_covid_19_cases = pd.DataFrame.from_dict(covid_19_json_data, orient='columns')
        return df_covid_19_cases

@st.cache(allow_output_mutation=True)
def getCovid19CasesLatest():
    URL = "https://coronavirus-ph-api.herokuapp.com/doh-data-drop"
    headers = {'content-type': 'application/json'}
    response = requests.get(URL, headers=headers)
    covid_19_json = response.json()
    #get data values from json
    covid_19_json_data = covid_19_json['data']
    #convert json data to dataframe
    df_covid_19_cases = pd.DataFrame.from_dict(covid_19_json_data, orient='columns')
    return df_covid_19_cases

def getLocation():
    # gmaps = googlemaps.Client(key = 'AIzaSyDCkp6UuUj9KnshHK-12gy_A8WQPnL1cHo')
    # geocode_result = gmaps.geolocate()
    #url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyDCkp6UuUj9KnshHK-12gy_A8WQPnL1cHo'
    url = 'https://www.googleapis.com/geolocation/v1/geolocate'
    myobj = {'key': 'AIzaSyDCkp6UuUj9KnshHK-12gy_A8WQPnL1cHo'}

    geocode_result = requests.post(url, data=myobj)

    #st.write(geocode_result.text)
    return geocode_result.json()

def get_client_address():
    try:
        #return os.environ.get('X-Forwarded-For').split(',')[-1].strip()
        return os.environ.get('X-Forwarded-For')
    except KeyError:
        return os.environ.get('REMOTE_ADDR')
        #return os.getenv('REMOTE_ADDR')

# iid = 1
# def next_id():
#     global iid
#     res = iid
#     iid += 1
#     return iid

def getCoordinatesFromDB(sessionId):
    try:
        #sessionId = sessionId + 1
        sessionIdString = str(sessionId)
        db = sqlite3.connect('user_coordinates.db')
        conn = db.cursor()
        db.commit()

        # search for sessionID
        conn.execute("SELECT * FROM user_coordinates where sessionIdString='" + str(sessionIdString) + "'")
        result = conn.fetchone()
        return result
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def getDBCountForSession():
    try:
        db = sqlite3.connect('user_coordinates.db')
        conn = db.cursor()
        db.commit()

        # search for sessionID
        conn.execute("SELECT COUNT(*) FROM user_coordinates")
        count = conn.fetchone()
        return count

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

st.cache(allow_output_mutation=False)
def getSessionId():
    global sessionId

    if sessionId is None:
        sessionId = getDBCountForSession()[0]
        return sessionId
    else:
        return sessionId

# if not hasattr(st, 'global_con'):
#     st.global_con = getDBCountForSession()[0]
#
# sessionId = st.global_con

sessionId = getSessionId()
session_state = SessionState.get(sessionId=sessionId)


#st.write("ALWAYS RUN:", sessionId)
def main():
    global sessionId
    #sessionId = sessionId + 1

    #st.write("User Current Session Id: ", sessionId)
    #title
    st.markdown("<h3 style='box-shadow: 0 0 25px rgb(179, 182, 180);border-radius: 10px; border: 1px solid black;height:100%;padding: 20px 20px 20px 20px; text-align: center; background-color:#001a33; color:white;'>COVID-19 CASES IN THE PHILIPPINES</h3>", unsafe_allow_html=True)
    #st.markdown("<br><span style='border-radius: 5px; line-height: 80px ;padding: 5px 5px 5px 5px;  background-color: black; color: white;'><b>COVID-19 CASES IN THE PHILIPPINES</b></span><br>",unsafe_allow_html=True)
    activities = ["Search Location", "Current Location (Allow Access To Location)", "List of Covid-19 Cases", "Charts"]
    choice = st.sidebar.selectbox("", activities)

    # get covid cases
    df_covid_19_cases = getCovid19Cases()
    # move case_no to the left most
    case_no = df_covid_19_cases['case_no']
    df_covid_19_cases.drop(labels=['case_no'], axis=1, inplace=True)
    df_covid_19_cases.insert(0, 'case_no', case_no)
    # get latitude and longitude
    df_covid_19_cases_loc = df_covid_19_cases[['latitude', 'longitude']]

    # get covid cases Latest 7k
    df_covid_19_cases_latest = getCovid19CasesLatest()
    df_covid_19_cases_loc_latest = df_covid_19_cases_latest[['latitude', 'longitude']]
    if(df_covid_19_cases_loc_latest['latitude'].isnull().values.any()):
        df_covid_19_cases_loc_latest = df_covid_19_cases[['latitude', 'longitude']]


    #clean data for plotting else no plots in map
    df_covid_19_cases_loc_latest['latitude'] = df_covid_19_cases_loc_latest['latitude'].astype(float)
    df_covid_19_cases_loc_latest['longitude'] = df_covid_19_cases_loc_latest['longitude'].astype(float)
    #df_covid_19_cases_loc_latest['latitude'] = pd.to_numeric(df_covid_19_cases_loc_latest['latitude'], errors='coerce')
    #df_covid_19_cases_loc_latest['longitude'] = pd.to_numeric(df_covid_19_cases_loc_latest['longitude'],errors='coerce')
    df_covid_19_cases_loc_latest = df_covid_19_cases_loc_latest.dropna()

    nearest_case: None
    nearest_case_lat: None;
    nearest_case_lon: None;
    user_location:None;
    if choice == "Search Location":
        st.write("\n")
        st.write("\n")
        #user_address = st.text_input("Enter Location Below", "")
        user_address = st.text_input("Enter Location Below", "")
        submitButton = st.button("Submit Location")
        showDistance = st.checkbox('Compare Distance')

        if submitButton:
            #manual click the checkbox as hack
            # ip_address = get_client_address()
            # st.write(ip_address)

            locator = Nominatim(user_agent="myGeocoder")
            user_location = locator.geocode(user_address)

            if user_location:
                st.markdown("<span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color: none; color: white;'><b>MAP VIEW</b></span><br>",unsafe_allow_html=True)
                st.markdown("<div style='white-space: normal;'><span style='display: inline-block; word-wrap: break-word; border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color: green; color: white; border: 1px solid white;'><b>LOCATION: " + str(user_location) + "</b></span></div><br>", unsafe_allow_html=True)

                # covid-19 map
                # current location based on IP Address
                df_my_loc = pd.DataFrame(np.array([[user_location.latitude, user_location.longitude]]))
                df_my_loc.columns = ['latitude', 'longitude']
                #check distance if less than 10km
                nearest_case = None;
                if showDistance:
                    for row in df_covid_19_cases_loc_latest.itertuples():
                        covid_19_patient_loc = (row.latitude, row.longitude)
                        user_loc = (user_location.latitude, user_location.longitude)
                        distance = geodesic(user_loc, covid_19_patient_loc).km
                        #if distance < 10.0:
                        if distance:
                            if nearest_case is None:
                                nearest_case = distance
                            else:
                                if distance < nearest_case:
                                    nearest_case = distance
                                    #nearest_case = pd.DataFrame(np.array([[row.latitude, row.longitude]]))
                                    #st.write(nearest_case)
                                    nearest_case_lat = row.latitude
                                    nearest_case_lon = row.longitude

                #display nearest if less than 10KM
                if nearest_case != None:
                    #nearest_case_plot = pd.DataFrame(np.array([[nearest_case_lat, nearest_case_lon]]))
                    #st.dataframe(nearest_case_plot)
                    if nearest_case < 10.0:
                        st.markdown("<span style='white-space: normal; border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color: red; color: white; border: 1px solid white;'><b>DISTANCE FROM NEAREST CASE: " + str("{:.2f}".format(nearest_case)) + " KM</b></span><br>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color: green; color: white; border: 1px solid white;'><b>DISTANCE FROM NEAREST CASE: " + str("{:.2f}".format(nearest_case)) + " KM</b></span><br>", unsafe_allow_html=True)

                #st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color: none; color: white;'><b>MAP VIEW</b></span><br>",unsafe_allow_html=True)
                st.write("\n")
                st.write("\n")
                # st.dataframe(df_covid_19_cases_loc_latest)
                # st.dataframe(df_my_loc)
                #st.dataframe(nearest_case)
                map_display = st.info("Loading...")
                map_display2 = st.info("Loading...")
                map_display.deck_gl_chart(
                    viewport={
                         #'latitude': df_covid_19_cases_loc_latest['latitude'].values[0],
                         #'longitude': df_covid_19_cases_loc_latest['longitude'].values[0],
                        'latitude': user_location.latitude,
                        'longitude': user_location.longitude,
                        # 'latitude': my_loc_lat,
                        # 'longitude': my_loc_long,
                        'zoom': 11,
                        'pitch': 40,
                        #'mapStyle': 'mapbox://styles/mapbox/dark-v10'
                        'mapStyle': 'mapbox://styles/mapbox/satellite-v9'
                    },
                    layers=[{
                        'type': 'PointCloudLayer',
                        'data': df_covid_19_cases_loc_latest,
                        'radius': 200,
                        'elevationScale': 4,
                        'elevationRange': [0, 1000],
                        'pickable': True,
                        'extruded': True,
                        'getFillColor': [255, 8, 0],
                        'tooltip': True,
                        'hover': 'TEST'
                    },
                    {
                        'type': 'ScatterplotLayer',
                        'data': df_my_loc,
                        'radius': 1000,
                        #'opacity': 1,
                        #'getColor': [75, 205, 250],
                        #'autoHighlight': True,
                        'elevationScale': 4,
                        'elevationRange': [0, 1000],
                        'pickable': True,
                        'extruded': True,
                        'getFillColor': [30,144,255]
                    }])
                st.text("")
                map_display2.deck_gl_chart(
                    viewport={
                        # 'latitude': df_covid_19_cases_loc_latest['latitude'].values[0],
                        # 'longitude': df_covid_19_cases_loc_latest['longitude'].values[0],
                        'latitude': user_location.latitude,
                        'longitude': user_location.longitude,
                        # 'latitude': my_loc_lat,
                        # 'longitude': my_loc_long,
                        'zoom': 11,
                        'pitch': 40,
                        'mapStyle': 'mapbox://styles/mapbox/dark-v10'
                        #'mapStyle': 'mapbox://styles/mapbox/satellite-v9'
                    },
                    layers=[{
                        'type': 'HexagonLayer',
                        'data': df_covid_19_cases_loc_latest,
                        'radius': 200,
                        'elevationScale': 4,
                        'elevationRange': [0, 1000],
                        'pickable': True,
                        'extruded': True,
                        'getFillColor': [255, 8, 0],
                        'tooltip ': True
                    },
                        {
                            'type': 'ScatterplotLayer',
                            'data': df_my_loc,
                            'radius': 1000,
                            # 'opacity': 1,
                            # 'getColor': [75, 205, 250],
                            # 'autoHighlight': True,
                            'elevationScale': 4,
                            'elevationRange': [0, 1000],
                            'pickable': True,
                            'extruded': True,
                            'getFillColor': [30, 144, 255]
                        }])
                #st.map(df_covid_19_cases_loc_latest)


            # unable to search location
            else:
                st.info("No Location Found!")
                #st.markdown("<div style='border: 1px solid black;  word-wrap: break-word; eight:auto;; box-shadow: 0 0 8px rgb(179, 182, 180);border-radius: 12px; height:100%;padding: 20px 20px 20px 20px; background-color: #FFFFFF; color: black;display:block; text-align: start;'><p style='align:'center'><p style='height: 100%; text-align: justify;text-justify: inter-word;'><b>No Location Found...</b></p></div>",unsafe_allow_html=True)

    elif choice == "Current Location (Allow Access To Location)":


        #st.write("FIRST VALUE OF SESSIONID: ", sessionId)
        # if sessionId is not None:
        #     sessionId = getDBCountForSession()
        #     st.write("Current Location - User Current Session Id: ", sessionId[0])

        #sessionId = getSessionId()
        coordinates = getCoordinatesFromDB(session_state.sessionId)

        my_loc_lat: None
        my_loc_long: None
        #geocode_result = getLocation()
        geocode_result = None
        #st.write(geocode_result)
        if coordinates:
            # coordinates = web_element.split(":")
            my_loc_lat = float(coordinates[1])
            my_loc_long = float(coordinates[2])
            # my_loc_long = float(geocode_result['location']['lng'])
            # my_loc_lat = float(geocode_result['location']['lat'])
        else:
            #my_loc = geocoder.ipinfo('49.144.120.150')
            my_loc = geocoder.ipinfo('me')
            #my_loc = geocoder.ipinfo(ip)

            # my_loc_lat = float(latitude)
            # my_loc_long = float(longitude)
            # user_loc_string = str(my_loc.address)
            #st.write(my_loc.json)
            #st.write(str(my_loc_lat) + " : " + str(my_loc_long) + " "+ my_loc.city + " " + my_loc.country)
            # st.markdown(
            #     "<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color:; color: white;'><b>"+  my_loc.city + ", " + my_loc.country +"</b></span><br>",
            #     unsafe_allow_html=True)

        st.write("\n")
        st.write("\n")
        st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color:; color: white;'><b>MAP VIEW</b></span><br>",unsafe_allow_html=True)
        # st.markdown(
        #     "<div style='white-space: normal;'><span style='display: inline-block; word-wrap: break-word; border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color: green; color: white; border: 1px solid white;'><b>LOCATION: " + str(
        #         user_loc_string) + "</b></span></div><br>", unsafe_allow_html=True)
        # my_loc = geocoder.ip('me')[0]
        # # current location
        # my_loc_lat = my_loc.latlng[0]
        # my_loc_long = my_loc.latlng[1]
        # st.write(str(my_loc_lat) + " : " + str(my_loc_long))

        #st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color: black; color: white;'><b>CURRENT LOCATION (IP ADDRESS)</b></span><br>",unsafe_allow_html=True)
        # check distance if less than 10km
        # check distance if less than 10km
        nearest_case = None;
        for row in df_covid_19_cases_loc_latest.itertuples():
            covid_19_patient_loc = (row.latitude, row.longitude)
            user_loc = (my_loc_lat, my_loc_long)
            distance = geodesic(user_loc, covid_19_patient_loc).km
            #if distance < 10.0:
            if distance != None:
                if nearest_case is None:
                    nearest_case = distance
                else:
                    if distance < nearest_case:
                        nearest_case = distance

        # display nearest if less than 10KM
        #if nearest_case != None and nearest_case < 10.0:
        if nearest_case != None:
            if nearest_case < 10.0:
                st.markdown("<span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;background-color: red; color: white; border: 1px solid white;'><b>DISTANCE FROM NEAREST CASE: " + str("{:.2f}".format(nearest_case)) + " KM</b></span><br>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;background-color: green; color: white; border: 1px solid white;'><b>DISTANCE FROM NEAREST CASE: " + str("{:.2f}".format(nearest_case)) + " KM</b></span><br>", unsafe_allow_html=True)

        if my_loc_lat and my_loc_long:
            # covid-19 map
            #current location based on IP Address
            df_my_loc = pd.DataFrame(np.array([[my_loc_lat, my_loc_long]]))
            df_my_loc.columns = ['latitude', 'longitude']
            st.write("\n")
            st.spinner('Wait for it...')
            map_display = st.info("Loading...")
            map_display2 = st.info("Loading...")
            map_display.deck_gl_chart(
                viewport={
                    # 'latitude': user_location.latitude,
                    # 'longitude': user_location.longitude,
                    'latitude': my_loc_lat,
                    'longitude': my_loc_long,
                    'zoom': 12,
                    'pitch': 40,
                    'mapStyle': 'mapbox://styles/mapbox/satellite-v9'

                },
                layers=[{
                    'type': 'PointCloudLayer',
                    'data': df_covid_19_cases_loc_latest,
                    'radius': 200,
                    'elevationScale': 4,
                    'elevationRange': [0, 1000],
                    'pickable': True,
                    'extruded': True,
                    'getFillColor': [255, 8, 0]
                }, {
                    'type': 'ScatterplotLayer',
                    'data': df_my_loc,
                    'radius': 500,
                    'elevationScale': 4,
                    'elevationRange': [0, 1000],
                    'pickable': True,
                    'extruded': True,
                    'getFillColor': [30,144,255]
                }])
            st.write("\n")
            st.write("\n")
            st.text("")
            map_display2.deck_gl_chart(
                viewport={
                    # 'latitude': user_location.latitude,
                    # 'longitude': user_location.longitude,
                    'latitude': my_loc_lat,
                    'longitude': my_loc_long,
                    'zoom': 12,
                    'pitch': 40,
                    'mapStyle': 'mapbox://styles/mapbox/dark-v10'

                },
                layers=[{
                    'type': 'HexagonLayer',
                    'data': df_covid_19_cases_loc_latest,
                    'radius': 200,
                    'elevationScale': 4,
                    'elevationRange': [0, 1000],
                    'pickable': True,
                    'extruded': True,
                    'getFillColor': [255, 8, 0]
                }, {
                    'type': 'ScatterplotLayer',
                    'data': df_my_loc,
                    'radius': 500,
                    'elevationScale': 4,
                    'elevationRange': [0, 1000],
                    'pickable': True,
                    'extruded': True,
                    'getFillColor': [30, 144, 255]
                }])
            #st.map(df_covid_19_cases_loc_latest)
            # unable to search location
        else:
            st.markdown("<div style='border: 1px solid black;  word-wrap: break-word; eight:auto;; box-shadow: 0 0 8px rgb(179, 182, 180);border-radius: 12px; height:100%;padding: 20px 20px 20px 20px; background-color: #FFFFFF; color: #39B7CD;display:block; text-align: start;'><p style='align:'center'><p style='height: 100%; text-align: justify;text-justify: inter-word;'><b>No Location Found...</b></p></div>", unsafe_allow_html=True)

    elif choice == "List of Covid-19 Cases":
        # covid-19 cases dataframe
        st.write("\n")
        st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color:; color: white; borer: 1px solid white'><b>LIST OF COVID-19 CASES</b></span><br><br>",unsafe_allow_html=True)
        # cols = ["latitude", "longitude"]
        # st_ms = st.multiselect("Columns", df_covid_19_cases_latest.columns.tolist(), default=cols)
        # st.dataframe(st_ms)
        st.dataframe(df_covid_19_cases_latest)
        # st.write("\n")
        # st.write("\n")
        # st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color:; color: white; borer: 1px solid white'><b>OUTDATED LIST</b></span><br><br>",unsafe_allow_html=True)
        # st.dataframe(df_covid_19_cases)
        df_date_reported = df_covid_19_cases_latest.groupby('date_reported').count()
        df_date_reported = df_date_reported["case_code"].reset_index()
        df_date_reported.columns = ["Date", "Total"]
        st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color:; color: white; borer: 1px solid white'><b>CASES PER DAY</b></span><br><br>",unsafe_allow_html=True)
        st.dataframe(df_date_reported)
    elif choice == "Charts":
        st.write("\n")
        # Bar chart to show the Health Status using plotly
        # df_date_reported = df_covid_19_cases_latest.groupby('date_reported').count()
        # #df_date_reported = df_date_reported["case_code"].reset_index()
        # df_date_reported.columns = ["Date", "Total"]
        #st.bar_chart(df_date_reported)
        # Bar chart to show the Top 15 By Location using plotly
        st.markdown(
            "<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color:; color: white; borer: 1px solid white;'><b>DAILY CASES</b></span>",
            unsafe_allow_html=True)
        df_cases_data = df_covid_19_cases_latest.copy()
        df_cases_data['Count'] = 1
        k_location = pd.DataFrame(df_cases_data.groupby(['date_reported'], sort=False)['date_reported'].count().rename_axis(
            ["Number of Cases Per Location"]))
        Location = pd.Series(k_location.index[:])
        Count = list(k_location['date_reported'][:])
        Location_Count = pd.DataFrame(list(zip(Location, Count)), columns=['Location', 'Count'])
        daily_cases_fig = px.bar(Location_Count, x='Location', y='Count', color='Count',
                              labels={'Location': '', 'Count': ''},
                              color_continuous_scale='Bluered_r', text = Count)
        daily_cases_fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'font': dict(family="Roboto", size=12, color='white')
        })
        st.plotly_chart(daily_cases_fig)

        st.write("\n")
        st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color:; color: white; borer: 1px solid white;'><b>REGION</b></span>",unsafe_allow_html=True)
        grp_data_health = df_covid_19_cases_latest.copy()
        grp_data_health['Count'] = 1
        k_health = pd.DataFrame(
            grp_data_health.groupby(['region_res'], sort=False)['region_res'].count().rename_axis(
                ["Region"]).nlargest(10))
        health_status = pd.Series(k_health.index[:])
        health_status_count = list(k_health['region_res'][:])
        health_count = pd.DataFrame(list(zip(health_status, health_status_count)), columns=['Region', 'Count'])
        health_fig = px.bar(health_count, x='Region', y='Count', color='Count',
                            labels={'Region': '', 'Count': ''}, text = health_status_count)
        health_fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            #'font': dict(family="Courier New, monospace",size=16,color="#7f7f7f")
            'font': dict(family="Roboto", size=12, color='white')
        })
        st.plotly_chart(health_fig)

        # Bar chart to show the Top 15 By Location using plotly
        st.write("\n")
        st.markdown(
            "<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color:; color: white; borer: 1px solid white;'><b>LOCATION</b></span>",
            unsafe_allow_html=True)
        location_data = df_covid_19_cases_latest.copy()
        location_data['Count'] = 1
        k_location = pd.DataFrame(location_data.groupby(['prov_city_res'], sort=False)['prov_city_res'].count().rename_axis(
            ["Number of Cases Per Location"]).nlargest(15))
        Location = pd.Series(k_location.index[:])
        Count = list(k_location['prov_city_res'][:])
        Location_Count = pd.DataFrame(list(zip(Location, Count)), columns=['Location', 'Count'])
        location_fig = px.bar(Location_Count, x='Location', y='Count', color='Count',
                              labels={'Location': '', 'Count': ''},
                              color_continuous_scale='Bluered_r', text = Count)
        location_fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'font': dict(family="Roboto", size=12, color='white')
        })
        st.plotly_chart(location_fig)

        # Bar chart to show the Top 15 By Travel History using plotly
        st.write("\n")
        # 001a33 -
        st.markdown(
            "<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color:; color: white; borer: 1px solid white;'><b>TRAVEL HISTORY (Outdated)</b></span>",
            unsafe_allow_html=True)
        travel_history_data = df_covid_19_cases.copy()
        travel_history_data['Count'] = 1
        k_travel_history = pd.DataFrame(
            travel_history_data.groupby(['travel_history'], sort=False)['travel_history'].count().rename_axis(
                ["Travel History"]).nlargest(20))
        Travel_History = pd.Series(k_travel_history.index[:])
        Travel_Count = list(k_travel_history['travel_history'][:])
        Travel_History_Count = pd.DataFrame(list(zip(Travel_History, Travel_Count)),
                                            columns=['Travel_History', 'Count'])
        travel_fig = px.bar(Travel_History_Count, x='Travel_History', y='Count', color='Count',
                            labels={'Travel_History': '', 'Count': ''},
                            color_continuous_scale=px.colors.sequential.RdBu, text = Travel_Count)
        travel_fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'font': dict(family="Roboto", size=12, color='white')
        })
        st.plotly_chart(travel_fig)

        # #plot location using folium
        # locationlist = df_covid_19_cases_loc_latest.values.tolist()
        # #st.write(str(locationlist))
        # map = folium.Map(location=[14.50, 121], zoom_start=12)
        # for point in range(0, len(locationlist)):
        #     folium.Circle(locationlist[point],
        #     radius=500,
        #     popup='Positive Covid-19 Case',color='crimson',
        #     fill=True,
        #     fill_color='crimson'
        # ).add_to(map)
        # map.save('covid_19_ph.html')
        # #html_string = map._repr_html_()checkbox
        #
        # st.markdown(map._repr_html_(), unsafe_allow_html=True)
        #unable to search location
        # else:
        #     st.markdown("<div style='border: 1px solid black;  word-wrap: break-word; eight:auto; box-shadow: 0 0 8px rgb(179, 182, 180);border-radius: 12px; height:100%;padding: 20px 20px 20px 20px; background-color: #FFFFFF; color: #39B7CD;display:block; text-align: start;'><p style='align:'center'><p style='height: 100%; text-align: justify;text-justify: inter-word;'><b>No Location Found...</b></p></div>",unsafe_allow_html=True)

if __name__ == '__main__' :
    main()




