#! / usr / bin / python3

import fileinput, csv, pprint, json, team, urllib.request

start_time = time.time ()
pp = pprint.PrettyPrinter (indent = 4)
import unidecode as ud


#_______________Read the official tsv datasets from imdb.com _______________________
print ("read files .......% s"% (time.time () - start_time))
# 1 [titleRatings] ratings file
titleRatings = open ('data / title_ratings.tsv')
readerRatings = csv.DictReader (titleRatings, delimiter = '\ t')

# 2 [titleBasic] basic information file
titleBasic = open ('data / title_basics.tsv', encoding = "utf8")
readerBasic = csv.DictReader (titleBasic, delimiter = '\ t')

# 3 [titlePrincipals] file with information on the main team of a given film, actors, directors and writers
titlePrincipal = open ('data / title_principals.tsv', encoding = "utf8")
readerPrincipal = csv.DictReader (titlePrincipal, delimiter = '\ t')

# 4 [titleCrew] file with directors and writers
titleCrew = open ('data / title_crew.tsv', encoding = "utf8")
readerCrew = csv.DictReader (titleCrew, delimiter = '\ t')


# 6 [names] file with information of each person, actors, directors, writers, etc.
humans = open ('data / name_basics.tsv', encoding = "utf8")
readerHumans = csv.DictReader (humans, delimiter = '\ t')

print ("files read% s"% (time.time () - start_time))
# 0 auxiliary list with the id of all people, actors, directors, writers
humanListAux = set ()


#__________________________ creation of dictionaries____________________________________
# 1 [titleRatings] titles with more than 10,000 votes (but there are titles that are not films)
ratings_dict = {}
for row in readerRatings:
if int (row ['numVotes'])> 10000:
ratings_dict [row ['tconst']] = {'averageRating': row ['averageRating'], 'numVotes': row ['numVotes']}
print ("ratings_dict created |% s"% (time.time () - start_time))

# 2 [titleBasic] titles that are 'movies' key-> idFilme, Values-> 'primaryTitle', 'startYear', 'genres': [string]
basic_dict = {}
for row in readerBasic:
if row ['titleType'] == 'movie':
basic_dict [row ['tconst']] = {'primaryTitle': row ['primaryTitle'], 'startYear': row ['startYear'], 'genres': row ['genres']. split (",") , 'runtimeMinutes': row ['runtimeMinutes']}
#print (basic_dict [row ['tconst']])
print ("basic_dict created |% s"% (time.time () - start_time))

# 3 [titlePrincipals] only the actors. key -> idFilm, Value -> 'actors': ARRAY with the actor and actress, each element is an actor
actor_dict = {}
for row in reader
if row ['category'] == 'actor' or row ['category'] == 'actress':
if row ['tconst'] in actor_dict: #if this movie already exists
actor_dict [row ['tconst']] ['actors']. append (row ['nconst'])
else:
actor_dict [row ['tconst']] = {'actors': [row ['nconst']]}
print ("actor_dict created |% s"% (time.time () - start_time))


# 4 [titleCrew] dictionary with DIRECTORS and WRITERS. key -> idFilm, value -> directors: [string], 'writers': [string]
crew_dict = {}
for row in readerCrew:
crew_dict [row ['tconst']] = {'directors': row ['directors']. split (","), 'writers': row ['writers']. split (",")}
print ("crew_dict created |% s"% (time.time () - start_time))


#UNIAO from basic_dict to ratings_dict.
# get dictionary where the titles 'movies' with more than 10000 votes have the fields 'genres', 'primaryTitle' and 'startYear'
for key, val in basic_dict.items (): # go through basic_dict
if key in ratings_dict: #if the basic_dict title (> 10,000 votes) is in the ratings_dict
ratings_dict [key] ['genres'] = basic_dict [key] ['genres']
ratings_dict [key] ['primaryTitle'] = basic_dict [key] ['primaryTitle']
ratings_dict [key] ['startYear'] = basic_dict [key] ['startYear']
ratings_dict [key] ['runtimeMinutes'] = basic_dict [key] ['runtimeMinutes']
print ("merging basic_dict with created ratings_dict |% s"% (time.time () - start_time))


