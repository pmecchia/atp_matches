import flask
import pandas as pd
import numpy as np
import datetime
#from tensorflow.keras.models import load_model
#from keras.models import load_model
#from tensorflow import keras
#from keras.models import load_model
import tensorflow as tf
import pickle
import re
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from git import Repo


PATH_OF_GIT_REPO = r'/Users/pierremecchia/Documents/Documents/machine_learning/projects/tennis_betting/webapp'  # make sure .git folder is properly configured

COMMIT_MESSAGE = 'Update MatchesDay.csv'

def git_push():
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add(update=True)
        repo.index.commit(COMMIT_MESSAGE)
        repo.git.push("origin", "master")
    except:
        print('Some error occured while pushing the code')



#model_MLP=load_model('model/model_MLP.h5')
#model_MLP=models.load_model('model')
#model_MLP = keras.models.load_model('model/model_MLP')
model_MLP = tf.keras.models.load_model(r'/Users/pierremecchia/Documents/Documents/machine_learning/projects/tennis_betting/model/model_MLP')
df_selected_players = pd.read_pickle(r'/Users/pierremecchia/Documents/Documents/machine_learning/projects/tennis_betting/dataframes/df_selected_players.pkl')

# Load data (deserialize)
with open(r'/Users/pierremecchia/Documents/Documents/machine_learning/projects/tennis_betting/dataframes/label_dictionnary.pkl', 'rb') as handle:
    label_dictionnary = pickle.load(handle)

def checkName(Name):
    if '..' in Name:
        Name=Name.replace('..','.')
    else:
        Name=Name

    if '. ' in Name:
        Name=Name.replace('. ','.')
    else:
        Name=Name

    length=len(Name)
    if Name[length-1]!='.':
        Name=Name+'.'
    else:
        Name=Name
    return Name

def PlayerSyntax(playerName):

    playerName=checkName(playerName)#first syntax check for dots

    char_positions=[pos for pos, char in enumerate(playerName) if char == "-"] #array of character position in string
    if char_positions: ##  if not empty array
        for i in char_positions:
            if playerName[i-1].isupper(): #check if the character before is an uppercase
                #convert to list in order to change specific character
                new=list(playerName)
                new[i]="."
                playerName="".join(new)

    if playerName == "Kwon Soonwoo":
        playerName="Kwon S."
    elif playerName == "Ramos A.":
        playerName="Ramos-Vinolas A."
    elif playerName=="McDonald M.":
        playerName="Mcdonald M."
    elif playerName=="Galan Riveros D.E.":
        playerName="Galan D.E."

    return playerName

