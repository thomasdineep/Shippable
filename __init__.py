from flask import Flask, render_template, request
import requests, json
from datetime import datetime, timedelta

app = Flask(__name__)

url = ''
count_issues = {}
count_issues['open'] =  0
count_issues['last24hr'] = 0
count_issues['last7days'] = 0

@app.route("/", methods=['GET', 'POST'])
def index():
	
	if request.method == 'POST':
		git_url = request.form.get('url')
		url = get_api_url(git_url) # validate github url

		error = False
		issues = {}

		if url :
			issues['open'] = total_open_issues(url)
			issues['last24hr'] = total_issues_last24hr(url)
			issues['last24hr_7days'] = total_issues_last24hr_7days(url)
			issues['more_7days'] = total_issues_more_7days()
		else :
			error = True

		return render_template('index.html', issues=issues, url=git_url, error=error)

	return render_template('index.html')

# Creating Github API route
def get_api_url(git_url):
	words = git_url.split('/')

	if words[0] == "https:" and words[1] == "" and words[2] == "github.com" and words[3] != "" and words[4] != "" :
   		api = 'https://api.github.com/repos/' + words[3]+ '/' + words[4]
   	else:
   		api = False
	
	return api

# Get open issues
def total_open_issues(url):
	r = requests.get(url)
	response = r.json()
	count_issues['open'] = response['open_issues_count']
	return count_issues['open']

# Get open issues that were opened in the last 24 hours
def total_issues_last24hr(url):
	last24hr = datetime.now() - timedelta(hours = 24)
	last24 = str(last24hr)

 	r = requests.get(url + '/issues?since=' + last24)
	count_issues['last24hr'] = len(r.json())

	return count_issues['last24hr']

# Get opened issues more than 24 hours ago but less than 7 days ago
def total_issues_last24hr_7days(url):
	last7days = datetime.now() - timedelta(days = 7)
	last7days = str(last7days)
 	r = requests.get(url + '/issues?since=' + last7days)
	
	count_issues['last7days'] = len(r.json())
	last24hr_7days = count_issues['last7days'] - count_issues['last24hr']

	return last24hr_7days

# Get open issues that were opened more than 7 days ago 
def total_issues_more_7days():
	more_7days = count_issues['open'] - count_issues['last7days']
	return more_7days		


if __name__ == "__main__":
	app.run()