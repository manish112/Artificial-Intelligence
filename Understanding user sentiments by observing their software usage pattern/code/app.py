from flask import Flask, render_template
from flask import request
from flask import jsonify
from keras.preprocessing import image
import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import os
import uuid
import json
from pymongo import MongoClient
client = MongoClient(port=27017) 
app = Flask(__name__)

event_time={
"edit_assignprofile":2000,
"edit_fill":1600,
"edit_preferences_cameraraw":1500,
"edit_preferences_general":1600,
"edit_preferences_tools":2000,
"edit_transform_distort":2200,
"edit_transform_rotate":2500,
"edit_transform_scale":3000,
"edit_transform_skew":2600,
"file_close":1200,
"file_new_newfile":1500,
"file_new_newproject":1400,
"file_open_openfile":1400,
"file_open_openproject":1600,
"file_properties":1100,
"file_save":1000,
"filter_blur_average":2600,
"filter_blur_gaussianblur":2500,
"filter_blur_lensblur":2400,
"filter_blur_radialblur":2200,
"filter_distort_displace":2600,
"filter_distort_pinch":1800,
"filter_distort_twirl":1900,
"filter_noise_addnoise":1600,
"filter_noise_diffusenoise":1700,
"filter_noise_reducenoise":1900,
"filter_stylize_diffuse":1600,
"filter_stylize_emboss":2000,
"filter_stylize_oilpaint":2200,
"filter_stylize_tiles":2300,
"filter_stylize_wind":1800,
"publish_tofile_cloud_amazons3":1600,
"publish_tofile_cloud_dropbox":1800,
"publish_tofile_cloud_googledrive":1900,
"publish_tofile_localdrive":1500,
"publish_tofile_nas":2500,
"publish_toweb_facebook":3000,
"publish_toweb_instagram":3000,
"publish_toweb_youtube":3000
}
 
@app.route('/')
def home():
	return render_template('index.html')
	
@app.route('/train',methods=["GET","POST"])
def train_data():
	content = request.get_json()
	print(content['path'])
	array=content['screenMap']
	np_array=np.array(array).astype(np.uint8)
	path=os.getcwd()+'/data/training/'+content['path']
	img = Image.fromarray(np_array.T)
	#img.show()
	print(os.getcwd())
	os.makedirs(os.path.dirname(path), exist_ok=True)
	img.save(path+'/'+str(uuid.uuid1())+'.bmp')
	resp = jsonify(success="Training data received and stored")
	return resp
 
 
@app.route('/validation',methods=["GET","POST"])
def validation_data():
	content = request.get_json()
	print(content['path'])
	array=content['screenMap']
	np_array=np.array(array).astype(np.uint8)
	path=os.getcwd()+'/data/validation/'+content['path']
	img = Image.fromarray(np_array.T)
	#img.show()
	print(os.getcwd())
	os.makedirs(os.path.dirname(path), exist_ok=True)
	img.save(path+'/'+str(uuid.uuid1())+'.bmp')
	resp = jsonify(success="Validation data received and stored")
	return resp
	
	
@app.route('/evaluate',methods=["GET","POST"])
def evaluation_data():
	content = request.get_json()
	timeExp=1;
	if(int(content['delay'])>event_time.get(content['operationEnd'])):
		print('Delay deteced')
		timeExp=-1
	print(content['path'])
	array=content['screenMap']
	database=content['companyName']
	db=client[database]
	usercount = db.users.find({'user': content['path']}).count()
	print('user count'+str(usercount))
	if usercount==0:
		result=db.users.insert({'user':content['path']})
		print(result)
	np_array=np.array(array).astype(np.uint8)
	path=os.getcwd()+'//data//eval//'+content['path']+'/'
	img = Image.fromarray(np_array.T)
	print(os.getcwd())
	os.makedirs(os.path.dirname(path), exist_ok=True)
	img.save(path+'/ evaluate.bmp')
	model = tf.keras.models.load_model("D://MS//BITSPilani//Sem4//project//main//ui//data//model//myModel.h5")
	img1 = image.load_img(path+'/ evaluate.bmp', target_size=(300, 300), color_mode="grayscale")
	x = image.img_to_array(img1)
	x = np.expand_dims(x, axis=0)
	images = np.vstack([x])
	#with graph.as_default():
	classes1 = model.predict(images)
	class_index=model.predict_classes(images)
	single_pred = np.squeeze(class_index)
	if os.path.isfile('D://MS//BITSPilani//Sem4//project//main//ui//data//model//class_labels.npy'):
		class_indices = np.load('D://MS//BITSPilani//Sem4//project//main//ui//data//model//class_labels.npy').item()
	calculatedClass='';
	for classname, classidnex in class_indices.items():    
		if classidnex == class_index:
			print('Action detected: '+classname)
			calculatedClass=classname
	print(class_indices)
	print(class_index)
	docPath=''
	docAction=''
	print(classes1)
	db=client["product"]
	response=""
	resp_link=""
	db_resp=''
	flag_path=1
	flag_end=1
	oprEnd=content['operationEnd']
	if calculatedClass != content['operationEnd']:
		db_resp=db.helpdocs.find_one({'event':content['operationEnd'],'type':"path"})
		flag_path=-1
		resp_link="<a>"+db_resp["doclink"]+"<a> "
	if content['operationStatus']=="2":
		db_resp=db.helpdocs.find_one({"event":content['operationEnd'],"type":"end"})
		flag_end=-1
		resp_link+="<a>"+db_resp["doclink"]+"<a>"
	db=client[database]
	db.usage.insert({"username":content['path'],"userLevel":int(content['userLevel']),"type":"path","experience":flag_path,"event":content['operationEnd']})
	db.usage.insert({"username":content['path'],"userLevel": int(content['userLevel']),"type":"end","experience":flag_end,"event":content['operationEnd']})
	db.usage.insert({"username":content['path'],"userLevel":int(content['userLevel']),"type":"time","experience":timeExp,"event":content['operationEnd']})
	if len(resp_link)>0:
		response="You can read the following document:"+resp_link
	else:
		response=""
	resp = jsonify(success=response)
	return resp
	

@app.route('/register',methods=["GET","POST"])
def register_data():
	db=client["product"]
	content = request.get_json()
	db.helpdocs.insert({'event':content['operationEnd'], 'type':"end",'doclink':"http://"+content['operationEnd']+"_end"})
	db.helpdocs.insert({'event':content['operationEnd'], 'type':"path",'doclink':"http://"+content['operationEnd']+"_path"})
	#db.features.insert({'event':content['operationEnd']})
	#db.helpdocs.insert({'event':content['operationEnd'], 'type':"path",'doclink':"http://file_new_newproject_path"})
	return "done"
	
	
if __name__ == '__main__':
	app.run(debug=True)