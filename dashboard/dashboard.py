#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


# In[3]:


day_df = pd.read_csv("dashboard/day_clean.csv")
day_df.head()


# In[4]:


hour_df = pd.read_csv("dashboard/hour_clean.csv")
hour_df.head()


# ## Helper Functions

# In[5]:


def create_daily_order_df(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    daily_order_df = df.resample(rule='D', on='dteday').sum()
    return daily_order_df


# In[6]:


def create_sum_casual_users_df(df):
    sum_casual_user_df = df.groupby("dteday").casual.sum().sort_values(ascending=False).reset_index()
    return sum_casual_user_df


# In[7]:


def create_sum_registered_users_df(df):
    sum_registered_user_df = df.groupby("dteday").registered.sum().sort_values(ascending=False).reset_index()
    return sum_registered_user_df


# In[8]:


def create_byseason_df(df):
    sum_casual_users_df = df.groupby("season_new").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_casual_users_df


# In[9]:


def create_byhour_df(df):
    sum_hr_df = hour_df.groupby("hr").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_hr_df


# In[10]:


def create_byweekday_df(df):
    sum_weekday_df = day_df.groupby("weekday_new").cnt.mean().sort_values(ascending=False).reset_index()
    return sum_weekday_df


# In[11]:


def create_by_yrmnth_df(df):
    sum_yrmnth_orders_df = df.groupby(by=["Year", "mnth"]).agg({
                  "casual": "sum",
                  "registered": "sum",
                  "cnt": "sum"
    })
    return sum_yrmnth_orders_df


# In[12]:


def create_rfm_df(df):
    rfm_df = day_df.groupby(by="weekday_new", as_index=False).agg({
    "dteday": "max", # mengambil tanggal peminjaman terakhir
    "cnt": "sum" # menghitung jumlah peminjaman
})
    rfm_df.columns = ["weekday", "max_order_timestamp", "frequency"]

    # menghitung kapan terakhir pelanggan melakukan peminjaman (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = day_df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df


# In[13]:


#Change dteday column Data Type
datetime_columns = ["dteday"]

day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)

hour_df.sort_values(by="dteday", inplace=True)
hour_df.reset_index(inplace=True)

for column in datetime_columns:
  day_df[column] = pd.to_datetime(day_df[column])
  hour_df[column] = pd.to_datetime(day_df[column])


# In[14]:


#Ensure whether data type of dteday column has been changed
day_df.info()


# In[15]:


min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("dashboard/logo_freepik.jpg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Span',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )


# In[16]:


main_df_day = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]
main_df_hour = hour_df[(hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))]


# In[17]:


daily_order_df = create_daily_order_df(main_df_day)
sum_casual_users_df = create_sum_casual_users_df(main_df_day)
sum_registered_users_df = create_sum_registered_users_df(main_df_day)
byseason_df = create_byseason_df(main_df_day)
byhour_df = create_byhour_df(main_df_hour)
byweekday_df = create_byweekday_df(main_df_day)
by_yrmnth_df = create_by_yrmnth_df(main_df_day)
rfm_df = create_rfm_df(main_df_day)


# In[28]:


st.header('Capital Bike Sharing Analysis Dashboard :person biking:')
st.subheader('Daily Bike Renting')

col1, col2, col3 = st.columns(3)
 
with col1:
    total_users = daily_order_df.cnt.sum()
    st.metric("Total Users", value=total_users)
 
with col2:
    total_registered_users = sum_registered_users_df.registered.sum() 
    st.metric("Total Registered Users", value=total_registered_users)
    
with col3:
    total_casual_users = sum_casual_users_df.casual.sum() 
    st.metric("Total Casual Users", value=total_casual_users)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_order_df.index,
    daily_order_df["cnt"],
    marker='o', 
    linewidth=2,
    color="#90CAF9",
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)


# In[33]:


st.subheader("Most and Least Bike Rentals Each Season")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="cnt", y="season_new", data=byseason_df.sort_values(by="cnt", ascending=False), palette=colors, ax=ax[0])
ax[0].set_ylabel("Season", size=30)
ax[0].set_xlabel("Count", size=30)
ax[0].set_title("Most Bike Rentals", loc="center", fontsize=40)
ax[0].tick_params(axis ='y', labelsize=30)
ax[0].tick_params(axis ='x', labelsize=30)

sns.barplot(x="cnt", y="season_new", data=byseason_df.sort_values(by="cnt", ascending=True), palette=colors, ax=ax[1])
ax[1].set_ylabel("Season", size=30)
ax[1].set_xlabel("Count", size=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Least Bike Rentals", loc="center", fontsize=40)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis ='x', labelsize=30)

st.pyplot(fig)


# In[32]:


st.subheader("Most and Least Bike Rentals Each Hour")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
coolors = ["#D3D3D3", "#D3D3D3", "#72BCD4", "#D3D3D3", "#D3D3D3"]
coolorss = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4", "#D3D3D3"]

sns.barplot(x="hr", y="cnt", data=byhour_df.sort_values(by="cnt", ascending=False).head(5), palette=coolors, ax=ax[0])
ax[0].set_ylabel("Count", size=30)
ax[0].set_xlabel("Hour", size=30)
ax[0].set_title("Most Bike Rentals", loc="center", fontsize=40)
ax[0].tick_params(axis ='y', labelsize=30)
ax[0].tick_params(axis ='x', labelsize=30)

sns.barplot(x="hr", y="cnt", data=byhour_df.sort_values(by="cnt", ascending=True).head(5), palette=coolorss, ax=ax[1])
ax[1].set_ylabel("Count", size=30)
ax[1].set_xlabel("Hour", size=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Least Bike Rentals", loc="center", fontsize=40)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis ='x', labelsize=30)

st.pyplot(fig)


# In[34]:


st.subheader("Most and Least Bike Rentals Each Day")

fig, ax = plt.subplots(figsize=(35, 15))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="weekday_new", 
            y="cnt", 
            data=byweekday_df.sort_values(by="cnt", ascending=False).head(5), 
            palette=colors)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=30)
st.pyplot(fig)


# In[35]:


st.subheader("Sum of Registered User Each Month From 2011 - 2012")

fig, ax = plt.subplots(figsize=(35, 15))

by_yrmnth_df['registered'].plot(
    kind='line',
    marker='o',
    linewidth=2,
    color="#72BCD4")
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=30)

plt.gca().spines[['top', 'right']].set_visible(False)

st.pyplot(fig)


# In[36]:


st.subheader("RFM Analysis (Weekday)")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="weekday", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=30)
ax[0].tick_params(axis ='x', labelsize=20)
ax[0].tick_params(axis ='y', labelsize=20)

sns.barplot(y="frequency", x="weekday", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=30)
ax[1].tick_params(axis='x', labelsize=20)
ax[1].tick_params(axis ='y', labelsize=20)

st.pyplot(fig)

