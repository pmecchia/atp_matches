# 🎾 ATP Prediction 
:date: Creation date: March 2021

## 🎯 Objective
Create a web application to predict Association of Tennis Professionals (ATP)  World Tour matches winner. The ATP World Tour is a worldwide top-tier tennis tour for men organized by the Association of Tennis Professionals.

## 🕵️‍♂️ Description

## 🕐 Automation
I failed to make a completely stand-alone application.The reason is that from the Heroku server I couldn't scrape websites I use.

👍
The solution I found was to create an other GitHub repository called "atp-prediction-webapp" for my webapp deployment and enabled automatic deploys on Heroku for a GitHub branch, that means Heroku builds and deploys all pushes to that branch in my atp-prediction-webap repository.

Moreover, I created a python script "scrape.py" making scraping and predictions locally and then push in SSH the excel file "MatchesDay.csv" in my GitHub atp-prediction-webap repository. I converted the python script into an Unix executable called Automation . 

To go further in my automation, I created a real application file instead of a simple Unix executable that I will be able to schedule with the calendar application on Mac. To do it I followed this tutorial <a href="https://martechwithme.com/convert-python-script-app-windows-mac/" target="_blank">https://martechwithme.com/convert-python-script-app-windows-mac/</a>

👎 
The drawback is that my computer should be switch on to upadate my webapp.

## :desktop_computer: How to access ?

Link: <a href="https://atp-prediction.herokuapp.com/" target="_blank">https://atp-prediction.herokuapp.com/</a>