def DayMatches():
    #############################################################################
    ## Scrape Location, Players, Odds and Winner of each ATP matches of the day ##
    #############################################################################

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    url_odds="https://www.oddsportal.com/matches/tennis/"

    driver = webdriver.Chrome(executable_path=r'/Users/pierremecchia/Desktop/chromedriver',options=chrome_options)
    driver.get(url_odds)

    sleep(3)

    table=driver.find_elements_by_xpath("//*[@id='table-matches']/table/tbody/tr[contains(@class,'dark')]")

    list_href=[]
    list_location=[]
    list_player1=[]
    list_player2=[]
    list_odd1=[]
    list_odd2=[]
    list_winnerP1=[]

    ## find all ATP tournament and keep their link
    for row in table:
        if ("ATP" in row.text) and (not "Doubles" in row.text): #only interested in single atp matches
            href=row.find_element_by_xpath('./th[1]/a[2]').get_attribute('href')
            if href not in list_href:
                list_href.append(href)
    driver.quit()


    for href in list_href:

        driver = webdriver.Chrome(executable_path=r'/Users/pierremecchia/Desktop/chromedriver',options=chrome_options)
        #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=chrome_options)
        driver.get(href)
        sleep(3)
        ##find location of the atp tournament
        h1=driver.find_element_by_xpath('//*[@id="col-content"]/h1').text

        #clean location string
        location=h1.replace('Betting Odds','')
        location=location.replace('ATP ','')
        location=re.sub(r'\([^)]*\)', '', location)#delete special characters
        location=location.rstrip().lstrip() #delete white space at the beginning and end of string
        if location =='French Open':
            location='Paris'

        matches=driver.find_elements_by_xpath("//*[@id='tournamentTable']/tbody/tr") #List of matches in the tournament
        doScrap=False
        for match in matches:
            try:
                className=match.get_attribute("class")
                if className=='center nob-border': #create a counter in order to scrape only matches of the day
                    date=match.find_element_by_xpath('./th[1]/span').text
                    if 'Today' in date:
                        doScrap=True
                    else:
                        doScrap=False
                if doScrap==True:
                    if not('dark' or 'nob-border' or 'table-dummyrow')in className:

                        try:
                            if 'deactivate' in className: #for matches completed or currently playing (live matches)
                                players=match.find_element_by_xpath('./td[2]/a').text

                                if players=="": #append for live matches
                                    players=match.find_element_by_xpath('./td[2]/a[2]').text

                                #find odds
                                odd1=match.find_element_by_xpath('./td[4]/a').text
                                odd1_className=match.find_element_by_xpath('./td[4]').get_attribute("class")

                                odd2=match.find_element_by_xpath('./td[5]/a').text
                                odd2_className=match.find_element_by_xpath('./td[5]').get_attribute("class")

                                #find winner of the match
                                winnerP1=match.find_element_by_xpath('./td[3]').text

                                if ("ret" in winnerP1) : #no winner for retirement matches
                                    winnerP1=2
                                elif ("canc" in winnerP1): #no winner for canceled
                                    winnerP1=3
                                elif (("result-ok" not in odd1_className) & ("result-ok" not in odd2_className)): #match not finished
                                    winnerP1=np.nan
                                elif int(winnerP1[0])<int(winnerP1[2]):
                                    winnerP1=0
                                else:
                                    winnerP1=1
                            else: # for matches not played yet
                                players=match.find_element_by_xpath('./td[2]/a[not(contains(@class,"ico-tv-tournament"))]').text
                                odd1=match.find_element_by_xpath('./td[3]/a').text
                                odd2=match.find_element_by_xpath('./td[4]/a').text
                                winnerP1=np.nan

                            #Clean players names
                            player1=players.split(" - ")[0]
                            player1=PlayerSyntax(player1)
                            player2=players.split(" - ")[1]
                            player2=PlayerSyntax(player2)


                            list_location.append(location)
                            list_player1.append(player1)
                            list_player2.append(player2)
                            list_odd1.append(odd1)
                            list_odd2.append(odd2)
                            list_winnerP1.append(winnerP1)

                        except :
                            continue

            except NoSuchElementException:
                continue

        driver.quit()

    dictionnary={"Location":list_location,"Player1":list_player1,"Player2":list_player2,"AvgP1":list_odd1,"AvgP2":list_odd2,"P1Winner":list_winnerP1} #create a dictionnary
    df_matchs=pd.DataFrame(dictionnary) #convert dictionnary into pandas dataframe

    return df_matchs


