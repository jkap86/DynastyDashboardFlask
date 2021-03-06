from flask import Flask, render_template, request, redirect, url_for, jsonify, session 
from flask_session import Session
from flask_bootstrap import Bootstrap
import requests
import json
import datetime
from operator import itemgetter
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField
from wtforms.validators import DataRequired, AnyOf
import functools



app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)
Bootstrap(app)
app.config['SECRET_KEY'] = "1111" 

def getUsername(userID):
	url = requests.get('https://api.sleeper.app/v1/user/' + str(userID))
	url = url.json()
	return url['username']

def getUserIDfromUsername(username):
	url = requests.get('https://api.sleeper.app/v1/user/' + username)
	userID = url.json()['user_id']
	return userID

def getUserIDfromRosterID(rosterID, rosters):
	for roster in rosters:
		if roster['roster_id'] == rosterID:
			return roster['owner_id']

def getLeagues(username):
	userID = getUserIDfromUsername(username)
	leagues = requests.get('https://api.sleeper.app/v1/user/' + userID + '/leagues/nfl/2021')
	leagues = leagues.json()
	return leagues

def getRosters(league):
	rosters = requests.get('https://api.sleeper.app/v1/league/' + league['league_id'] + '/rosters')
	rosters = rosters.json()
	return rosters

def getTransactions(league):
	transactions = requests.get('https://api.sleeper.app/v1/league/' + league['league_id'] + '/transactions/1')
	transactions = transactions.json()
	return transactions

def getAvatar(username):
	x = requests.get('https://api.sleeper.app/v1/user/' + username)
	avatarID = x.json()['avatar']
	avatar = 'https://sleepercdn.com/avatars/' + avatarID
	return avatar

def getAvatarThumb(username):
	x = requests.get('https://api.sleeper.app/v1/user/' + username)
	avatarID = x.json()['avatar']
	avatarThumb = 'https://sleepercdn.com/avatars/thumbs/' + avatarID 
	return avatarThumb    



class ViewLeaguesForm(FlaskForm):
	username = StringField('username', [DataRequired()], render_kw={'placeholder': 'username', 'class': 'form'})

class ViewCommonForm(FlaskForm):
	leaguemateName = StringField('username', [DataRequired()], render_kw={'placeholder': 'username', 'class': 'form'})
	leaguemateName2 = StringField('leaguemateName', [DataRequired()], render_kw={'placeholder': 'leaguemate name', 'class': 'form'})

class ViewTransactions(FlaskForm):
	username3 = StringField('username3', [DataRequired()], render_kw={'placeholder': 'username', 'class': 'form'})

class ViewAllLeaguemates(FlaskForm):
	username2 = StringField('username2', [DataRequired()], render_kw={'placeholder': 'username', 'class': 'form'})

class PlayerSearch(FlaskForm):
	username4 = StringField('username4', [DataRequired()], render_kw={'placeholder': 'username', 'class': 'form'})
	playerSearch = StringField('playerSearch', [DataRequired()], render_kw={'placeholder': 'player', 'class': 'form'})

@app.route('/', methods=['POST', 'GET'])
def index():
	username = request.form.get('username')
	username2 = request.form.get('username2')
	username3 = request.form.get('username3')
	username4 = request.form.get('username4')
	playerSearch = request.form.get('playerSearch')
	leaguemateName = request.form.get('leaguemateName')
	leaguemateName2 = request.form.get('leaguemateName2')
	allPlayers = open('allplayers.txt', 'r')
	allPlayers = allPlayers.read()
	allPlayers = json.loads(allPlayers)
	players = []
	allPlayersKeys = list(allPlayers.keys())
	session['allPlayers'] = allPlayers
	session['username'] = username
	favTeam = request.form.get("team")
	if request.form.get('submitButton') == 'view-transactions':
		return redirect(url_for('transactions', username=username3))
	elif request.form.get('submitButton') == 'submit':
		return redirect(url_for('info', username=username))
	elif request.form.get('submitButton') == 'view-common-leagues':
		return redirect(url_for('leaguemates', leaguemateName=leaguemateName, leaguemateName2=leaguemateName2))
	elif request.form.get('submitButton') == 'view-all-leaguemates':
		return redirect(url_for('leaguematesAll', username=username2))
	elif request.form.get('submitButton') == 'view-player-search':
		return redirect(url_for('playerSearchResults', username=username4, playerSearch=playerSearch))
	else:
		form = ViewLeaguesForm(request.form)
		form2 = ViewCommonForm(request.form)
		form3 = ViewTransactions(request.form)
		form4 = ViewAllLeaguemates(request.form)
		form5 = PlayerSearch(request.form)
		favTeam = request.form.get("team")
		for key in allPlayersKeys:
			players.append(allPlayers[key])

	return render_template('index.html', allPlayers=players, favTeam=favTeam or 'was', form=form, form2=form2, form3=form3, form4=form4, form5=form5)