#clean from the dictionary the titles that have over 10,000 votes, but are not movies. We know that 'movies' have 6 fields
for key in ratings_dict.copy ():
if len (ratings_dict [key]) <6:
del ratings_dict [key]
else:
#acrecent the actors
if key in actor_dict:
ratings_dict [key] ['primaryActors'] = actor_dict [key] ['actors']
#insert these actors into the list of useful people
for actor in ratings_dict [key] ['primaryActors']:
humanListAux.add (actor)
#adding directors and writers
if key in crew_dict:
ratings_dict [key] ['directors'] = crew_dict [key] ['directors']
#insert these directors into the list of useful people
for drctr in ratings_dict [key] ['directors']:
humanListAux.add (drctr)
ratings_dict [key] ['writers'] = crew_dict [key] ['writers']
#insert these writers into the list of useful people
for wrtr in ratings_dict [key] ['writers']:
humanListAux.add (wrtr)
print ("cleared ratings_dict, added actors, directors and writers |% s"% (time.time () - start_time))


# 6 [humans] add with key -> idPessoa, value -> 'primaryName': string, 'birthYear': string, 'deathYear': string, 'primaryProfession': [string], 'knownForTitles': [string]
humans_dict = {}
for row in readerHumans:
#adding only people who are useful
if row ['nconst'] in humanListAux:
humans_dict [row ['nconst']] = {'primaryName': row ['primaryName'], 'birthYear': row ['birthYear'], 'deathYear': row ['deathYear'], 'primaryProfession': row [ 'primaryProfession']. split (","), 'knownForTitles': row ['knownForTitles']. split (",")}
print ("humans_dict created |% s"% (time.time () - start_time))

#removing from titles 'knownForTitle' titles that are not in ratings_dict
for key in humans_dict:
for tit in humans_dict [key] ['knownForTitles']:
if tit not in ratings_dict:
humans_dict [key] ['knownForTitles']. remove (tit)
print ("removed from the 'knownForTitle' field the titles that are not in the ratings_dict |% s"% (time.time () - start_time))



#________writing and creating movies.json file that contains all movies with the fields above, only those from imdb________
json = json.dumps (ratings_dict)
f = open ("movies.json", "w")
f.write (json)
f.close ()

print ("movie.json file created |% s"% (time.time () - start_time))


_______critical and creation of humans.json file that contains the information of everyone listed in movies.json _____________
json = json.dumps (humans_dict)
f = open ("humans.json", "w")
f.write (json)
f.close ()


'''______________________Download all the 'movies' from omdbapi.com and put them in api_movies.json _____________________'''

api_dict = {}

movies = json.load (open ('data / movies.json'))
api_movies = json.load (open ('data / api_movies.json'))

api_aux = set () #contem the ids of the movies already downloaded
for key in api_movies:
api_aux.add (key)

api_key1 = '& apikey = 5aec35de'
api_key2 = '& apikey = ef28afd8'
api_key3 = '& apikey = 2fb13c99'
api_key4 = '& apikey = a1d3e574'

api_key_aux = api_key4

i = 0
j = 0
for key in movies:
if key not in api_aux:
url = 'http://www.omdbapi.com/?i=' + key + api_key_aux
response = urllib.request.urlopen (url)
data = response.read ()
text = data.decode ('utf-8')
d = json.loads (text)
api_dict [d ['imdbID']] = d

print ("movie" + str (j))
i + = 1

if api_key_aux == api_key1:
api_key_aux = api_key2
else:
if api_key_aux == api_key2:
api_key_aux = api_key1
else:
if api_key_aux == api_key3:
api_key_aux = api_key1
j + = 1
if j> 2:
break


if bool (api_dict):
api_movies.update (api_dict)
with open ('data / api_movies.json', 'w') as f:
json.dump (api_movies, f)
else:
print ("over")





"""______________________ ADD FIELDS THAT MISS THE MOVIES.JSON (pick them up at api_movies.json) _______________________________"""


api_movies = json.load (open ('data / api_movies.json'))
movies = json.load (open ('data / movies.json'))
humans = json.load (open ('data / humans.json'))

def boxOfficeToFloat (a):
if a! = 'N / A':
a = a.replace ('$', '')
a = a.replace (',', '')
a = float (a)
return a

for title in movies:
movies [title] ['rated'] = api_movies [title] ['Rated']
movies [title] ['plot'] = api_movies [title] ['Plot']
movies [title] ['poster'] = api_movies [title] ['Poster']
movies [title] ['website'] = api_movies [title] ['Website']
movies [title] ['studio'] = api_movies [title] ['Production']
movies [title] ['boxoffice'] = boxOfficeToFloat (api_movies [title] ['BoxOffice'])
movies [title] ['country'] = api_movies [title] ['Country']. split (',')
movies [title] ['language'] = api_movies [title] ['Language']. split (',')
movies [title] ['genre'] = api_movies [title] ['Genre']. split (',')
movies [title] ['ratings'] = api_movies [title] ['Ratings']

json = json.dumps (movies)
f = open ("movies.json", "w")
f.write (json)
f.close ()

