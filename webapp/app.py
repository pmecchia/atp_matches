import flask
import pandas as pd

app = flask.Flask(__name__, template_folder='templates')

df_matches=pd.read_csv('../MatchesDay.csv')
df_matches['ActualRankingP1']=df_matches.ActualRankingP1.astype(int)
df_matches['ActualRankingP2']=df_matches.ActualRankingP2.astype(int)


#df_matches=df_matches[["NewNameP1","ActualRankingP1","AvgP1","NewNameP2","ActualRankingP2","AvgP2","PhotoP1","PhotoP2","Hei"]]
#df_matches.columns = df_matches.iloc[0]
#df_matches = df_matches[1:]
@app.route('/')


def main():

    return(flask.render_template('main.html',data=df_matches))

if __name__ == '__main__':

    app.run()
