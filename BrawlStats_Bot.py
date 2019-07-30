import requests
import json
import praw
import pdb
import re
import os

reddit = praw.Reddit('bot1');
headers = {
    'Authorization': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkaXNjb3JkX3VzZXJfaWQiOiIxNjc2NDY5NTM2NzEzNjA1MTIiLCJpYXQiOjE1NTM2NTMyMDR9.3KRaygmXTr0soPLG74Mfwa9Phze_N5jcOfJfa7wlYnw"
    }
# ERROR CODES:
# -1 = 404 page not found
# -2 = no string following script call
#TODO: try catch instead of error codes



# returns the json dict (player)
def getPlayer(id):
	if id < 0:
		return id
	url = "https://brawlapi.cf/api/player?tag=" + id
	response = requests.request("GET", url, headers=headers)
	if response.status_code == 404:
		return -1
	data = response.json()
	return data

# returns the json dict (club)
def getClub(id):
	if id < 0:
		return id
	url = "https://brawlapi.cf/api/club?tag=" + id
	response = requests.request("GET", url, headers=headers)
	if response.status_code == 404:
		return -1
	data = response.json()
	return data


# returns the comment to reply with (player)
def createPlayerComment(data):
	if data == -1:
		return "Hmm I don't think this player exists"
	elif data == -2:
		return "Hmm could not find a tag to search"
	else:
		reply = "##Brawl Stats for Player: " + data["name"] + " (#" + data["tag"] + ")"
		reply+= "\n\n***"
		reply+= "\n\n**Trophy Record:** " + str(data["highestTrophies"])
		reply+= "\n\n**Current Trophies:** " + str(data["trophies"])
		reply+= "\n\n**Solo Wins:** " + str(data["soloShowdownVictories"])
		reply+= "\n\n**Duo Wins:** " + str(data["duoShowdownVictories"])
		reply+= "\n\n**3v3 Wins:** " + str(data["victories"])
		reply+=" \n\n**Brawlers Unlocked:** " + str(data["brawlersUnlocked"])
		reply+= "\n\n**Average Trophies/Brawler:** " + str(round(data["trophies"]/data["brawlersUnlocked"],1))
		reply+= "\n\n**Club:** " + data["club"]["name"] + " (#" + data["club"]["tag"] + ")"
		return reply

# returns the comment to reply with (club)
def createClubString(data):
	if data == -1:
		return "Hmm I don't think this club exists"
	elif data == -2:
		return "Hmm could not find a tag to search"
	else:
		reply = "##Brawl Stats for Club: " + data["name"] + " (#" + data["tag"] + ") "
		reply+= "\n\n***"
		reply+= "\n\n**Trophies:** " + str(data["trophies"])
		reply+= "\n\n**Members:** " + str(data["membersCount"]) + "/100"
		reply+= "\n\n**Status:** " + data["status"]
		reply+= "\n\n**Required Trophies:** " + str(data["requiredTrophies"])
		return reply
		

# returns the tag eg: P3QYGG (no)te without '#')
def getTagSubstring(body):
	tokenized = body.split(" ")
	tokenCounter = 0
	tag = ""
	for substring in tokenized:
		if re.search("!playerStats",substring, re.IGNORECASE):
			if tokenCounter+1 >= len(tokenized):
				return -2
			tag = tokenized[tokenCounter+1]
		tokenCounter+=1
	return re.sub("#", "", tag) #remove '#' if exists.



if not os.path.isfile("replied.txt"):
	replied = []
else:
	with open("replied.txt","r") as f:
		replied = f.read()
		replied = replied.split("\n")
		replied = list(filter(None, replied))

subreddit = reddit.subreddit('pythonforengineers')
for submission in subreddit.new(limit=5):
	for comment in submission.comments:
		if comment.id not in replied:
			if re.search("!playerStats", comment.body, re.IGNORECASE):
				tagRequest = getTagSubstring(comment.body);
				comment.reply(createPlayerComment(getPlayer(tagRequest)))
				print("replying to: " , comment.id)
				replied.append(comment.id);

			elif re.search("!clubStats", comment.body, re.IGNORECASE):
				comment.reply(createClubString(getClub(getTagSubstring(comment.body))))
				print("replying to: " , comment.id)
				replied.append(comment.id)

with open("replied.txt", "w") as f:
    for post_id in replied:
    	f.write(post_id + "\n")
