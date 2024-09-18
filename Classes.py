import nltk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import string
import emoji
from urlextract import URLExtract
from wordcloud import WordCloud,STOPWORDS
from nltk.corpus import stopwords
import nltk
from datetime import datetime
import gensim
from gensim.utils import simple_preprocess
from sklearn.neighbors import NearestNeighbors
nltk.download('stopwords')

## user list
def user_list(col):
  user=col.unique().tolist()
  if "group notification" in user:
        user.remove("group notification")
  user.sort()
  user.insert(0,"Overall")
  return user


#message_preprocessing
def Message_preprocessing(df):
       ext=URLExtract()
       list=[]
       for text in df["messages"]:
          text=text.lower()
          text=emoji.replace_emoji(text, replace='')
          url_l=ext.find_urls(text)
          for i in url_l:
                if len(url_l)!=0:
                    text=text.replace(f"{i}","")
          text=re.sub("<media omitted>","",text)
          text=re.sub("www.\w+","",text)
          text=re.sub("\w+@gmail.com","",text)
          if re.findall("-\s",text):
               text=""
          if sum([i in text for i in ["this message was deleted","videocalls","you deleted this message","missed voice call"]]):
                 text=""
          if text!="":
             list.append(text)
       text_l=" ".join(list).split()
       new_l=[]
       for i in text_l:
          if i not in string.punctuation:
            if i not in stopwords.words('english'):
              if len(i[2:])>0:
                 new_l.append(i)
       return new_l


#Preprocess_data
def Preprocess_data(file):

     exp=r"\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}\s+..."
     date_time_file=re.findall(exp,file)
     text=re.split(exp,file)[1:]

     data=pd.DataFrame({"date_time_file":date_time_file,"text":text})
     data.drop(0,axis=0,inplace=True)

     data["date"]=pd.to_datetime(data["date_time_file"].apply(lambda x:re.findall(r"\d{1,2}/\d{1,2}/\d{1,3}",x)[0]),format="%d/%m/%y")
     data["time"]=data["date_time_file"].apply(lambda x:re.findall(r"\d{1,2}:\d{1,2}\s+\w+",x)[0])
     data["time_baje"]=data["time"].apply(lambda x:re.findall("\d{1,2}:\d{1,2}",x)[0])
     data["time_ap"]=data["time"].apply(lambda x:re.split("\d{1,2}:\d{1,2}",x)[1])
     data["time_ap"]=data["time_ap"]. apply(lambda x : x.strip())
     data["month_num"]=data["date"].dt.month

     data["year"]=data["date"].dt.year
     data["month_name"]=data["date"].dt.month_name()
     data["day_name"]=data["date"].dt.day_name()

     date_time_ap=data["time_baje"].apply(lambda x:re.split(":",x)[0]).astype("int")
     time_range=date_time_ap.apply(lambda x: f"{x}-{x+1}" if x!=12 else "12-1")+" "+data["time_ap"]
     data["time_range_ap"]=time_range

     users=[]
     messages=[]
     for t in data["text"]:
        l=re.split("([\w\W]+?):\s",t)
        if l[1:]:
           users.append(l[1])
           messages.append(l[2])
        else:
           users.append(r"ggroup notification")
           messages.append(l[0])

     data["users"]=users
     data["users"]=data["users"].apply(lambda x:x[1:].strip())
     data["messages"]=messages
     data["messages"]=data["messages"].apply(lambda x:x.strip())
     data["messages"]=data["messages"].replace("null","Videocalls")

     new_data=data.drop(["date_time_file","text","time","time_baje","time_ap",],axis=1)
     df=new_data.copy()
     return df

