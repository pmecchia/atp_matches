import flask
import pandas as pd




atp_prediction = flask.Flask(__name__, template_folder='templates')


df_matches=pd.read_csv('static/MatchesDay.csv')
#df_matches['ActualRankingP1']=df_matches.ActualRankingP1.astype(int)
#df_matches['ActualRankingP2']=df_matches.ActualRankingP2.astype(int)

@atp_prediction.route('/')
def main():
    return(flask.render_template('main.html',data=df_matches))

if __name__ == '__main__':
    main()
    atp_prediction.run()