# exchanging iDS with people's names (for EXTRA dataset)
for title in movies:
x = movies [title] .get ("primaryActors", None)
if x! = None:
i = 0
for actor in movies [title] ["primaryActors"]:
movies [title] ["primaryActors"] [i] = humans [actor] ["primaryName"]
i + = 1
x = movies [title] .get ("directors", None)
if x! = None:
j = 0
for actor in movies [title] ["directors"]:
if actor! = '\\ N':
movies [title] ["directors"] [j] = humans [actor] ["primaryName"]
j + = 1
x = movies [title] .get ("writers", None)
if x! = None:
k = 0
for actor in movies [title] ["writers"]:
if actor! = '\\ N':
movies [title] ["writers"] [k] = humans [actor] ["primaryName"]
k + = 1


json = json.dumps (movies)
f = open ("movies.json", "w")
f.write (json)
f.close () 

movies = json.load (open ('data / movies.json'))
for title in movies:
x = movies [title] .get ("language", None)
if x! = None:
i = 0
for genre in movies [title] ["language"]:
movies [title] ["language"] [i] = movies [title] ["language"] [i] .strip ()
i + = 1
x = movies [title] .get ("country", None)
if x! = None:
i = 0
for genre in movies [title] ["country"]:
movies [title] ["country"] [i] = movies [title] ["country"] [i] .strip ()
i + = 1

json = json.dumps (movies)
f = open ("movies.json", "w")
f.write (json)
f.close ()

#_______________________NEW movies.json with ids instead of strings for the Genre, Country, Corporation, Language, mpaaRATE_______________________ fields

movies = json.load (open ('data / movies_ids.json'))

genres = json.load (open ('data / genres.json'))
corporations = json.load (open ('data / corporations.json'))
countries = json.load (open ('data / country.json'))
languages ​​= json.load (open ('data / languages.json'))
mpaa_rate = json.load (open ('data / mpaa_rate.json'))

def getKey (dic, str):
for key in dic:
if dic [key] == str:
return key



for title in movies:

#genres
x = movies [title] .get ("genres", None)
if x! = None:
i = 0
for genre in movies [title] ["genres"]:
movies [title] ["genres"] [i] = getKey (genres, genre)
i + = 1
#corporation
x = movies [title] .get ("corporation", None)
if x! = None:
movies [title] ["corporation"] = getKey (corporations, x)
#countries
x = movies [title] .get ("country", None)
if x! = None:
i = 0
for country in movies [title] ["country"]:
movies [title] ["country"] [i] = getKey (countries, country)
i + = 1
#mpaa_rate
x = movies [title] .get ("mpaa_rate", None)
if x! = None:
movies [title] ["mpaa_rate"] = getKey (mpaa_rate, x)
for title in movies:
#languages
x = movies [title] .get ("language", None)
if x! = None:
i = 0
for lang in movies [title] ["language"]:
movies [title] ["language"] [i] = getKey (languages, lang)
i + = 1


json = json.dumps (movies)
f = open ("movies.json", "w")
f.write (json)
f.close ()


#_____convert value of the different ratings to decimal_______________ (done)


# "ratings": [
# {
# "Source": "Internet Movie Database",
# "Value": "7.5 / 10"
#},
# {
# "Source": "Rotten Tomatoes",
# "Value": "59%"
#},
# {
# "Source": "Metacritic",
# "Value": "48/100"
#}
#]

def conv_IMD (str):
list = str.split ('/')
a = list [0]
return (float (a) /1.0)

def conv_RT (str):
list = str.split ('%')
a = list [0]
return (int (a) /10.0)

def conv_MC (str):
list = str.split ('/')
a = list [0]
return (int (a) /10.0)

for title in movies:
i = 0
for rating in movies [title] ["ratings"]:
if rating ["Source"] == "Internet Movie Database":
value = rating ["Value"]
movies [title] ["ratings"] [i] ["Value"] = conv_IMD (value)
i + = 1
if rating ["Source"] == "Rotten Tomatoes":
value = rating ["Value"]
movies [title] ["ratings"] [i] ["Value"] = conv_RT (value)
i + = 1
if rating ["Source"] == "Metacritic":
value = rating ["Value"]
movies [title] ["ratings"] [i] ["Value"] = conv_MC (value)
i + = 1

json = json.dumps (movies)
f = open ("movies_ids.json", "w")
f.write (json)
f.close ()


#____________________________


dictP = {}
movies = json.load (open ('data / movies_ids.json'))
for key in movies:
dictP [(movies [key] ["primaryTitle"])] = ""

json = json.dumps (dictP)
f = open ("movies.json", "w",)
f.write (json)
f.close ()