@app.route('/info/<username>', methods=["POST", "GET"])
@functools.lru_cache(maxsize=128)
def info(username):
	username = username.strip()
	leagueID = request.form.get('submitLeagueID')
	if request.method == 'POST':
		username = session.get('username')
		if leagueID != None:
			return redirect(url_for('roster', leagueID=leagueID, username=username))
	else:
		leagues = getLeagues(username)
		userID = getUserIDfromUsername(username)
		x = requests.get("https://api.sleeper.app/v1/user/" + userID)
		avatarID = x.json()['avatar']
		pwins = 0
		plosses = 0
		for league in leagues:
			rosters = getRosters(league)
			for roster in rosters:
				if roster['owner_id'] == userID:
					if roster['metadata']:
						if 'record' in roster['metadata'].keys():
							record = roster['metadata']['record']
							pwins = pwins + record.count('W')
							plosses = plosses + record.count('L')
					

	return render_template('info.html', username=username, leagues=leagues, leaguesCount=len(leagues), pwins=pwins, plosses=plosses, avatar="https://sleepercdn.com/avatars/" + avatarID, favTeam=session.get('fav-team'))

@app.route('/transactions/<username>')
@functools.lru_cache(maxsize=128)
def transactions(username):
	username = username.strip()
	allPlayers = session.get('allPlayers')
	transactionsAll = []
	userID = getUserIDfromUsername(username)
	for league in getLeagues(username):
		rosters = getRosters(league)
		transactions = getTransactions(league)
		rosterIDList = list(filter(lambda x:x['owner_id'] == userID, rosters)) or ""
		for ID in rosterIDList:
			rosterID = ID
		try:
			for transaction in list(filter(lambda x:int(rosterID['roster_id']) in x['roster_ids'], transactions)):	
				transaction['status_updated'] = datetime.datetime.fromtimestamp(transaction['status_updated']/1000).strftime('%Y-%m-%d %H:%M:%S')
				userKey = {}
				draftPicks = list(filter(lambda x:x['roster_id'], transaction['draft_picks']))
				for draftPick in draftPicks:
					userKey[draftPick['roster_id']] = getUsername(getUserIDfromRosterID(draftPick['roster_id'], rosters))
				transactionsAll.append({'transaction':transaction, 'league':league['name'], 'status':transaction['status'], 'date':transaction['status_updated'], 'roster-id':rosterID['roster_id'], 'draft-pick-count':len(transaction['draft_picks']), 'userKey':userKey })
		except NameError:
			pass
	return render_template('transactions.html', username=username, allPlayers=allPlayers, transactionsAll=transactionsAll)

@app.route('/leaguemates/<leaguemateName>/<leaguemateName2>', methods=["POST", "GET"])
@functools.lru_cache(maxsize=128)
def leaguemates(leaguemateName, leaguemateName2):
	leaguemateName = leaguemateName.strip()
	leaguemateName2 = leaguemateName2.strip()
	commonLeagues = []
	favTeam = session.get('fav-team')
	if request.method == 'POST':
		return redirect(url_for('roster', username=request.form.get('submitLeaguemateName'), leagueID=request.form.get('submitLeagueID')))	

	else:
		leaguemateLeagues = getLeagues(leaguemateName)
		leaguemateLeagues2 = getLeagues(leaguemateName2)
		for i in range(0, len(leaguemateLeagues)):
			for j in range(0, len(leaguemateLeagues2)):
				if leaguemateLeagues[i]['league_id'] == leaguemateLeagues2[j]['league_id']:
					commonLeagues.append(leaguemateLeagues[i])
	return render_template('leaguemates.html', leaguemateName=leaguemateName, leaguemateName2=leaguemateName2, commonLeagues=commonLeagues, commonLeaguesCount=len(commonLeagues), favTeam=favTeam)

