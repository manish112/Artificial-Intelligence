from pymongo import MongoClient
import pdb

path_weights=[0.5,0.75,1.0]
end_weights=[0.5,1.0,1.5]
time_weights=[0.2,0.2,0.2]
global score_path
global score_end
score_path=0.0
score_end=0.0
overallscore=0.0

client = MongoClient(port=27017)
db=client["product"]
for features in db.features.find({},{"_id":0}):
	print(features['event'])
	feature=features['event']
	db=client["abccorp"]
	operation_score=0.0
	db.overallscore.update({"event":feature,"type":"weighted"},{"$set":{"experience_score":score_path}},upsert=True)
	for x in range(1,4):
		score_path=0.0
		score_end=0.0
		score_time=0.0
		db.overallscore.update({"event":feature,"type":"path","userLevel":x},{"$set":{"experience_score":score_path}},upsert=True)
		db.overallscore.update({"event":feature,"type":"end","userLevel":x},{"$set":{"experience_score":score_path}},upsert=True)
		db.overallscore.update({"event":feature,"type":"time","userLevel":x},{"$set":{"experience_score":score_path}},upsert=True)
		db.overallscore.update({"event":feature,"type":"combined","userLevel":x},{"$set":{"experience_score":score_path}},upsert=True)
		pipeline=[{"$match":{"event":feature,"type":"path","userLevel":x}},{"$group": {"_id":"$event", "sumscore":{"$sum":"$experience"}, "count": {"$sum":1}}},{"$project":{"score":{"$divide":["$sumscore","$count"]}}}]
		for expscore in db.usage.aggregate(pipeline):
			print("score path"+str(x)+":"+str(expscore['score']))
			score_path=expscore['score']
			db.overallscore.update({"event":feature,"type":"path","userLevel":x},{"$set":{"experience_score":score_path}},upsert=True)
		pipeline=[{"$match":{"event":feature,"type":"end","userLevel":x}},{"$group": {"_id":"$event", "sumscore":{"$sum":"$experience"}, "count": {"$sum":1}}},{"$project":{"score":{"$divide":["$sumscore","$count"]}}}]
		for expscore_end in db.usage.aggregate(pipeline):
			print("score end"+str(x)+":"+str(expscore_end['score']))
			score_end=expscore_end['score']
			db.overallscore.update({"event":feature,"type":"end","userLevel":x},{"$set":{"experience_score":score_end}},upsert=True)
		pipeline=[{"$match":{"event":feature,"type":"time","userLevel":x}},{"$group": {"_id":"$event", "sumscore":{"$sum":"$experience"}, "count": {"$sum":1}}},{"$project":{"score":{"$divide":["$sumscore","$count"]}}}]
		for expscore_time in db.usage.aggregate(pipeline):
			print("score time"+str(x)+":"+str(expscore_time['score']))
			score_time=expscore_time['score']
			db.overallscore.update({"event":feature,"type":"time","userLevel":x},{"$set":{"experience_score":score_time}},upsert=True)
		#pdb.set_trace()
		print("score path"+str(score_path)+"score end"+str(score_end))
		feature_score=(score_path*path_weights[x-1])+(score_path*end_weights[x-1])+(score_time*time_weights[x-1])
		operation_score+=feature_score
		r=db.overallscore.update({"event":feature,"type":"combined","userLevel":x},{"$set":{"experience_score":feature_score}},upsert=True)
		print(r)
	overallscore+=operation_score
	db.overallscore.update({"event":feature,"type":"weighted"},{"$set":{"experience_score":operation_score}},upsert=True)
db.overallscore.update({"type":"overallscore"},{"$set":{"experience_score":overallscore}},upsert=True)
customer_mood=""
if overallscore>1.0:
	customer_mood="Extremely Happy"
elif overallscore>0.7 and overallscore<=1.0:
	customer_mood="Happy"
elif overallscore>-0.7 and overallscore<=0.7:
	customer_mood="Neutral"
elif overallscore>-1.0 and overallscore<=-0.7:
	customer_mood="Disappointed"
else:
	customer_mood="Sad"
print("The customer mood is "+customer_mood)
db.overallscore.update({"type":"customermood"},{"$set":{"mood":customer_mood}},upsert=True)