def TournamentsData(locations_list):

    ##################################################################################
    ## Scrape Series, Surface and Court of tournaments present in the locations_list ##
    ##################################################################################

    chrome_options=webdriver.ChromeOptions()

    url_tourn="https://www.atptour.com/en/tournaments/"

    driver = webdriver.Chrome(executable_path=r'/Users/pierremecchia/Desktop/chromedriver')
    driver.get(url_tourn)
    sleep(4)

    list_series=[]
    list_court=[]
    list_location=[]
    list_surface=[]


    #list all tournaments in the current month

    month_tournament=driver.find_elements_by_xpath("//*[@id='contentAccordionWrapper']/div[contains(@class,'expand')][1]/div[2]/div/table/tbody/tr")

    #tournaments from previous month, needed for tournaments played on two months

    previous_month_tournament=driver.find_elements_by_xpath("//*[@id='contentAccordionWrapper']/div[not(contains(@class,'expand'))]")
    last_month=len(previous_month_tournament)-1
    previous_month_tournament=driver.find_elements_by_xpath("//*[@id='contentAccordionWrapper']/div[%d]/div[2]/div/table/tbody/tr"%last_month)

    list_tournaments=previous_month_tournament+month_tournament #current and previous mounth tournaments

    for tournament in list_tournaments:
        try:
            #scrape location for each tournament in the list
            location=tournament.find_element_by_xpath('./td[2]/span[1]')
            location=location.get_attribute("innerText")
            town=location.split(",")[0]

            if town in locations_list: #identify tournaments that we have to scrape
                date=tournament.find_element_by_xpath('./td[2]/span[2]')
                date=date.get_attribute("innerText")
                end_date=date.split(" - ")[1] #end tournament date
                start_date=date.split(" - ")[0]
                now = datetime.datetime.now().date() #today date
                end_date=datetime.datetime.strptime(end_date, "%Y.%m.%d").date() #datetime format
                start_date=datetime.datetime.strptime(start_date, "%Y.%m.%d").date() #datetime format
                if end_date >= now >= start_date: #check if tournament is currently being played
                    try:
                        #define the serie of the tournament thanks to the image source
                        series=tournament.find_element_by_xpath('./td[1]/img').get_attribute("src")
                        if "250.png" in series:
                            series="ATP250"
                        elif "500.png" in series:
                            series="ATP500"
                        elif "1000.png" in series:
                            series="Masters 1000"
                        elif "grandslam.png" in series:
                            series="Grand Slam"
                        elif "finals.svg" in series:
                            series="ATP Finals"
                        else:
                            series=np.nan
                    except:
                        series=np.nan
                    try:
                        #scrape court and surface of the tournament
                        playground=tournament.find_element_by_xpath('./td[3]/table/tbody/tr/td[2]/div/div')
                        playground=playground.get_attribute("innerText")
                        playground=playground.split(" ")
                        court=playground[0]
                        surface=playground[1]

                    except:
                        court=np.nan
                        surface=np.nan


                    list_series.append(series)
                    list_surface.append(surface)
                    list_court.append(court)
                    list_location.append(town)

        except:
            continue
    driver.quit()

    loc_dict={"Location":list_location,"Series":list_series,"Court":list_court,"Surface":list_surface} #create a dictionnary
    df_tournaments=pd.DataFrame(loc_dict) # convert dictionnary into pandas dataframe
    print(loc_dict)
    return df_tournaments


def PlayerNotFound(Player,df_selected_players):
    if Player not in (df_selected_players["NewName"]):
        firstName=Player.split(" ")[-1]
        Name=" ".join(Player.split(" ")[0:-1])

        if df_selected_players["NewName"].str.contains(Name+" "+firstName[0]).any():
            similarPlayer=[]
            i=0
            while len(similarPlayer) != 1:
                similarPlayer=df_selected_players["NewName"][df_selected_players["NewName"].str.contains(Name+" "+firstName[0:i+1])].reset_index(drop=True)
                i+=1
                if i==len(firstName):
                    similarPlayer=Player
                    break
            Player=similarPlayer
        elif df_selected_players["NewName"].str.contains(Name.replace("-"," ")+" "+firstName[0]).any():
            similarPlayer=[]
            i=0
            while len(similarPlayer) != 1:
                similarPlayer=df_selected_players["NewName"][df_selected_players["NewName"].str.contains(Name.replace("-"," ")+" "+firstName[0:i+1])].reset_index(drop=True)
                i+=1
                if i==len(firstName):
                    similarPlayer=Player
                    break
            Player=similarPlayer
        elif df_selected_players["NewName"].str.contains(Name.split("-")[0]+" "+firstName[0]).any():
            similarPlayer=[]
            i=0
            while len(similarPlayer) != 1:
                similarPlayer=df_selected_players["NewName"][df_selected_players["NewName"].str.contains(Name.split("-")[0]+" "+firstName[0:i+1])].reset_index(drop=True)
                i+=1
                if i==len(firstName):
                    similarPlayer=Player
                    break
            Player=similarPlayer
        else:
            Player=Player

    return Player