@app.route('/leaguemates/<username>/all', methods=["POST", "GET"] )
@functools.lru_cache(maxsize=128)
def leaguematesAll(username):
	username = username.strip()
	leaguemates = []
	avatarThumbs = {}
	if request.method == 'POST':
		leaguemateName = request.form.get("submitUsername")
		if request.form['submitUsername'] != None:
			return redirect(url_for('leaguematesAll', username=leaguemateName))
	else:
		for league in getLeagues(username):
			usersLeague = requests.get('https://api.sleeper.app/v1/league/' + league['league_id'] + '/users')
			for user in usersLeague.json():
				leaguemates.append({'user-id': user['display_name'], 'league': league['name']})
				if user['avatar']:
					avatarThumbs[user['display_name']] = 'https://sleepercdn.com/avatars/thumbs/' + user['avatar']
		myDict = {}
		for d in leaguemates:
			c = d['user-id']
			myDict[c] = myDict.get(c,0)+1
	avatar = getAvatar(username)
			
	return render_template('leaguematesAll.html', username=username, leaguematesDict=myDict, avatar=avatar, avatarThumbs=avatarThumbs)

@app.route('/<username>/<playerSearch>')
@functools.lru_cache(maxsize=128)
def playerSearchResults(username ,playerSearch):
	username = username.lower().strip()
	allPlayers = session.get('allPlayers')
	leaguesPlayers = []
	leaguesWith = {}
	leaguesOwned = []
	leagues = getLeagues(username)
	pwins = 0
	plosses = 0
	for league in leagues:
		rosters = getRosters(league)
		ownerName = 'Available'
		for roster in rosters:
			players = roster['players']
			if players != None:
				leaguesPlayers.append(players)
				for lp in players:
					try:
						if playerSearch == " ".join([allPlayers[lp]['first_name'], allPlayers[lp]['last_name'], allPlayers[lp]['position'], str(allPlayers[lp]['team'])]):
							ownerID = roster['owner_id']
							info = requests.get('https://api.sleeper.app/v1/user/' + str(ownerID))
							ownerName = info.json()['username']
							if lp in roster['starters']:
								leaguesWith[league['name']] = [ownerName, 'starter']
							else:
								leaguesWith[league['name']] = [ownerName, 'bench']
							if ownerName == username:
								leaguesOwned.append(league['name'])
								if roster['metadata']:
									if 'record' in roster['metadata'].keys():
										record = roster['metadata']['record']
										pwins = pwins + record.count('W')
										plosses = plosses + record.count('L')
					except KeyError:
						pass
		if ownerName == 'Available':
			leaguesWith[league['name']] = ownerName	

	return render_template('playerSearchResults.html', playerSearch=playerSearch, username=username, leaguesCount=len(leaguesOwned), leaguesOwned=leaguesOwned, leaguesList=leaguesWith, pwins=pwins, plosses=plosses)

@app.route('/roster/<username>/<leagueID>', methods=["POST", "GET"])
@functools.lru_cache(maxsize=128)
def roster(leagueID, username):
	allPlayers = session.get('allPlayers')
	userID = getUserIDfromUsername(username)
	league = requests.get("https://api.sleeper.app/v1/league/" + leagueID)
	league = league.json()
	leagueName = league['name']
	rosters = requests.get('https://api.sleeper.app/v1/league/' + leagueID + '/rosters')
	rosters = rosters.json()
	leaguemates = []
	for roster in rosters:
		x = requests.get("https://api.sleeper.app/v1/user/" + roster['owner_id'])
		avatarID = x.json()['avatar']
		if roster['owner_id'] == userID:
			players = roster['players'] or []
			wins = roster['settings']['wins']
			losses = roster['settings']['losses']
			ties = roster['settings']['ties']
			if roster['metadata']:	
				record = roster['metadata']['record']
				pwins = record.count('W')
				plosses = record.count('L')
			else:
				pwins = "n/a"
				plosses = "Inaugural Season"
		else:
			leaguemates.append([getUsername(roster['owner_id']), avatarID])
	playersNames = []
	for player in players:
		try:
			playersNames.append(allPlayers[player]['position'] + " " + allPlayers[player]['first_name'] + " " + allPlayers[player]['last_name'] + " " + allPlayers[player]['team'])
		except KeyError:
			pass
		except TypeError:
			pass
	playersNames.sort()
	return render_template('roster.html', leagueName=leagueName, teamName=username, players=playersNames, playerCount=len(playersNames), leaguemates=leaguemates, wins=wins, losses=losses, ties=ties, pwins=pwins, plosses=plosses, leagueID=leagueID)