#Statics
class Statics:
   def __init__(self,df,select_name):
      self.df=df
      if select_name!="Overall":
         self.df=self.df[self.df["users"]==select_name]
   def Total_message(self):
      df=self.df
      try:
          Total_message=df["messages"].shape[0]-df["messages"].value_counts()[""]
      except:
          Total_message=df["messages"].shape[0]
      return Total_message
   def Word_count(self):
       df=self.df
       ext=URLExtract()
       list=[]
       for text in df["messages"]:
          text=text.lower()
          text=emoji.replace_emoji(text, replace='')
          url_l=ext.find_urls(text)
          for i in url_l:
                if len(url_l)!=0:
                    text=text.replace(f"{i}","")
          text=re.sub("<media omitted>","",text)
          text=re.sub("www.\w+","",text)
          text=re.sub("\w+@gmail.com","",text)
          if re.findall("-\s",text):
               text=""
          if sum([i in text for i in ["this message was deleted","videocalls","you deleted this message","missed voice call"]]):
                 text=""
          if text!="":
             list.append(text)
       text_l=" ".join(list).split()
       return len(text_l)

   def Total_link(self):
       df=self.df
       ext=URLExtract()
       list=[]
       for text in df["messages"]:
          list.extend(ext.find_urls(text))
       return len(list)

   def Total_media(self):
       df=self.df
       return df[df["messages"]=="<Media omitted>"].shape[0]

   def Total_link(self):
       df=self.df
       ext=URLExtract()
       list=[]
       for text in df["messages"]:
          list.extend(ext.find_urls(text))
       return len(list)

   def Total_media(self):
       df=self.df
       return df[df["messages"]=="<Media omitted>"].shape[0]

#Plot_libary

class Plot_libary:
    def __init__(self,df,select_name):
        self.df=df
        if select_name!="Overall":
            self.df=self.df[self.df["users"]==select_name]
    def Barplot(self):
        df=self.df
        fig, axis = plt.subplots()
        X = df["users"].value_counts()[0:8]
        sns.barplot(x=X.index, y=X.values, palette="gist_rainbow_r", ax=axis)
        axis.set_xticklabels(X.index, rotation=90)
        axis.set_xlabel("User name")
        axis.set_ylabel("Number of count")
        return fig
    def Piechart(self):
        df=self.df
        fig, axis = plt.subplots()
        X = df["users"].value_counts().head()
        axis.pie(X,labels=X.index,autopct="%1.2f%%",explode=[i*0.2 for i in range(X.shape[0])],radius=2,rotatelabels=False)
        return fig

    def Wordcloudplot(self):
        df=self.df
        list=Message_preprocessing(df)
        text=" ".join(list)
        wc=WordCloud(width=400,height=400,background_color="white",stopwords = set(STOPWORDS)).generate(text)
        fig, axis = plt.subplots()
        axis.imshow(wc)
        return fig

    def Top_word(self):
        df=self.df
        list=Message_preprocessing(df)
        text_l=" ".join(list).split()
        new_l=[]
        for i in text_l:
          if i not in string.punctuation:
            if i not in stopwords.words('english'):
              if i  not in ['hai','ke', 'he', 'me', 'ni', 'Videocalls', 'to', 'ko', 'ka', 'ki','se', 'bhi', 'hi', 'kar', 'kya', 'le', 'ho', 'nahi','के','kr','tha','Me','Ye','raha','de','ja','lo','ne','में', 'h','tu','Tu','Or','है','kai','hu','से','को','pe','ye','की']:
                 new_l.append(i)
        dt=pd.DataFrame(new_l,columns=["word"])
        dt=dt["word"].value_counts()[0:30].reset_index()
        fig, axis = plt.subplots()
        sns.barplot(x=dt["word"], y=dt["count"], palette="gist_rainbow_r", ax=axis,orient="v")
        axis.set_xticklabels(dt["word"], rotation=90)
        axis.set_xlabel("Word Count")
        axis.set_ylabel("Word")
        return fig

    def Found_emoji(self):
      df=self.df
      X=" ".join(df["messages"].values)
      X=X.split()
      list=[]
      emoji_l=emoji.EMOJI_DATA
      for i in X:
         list.extend([j for j in i if j in emoji_l])
      return pd.Series(list).value_counts().reset_index()
    
#Time_stamp library


