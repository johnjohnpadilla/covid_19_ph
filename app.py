import streamlit as st
import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
from geopy.geocoders import Nominatim
import geocoder
from geopy.distance import geodesic

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

local_css("style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

#icon("search")
#selected = st.text_input("", "Search...")
#button_clicked = st.button("OK")

@st.cache(allow_output_mutation=True)
def getCovid19Cases():
    URL = "https://coronavirus-ph-api.herokuapp.com/cases"
    headers = {'content-type': 'application/json'}
    response = requests.get(URL, headers=headers)
    covid_19_json = response.json()
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

def main():
    #title
    st.markdown("<h3 style='box-shadow: 0 0 25px rgb(179, 182, 180);border-radius: 10px; border: 1px solid black;height:100%;padding: 20px 20px 20px 20px; text-align: center; background-color:#001a33; color:white;'>COVID-19 CASES IN THE PHILIPPINES</h3>", unsafe_allow_html=True)
    #st.markdown("<br><span style='border-radius: 5px; line-height: 80px ;padding: 5px 5px 5px 5px;  background-color: black; color: white;'><b>COVID-19 CASES IN THE PHILIPPINES</b></span><br>",unsafe_allow_html=True)
    activities = ["Search Location", "Use Current Location (IP Address)", "List of Covid-19 Cases", "Charts"]
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
        df_covid_19_cases_loc_latest = df_covid_19_cases
    #st.dataframe(df_covid_19_cases_loc_latest)

    if choice == "Search Location":
        st.write("\n")
        st.write("\n")
        #user_address = st.text_input("Enter Location Below", "")
        user_address = st.text_input("Enter Location Below", "")
        submitButton = st.button("Submit Location")
        showDistance = st.checkbox('Compare Distance')
        nearest_case_lat: None;
        nearest_case_lon: None;
        if submitButton:
            locator = Nominatim(user_agent="myGeocoder")
            user_location = locator.geocode(user_address)
           # st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color: black; color: white;'><b>LOCATION:</b></span>",unsafe_allow_html=True)
            st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color: green; color: white; border: 1px solid white;'><b>LOCATION: " + str(user_location) + "</b></span><br>",unsafe_allow_html=True)
            if user_location:
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
                        if distance < 10.0:
                            if nearest_case is None:
                                nearest_case = distance
                            else:
                                if distance < nearest_case:
                                    nearest_case = distance
                                    # nearest_case_lat = row.latitude
                                    # nearest_case_lon = row.longitude

                #display nearest if less than 10KM
                if nearest_case != None:
                    #nearest_case_plot = pd.DataFrame(np.array([[nearest_case_lat, nearest_case_lon]]))
                    #st.dataframe(nearest_case_plot)
                    if nearest_case < 10.0:
                        st.markdown("<span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color: red; color: white; border: 1px solid white;'><b>DISTANCE TO NEAREST CONFIRMED CASE : " + str("{:.2f}".format(nearest_case)) + " KM</b></span><br>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color: green; color: white; border: 1px solid white;'><b>DISTANCE TO NEAREST CONFIRMED CASE : " + str("{:.2f}".format(nearest_case)) + " KM</b></span><br>", unsafe_allow_html=True)


                st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color: none; color: white;'><b>MAP VIEW</b></span><br>",unsafe_allow_html=True)
                st.write("\n")
                st.deck_gl_chart(
                    viewport={
                        'latitude': user_location.latitude,
                        'longitude': user_location.longitude,
                        # 'latitude': my_loc_lat,
                        # 'longitude': my_loc_long,
                        'zoom': 11,
                        'pitch': 40,
                        'mapStyle' : 'mapbox://styles/mapbox/dark-v10'
                    },
                    layers=[{
                        'type': 'HexagonLayer',
                        'data': df_covid_19_cases_loc_latest,
                        'radius': 400,
                        'elevationScale': 4,
                        'elevationRange': [0, 1000],
                        'pickable': True,
                        'extruded': True,
                        'getFillColor': [255, 8, 0],
                        #'getFillColor': (300, 300, 180, 200)
                        #'getFillColor': [50, 100, 50] green
                        #'getFillColor': [248, 24, 148]
                #     }, {
                #     'type': 'ArcLayer',
                #     'data': df_my_loc,
                #     'radius': 500,
                #     'elevationScale': 8,
                #     'elevationRange': [0, 1000],
                #     'pickable': True,
                #     'extruded': True,
                #     'getFillColor': [100,100,100]
                 }, {
                    'id': "scat-blue",
                    'type': 'ScatterplotLayer',
                    'data': df_my_loc,
                    'radius': 1000,
                    'opacity': 1,
                    'getColor': [75, 205, 250],
                    'autoHighlight': True,
                    'elevationScale': 4,
                    'elevationRange': [0, 1000],
                    'pickable': True,
                    'extruded': True,
                    'getFillColor': [30,144,255]
                }
                #         , {
                #     'type': 'ScatterplotLayer',
                #     'data':  nearest_case_plot,
                #     'radius': 500,
                #     'elevationScale': 4,
                #     'elevationRange': [0, 1000],
                #     'pickable': True,
                #     'extruded': True,
                #     'getFillColor': [30,144,255]
                # }
                    ])
                st.write("\n")
                st.write("\n")
                #st.map(df_covid_19_cases_loc_latest)


            # unable to search location
            else:
                st.markdown("<div style='border: 1px solid black;  word-wrap: break-word; eight:auto;; box-shadow: 0 0 8px rgb(179, 182, 180);border-radius: 12px; height:100%;padding: 20px 20px 20px 20px; background-color: #FFFFFF; color: black;display:block; text-align: start;'><p style='align:'center'><p style='height: 100%; text-align: justify;text-justify: inter-word;'><b>No Location Found...</b></p></div>",unsafe_allow_html=True)

    elif choice == "Use Current Location (IP Address)":
        st.write("\n")
        st.write("\n")
        my_loc = geocoder.ip('me')
        # st.write(str(my_loc.latlng[0]) + " : " + str(my_loc.latlng[1]))
        # current location
        my_loc_lat = my_loc.latlng[0]
        my_loc_long = my_loc.latlng[1]
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
                st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;background-color: red; color: white; border: 1px solid white;'><b>DISTANCE TO NEAREST CONFIRMED CASE : " + str("{:.2f}".format(nearest_case)) + " KM</b></span><br>", unsafe_allow_html=True)
            else:
                st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;background-color: green; color: white; border: 1px solid white;'><b>DISTANCE TO NEAREST CONFIRMED CASE : " + str("{:.2f}".format(nearest_case)) + " KM</b></span><br>", unsafe_allow_html=True)

        if my_loc_lat and my_loc_long:
            # covid-19 map
            #current location based on IP Address
            df_my_loc = pd.DataFrame(np.array([[my_loc_lat, my_loc_long]]))
            df_my_loc.columns = ['latitude', 'longitude']
            st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px;  background-color:; color: white;'><b>MAP VIEW</b></span><br>",unsafe_allow_html=True)
            st.write("\n")
            st.deck_gl_chart(
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
                    'getFillColor': [30,144,255]
                }])
            st.write("\n")
            st.write("\n")
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
        st.write("\n")
        st.write("\n")
        st.dataframe(df_covid_19_cases)
        st.write("\n")
        st.write("\n")
        df_date_reported = df_covid_19_cases_latest.groupby('date_reported').count()
        df_date_reported = df_date_reported["case_code"].reset_index()
        df_date_reported.columns = ["Date", "Total"]
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
        location_fig = px.bar(Location_Count, x='Location', y='Count', color='Count',
                              labels={'Location': '', 'Count': ''},
                              color_continuous_scale='Bluered_r', text = Count)
        st.plotly_chart(location_fig)

        st.write("\n")
        st.markdown("<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color:; color: white; borer: 1px solid white;'><b>HEALTH STATUS (Outdated)</b></span>",unsafe_allow_html=True)
        grp_data_health = df_covid_19_cases.copy()
        grp_data_health['Count'] = 1
        k_health = pd.DataFrame(
            grp_data_health.groupby(['health_status'], sort=False)['health_status'].count().rename_axis(
                ["Health Status"]).nlargest(15))
        health_status = pd.Series(k_health.index[:])
        health_status_count = list(k_health['health_status'][:])
        health_count = pd.DataFrame(list(zip(health_status, health_status_count)), columns=['Health Status', 'Count'])
        health_fig = px.bar(health_count, x='Health Status', y='Count', color='Count',
                            labels={'Health Status': '', 'Count': ''}, text = health_status_count)
        st.plotly_chart(health_fig)

        # Bar chart to show the Top 15 By Location using plotly
        st.write("\n")
        st.markdown(
            "<br><span style='border-radius: 5px; line-height: 40px ;padding: 5px 5px 5px 5px; background-color:; color: white; borer: 1px solid white;'><b>LOCATION (Outdated)</b></span>",
            unsafe_allow_html=True)
        location_data = df_covid_19_cases.copy()
        location_data['Count'] = 1
        k_location = pd.DataFrame(location_data.groupby(['location'], sort=False)['location'].count().rename_axis(
            ["Number of Cases Per Location"]).nlargest(15))
        Location = pd.Series(k_location.index[:])
        Count = list(k_location['location'][:])
        Location_Count = pd.DataFrame(list(zip(Location, Count)), columns=['Location', 'Count'])
        location_fig = px.bar(Location_Count, x='Location', y='Count', color='Count',
                              labels={'Location': '', 'Count': ''},
                              color_continuous_scale='Bluered_r', text = Count)
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
        st.plotly_chart(travel_fig)

            #plot location using folium
        locationlist = df_covid_19_cases_loc.values.tolist()
        #st.write(str(locationlist))
        # map = folium.Map(location=[14.50, 121], zoom_start=12)
        # for point in range(0, len(locationlist)):
        #     folium.Circle(locationlist[point],
        #     radius=500,
        #     popup='Positive Covid-19 Case',color='crimson',
        #     fill=True,
        #     fill_color='crimson'
        # ).add_to(map)
        # #map.save('covid_19_ph.html')
        # html_string = map._repr_html_()
        # st.markdown(html_string, unsafe_allow_html=True)
        #unable to search location
        # else:
        #     st.markdown("<div style='border: 1px solid black;  word-wrap: break-word; eight:auto; box-shadow: 0 0 8px rgb(179, 182, 180);border-radius: 12px; height:100%;padding: 20px 20px 20px 20px; background-color: #FFFFFF; color: #39B7CD;display:block; text-align: start;'><p style='align:'center'><p style='height: 100%; text-align: justify;text-justify: inter-word;'><b>No Location Found...</b></p></div>",unsafe_allow_html=True)

if __name__ == '__main__' :
    main()