import streamlit as st
from Classes import *

#👉👉👉Streamlit

st.sidebar.title(":blue[Watsapp Analizer]📈📉")
file=st.sidebar.file_uploader("Upload your file")
st.sidebar.write("")
if file is not None:
    data_bytes=file.getvalue()
    data_file=data_bytes.decode("utf-8")
    data=Preprocess_data(data_file)
    select_user=st.sidebar.selectbox("Select on choice",user_list(data["users"]))
    if st.sidebar.button("Run Analysis"):

       st.header("",divider="rainbow")
       with st.popover("Show Statics",use_container_width=20):
          col1,col2,col3,col4=st.columns([1,1,1,1])
          stat=Statics(data,select_user)
          with col1:
             col1.header("Total Message",divider='rainbow')
             col1.header(stat.Total_message())
             col1.write("")
          with col2:
             col2.header("Total Word",divider='rainbow')
             col2.header(stat.Word_count())
             col2.write("")
          with col3:
             col3.header("Total Link",divider='rainbow')
             col3.header(stat.Total_link())
             col3.write("")
          with col4:
             col4.header("Total Media",divider='rainbow')
             col4.header(stat.Total_media())
             col4.write("")

       st.header("Show The Plot",divider="rainbow")
       with st.container():
             Pl=Plot_libary(data,select_user)
             st.subheader("Top Busy User",divider='rainbow')
             st.pyplot(Pl.Barplot())
             st.write("")

             st.subheader("User Contribution",divider='rainbow')
             st.pyplot(Pl.Piechart())
             st.write("")

             st.subheader("Word Cloud",divider='rainbow')
             st.pyplot(Pl.Wordcloudplot())
             st.write("")

             st.subheader("Top Word Used",divider='rainbow')
             st.pyplot(Pl.Top_word())
             st.write("")

             st.subheader("Top Emoji",divider='rainbow')
             st.dataframe(Pl.Found_emoji())
             st.write("")

       st.header("Show The Timestamp ",divider="rainbow")
       with st.container():
             Ts=Time_stamp(data,select_user)
             st.subheader("Busy Year-Month",divider='rainbow')
             st.pyplot(Ts.Busy_year_month())
             st.write("")

             st.subheader("Busy Day",divider='rainbow')
             st.pyplot(Ts.Busy_day())
             st.write("")

             st.subheader("Busy Month",divider='rainbow')
             st.pyplot(Ts.Busy_month())
             st.write("")

             st.subheader("Busy Day-Name",divider='rainbow')
             st.pyplot(Ts.Busy_day_name())
             st.write("")

             st.subheader("Busy Time",divider='rainbow')
             st.pyplot(Ts.Busy_time_ap())
             st.write("")

             st.subheader("Busy Heatmap",divider='rainbow')
             st.pyplot(Ts.Busy_heatmap())
             st.write("")

       st.header("Nearest friend ",divider="rainbow")
       if select_user!='Overall':
         with st.container():
             st.write(Nearest(data,select_user))
       
      