def Validation_Labelizer(df):
    dict_idx=0
    for idx,column in enumerate(df):

        if df[column].dtype==object:
            df.iloc[:,idx]=df.iloc[:,idx].map(label_dictionnary[dict_idx])
            dict_idx+=1
    return df


def data():
    df_matchs=DayMatches() #Scrape atp matches of the day
    locations_list=df_matchs['Location'].unique() #location list of tournaments of the day
    df_tournaments=TournamentsData(locations_list) # scrape additionnals datas of the tournaments of the day
    df_validation=df_matchs.merge(df_tournaments,on="Location") #merge
    df_validation['Player1']=df_validation.apply(lambda x: PlayerNotFound(x["Player1"],df_selected_players),axis=1)
    df_validation['Player2']=df_validation.apply(lambda x: PlayerNotFound(x["Player2"],df_selected_players),axis=1)


    df_validation=df_validation.merge(df_selected_players,left_on='Player1',right_on="NewName", how='left',suffixes=['P2','P1']) #first merge for winner player
    df_validation=df_validation.merge(df_selected_players,left_on='Player2',right_on="NewName", how='left',suffixes=['P1','P2'])#second merge for loser player
    df_validation=df_validation.drop(['FirstNameP1','FirstNameP2','NameP1','NameP2',"AtpIdP1","AtpIdP2","AtpNameP1","AtpNameP2"],axis=1) # drop useless features
    df_validation=df_validation[['Location','Player1','Player2','Series', 'Court', 'Surface', 'ActualRankingP1', 'ActualRankingP2', 'AvgP1', 'AvgP2','HeightP1', 'HandednessP1', 'NewNameP1', 'IdP1','PhotoP1', 'HeightP2', 'HandednessP2', 'NewNameP2', 'IdP2','PhotoP2','P1Winner']]#ordering columns

    df_html=df_validation.copy()

    df_validation=df_validation.drop(["Player1","Player2","NewNameP1","NewNameP2","PhotoP1","PhotoP2"],axis=1) # features already present in idP1 and idP2
    df_validation['AvgP1']=df_validation.AvgP1.astype(float)#convert column to float
    df_validation['AvgP2']=df_validation.AvgP2.astype(float)#convert column to float
    df_validation=df_validation[df_validation['IdP1'].notna()&df_validation['IdP2'].notna()&df_validation['ActualRankingP1'].notna()&df_validation['ActualRankingP2'].notna()] #keep rows without NaN values in Id columns
    df_validation=Validation_Labelizer(df_validation) #Labelizer
    X_validation=df_validation.drop(['P1Winner'],axis=1)
    df_validation["Prediction"]=model_MLP.predict(X_validation)

    df_html=df_html[df_html['IdP1'].notna()&df_html['IdP2'].notna()&df_html['ActualRankingP1'].notna()&df_html['ActualRankingP2'].notna()] #keep rows without NaN values in Id columns
    df_html['PredictP1']=df_validation['Prediction']
    df_html['ActualRankingP1']=df_html.ActualRankingP1.astype(int)
    df_html['ActualRankingP2']=df_html.ActualRankingP2.astype(int)
    print(df_html)
    return df_html

dataframe_app=data()
dataframe_app.to_csv(r'/Users/pierremecchia/Documents/Documents/machine_learning/projects/tennis_betting/webapp/MatchesDay.csv',index=False)
git_push()