class Time_stamp:
    def __init__(self,df,select_name):
        self.df=df
        if select_name!="Overall":
            self.df=self.df[self.df["users"]==select_name]

    def Busy_year_month(self):
        df=self.df
        fig, axis = plt.subplots()
        dt=df.groupby(["year","month_num","month_name"]).count()["messages"].reset_index()
        dt["month_year"]=dt["month_name"]+"-"+dt["year"].astype("str")
        sns.barplot(x=dt["month_year"], y=dt["messages"], palette="gist_rainbow_r", ax=axis)
        axis.set_xticklabels(dt["month_year"],rotation="vertical")
        axis.set_xlabel("Year-Month")
        axis.set_ylabel("Number of count")
        return fig

    def Busy_day(self):
        df=self.df
        fig, axis = plt.subplots(figsize=(17,12))
        df["only_date"]=df["date"].dt.date
        dt=df.groupby(["only_date"]).count()["messages"].reset_index()
        sns.lineplot(x=dt["only_date"], y=dt["messages"], color="green", ax=axis)
        axis.set_xlabel("year-month-date")
        axis.set_ylabel("Number of count")
        return fig

    def Busy_month(self):
        df=self.df
        fig, axis = plt.subplots()
        dt=df["month_name"].value_counts().reset_index()
        sns.barplot(x=dt["month_name"], y=dt["count"],  ax=axis,palette="gist_rainbow")
        axis.set_xticklabels(dt["month_name"],rotation="vertical")
        axis.set_xlabel("Month Name")
        axis.set_ylabel("Number of Count")
        return fig

    def Busy_day_name(self):
        df=self.df
        fig, axis = plt.subplots()
        dt=df["day_name"].value_counts().reset_index()
        sns.barplot(x=dt["day_name"], y=dt["count"],  ax=axis,palette="gist_rainbow_r")
        axis.set_xticklabels(dt["day_name"],rotation="vertical")
        axis.set_xlabel("Day Name")
        axis.set_ylabel("Number of Count")
        return fig

    def Busy_time_ap(self):
        df=self.df
        fig, axis = plt.subplots()
        A=df["time_range_ap"].value_counts()
        axis=sns.barplot( x=A.index, y=A.values,palette="nipy_spectral_r")
        plt.xticks(rotation="vertical")
        return fig

    def Busy_heatmap(self):
        df=self.df
        fig,axis = plt.subplots()
        dt_pivot=df.pivot_table(index="day_name",columns="time_range_ap",values="messages",aggfunc="count").fillna(0)
        axis=sns.heatmap(dt_pivot)
        return fig



#Message Preprocessing Nearest Friend
def Message_pre_Nearest(df):
       ext=URLExtract()
       list=[]
       for text in df["messages"]:
          text=text.lower()
          text=emoji.replace_emoji(text, replace='')
          url_l=ext.find_urls(text)
          for i in url_l:
                if len(url_l)!=0:
                    text=text.replace(f"{i}","")
          text=re.sub("<media omitted>","",text)
          text=re.sub("www.\w+","",text)
          text=re.sub("\w+@gmail.com","",text)
          if re.findall("-\s",text):
               text=""
          if sum([i in text for i in ["this message was deleted","videocalls","you deleted this message","missed voice call"]]):
                 text=""
          list.append(text)

       sent_list=[]
       for i in list:
         word_list=[]
         for j in i.split():
           if j not in string.punctuation:
              if j not in stopwords.words('english'):
                if j!='<this message edited>':
                   if len(j[2:])>0:
                     word_list.append(j)
         sent_list.append(" ".join(word_list))
       return sent_list
# Nearest user
def Nearest(df,user_name):
     df["messages_preprocess"]=Message_pre_Nearest(df)
     new_data=df[df["messages_preprocess"]!=""]
     new_data=new_data.reset_index()
     model=gensim.models.Word2Vec(vector_size=100,window=3,min_count=1)
     sen_text=[]
     for i in new_data["messages_preprocess"]:
         sen_text.append(i.split())
     model.build_vocab(sen_text)
     model.train(new_data["messages_preprocess"],total_examples=model.corpus_count,epochs=model.epochs)
     sent_vector=[]
     maxlen_l=[]
     for text_l in sen_text:
        text_vector=[]
        for i in text_l:
          text_vector.extend(model.wv[i]/(np.linalg.norm(model.wv[i])))
        sent_vector.append(text_vector)
        maxlen_l.append(len(text_vector))
     ten_l=[]
     for i in sent_vector:
       if len(i)>=500:
         ten_l.append(i[:500])
       else:
         n=500-len(i)
         i.extend(list(np.zeros(n)))
         ten_l.append(i)
     seq=np.array(ten_l)


     def user_vector_m(df):
       user_vector=[]
       user=df["users"].unique().tolist()
       for u in user:
          index=df[df["users"]==u].index
          user_vector.append((seq[index].sum(axis=0))/(seq[index].sum(axis=0)).sum())
       return user,user_vector

     user,user_vector=user_vector_m(new_data)
     kn=NearestNeighbors(n_neighbors=len(user))
     kn.fit(user_vector)
     X=user_name
     index=kn.kneighbors(user_vector[user.index(X)].reshape(1,-1))
     user1=np.array(user)
     return user1[index[1][0].tolist()][1:11]

