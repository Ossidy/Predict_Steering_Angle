#-*- coding: utf-8 -*-
# Model for predict steering
#
# *** Udacity Predict steering angle ****
#
# Copyright 2016 Xiao Wang, Zhaocheng Liu
# {xwang696, zcliu}@gatech.edu

import tensorflow as tf
import pred_steer
import read_data
import time
import os
import random
import numpy as np

random.seed(18)

folder = './tensor/'
for the_file in os.listdir(folder):
	file_path = os.path.join(folder, the_file)
	os.remove(file_path)

input_path = "./data/angles_train.txt"
eval_path = "./data/angles_valid.txt"

### indicate whether in training phase or in testing case, used for batch normalization
train_flag = tf.placeholder(tf.bool, name='train_flag')
### actually this is the keep probability in those fully connected layers
drop_prob = tf.placeholder('float', name='drop_prob')
wd = tf.placeholder('float', name='wd')

def running(learning_rate, keep_prob, BATCH_SIZE, weight_decay):
	x = tf.placeholder(tf.float32, [BATCH_SIZE, 140, 320, 3])
	y = tf.placeholder(tf.float32, [BATCH_SIZE])

	global_step = tf.Variable(0, trainable = False)

	##### training queue inputs #####

	## get input
	train_images, train_angles, valid_images, valid_angles = read_data.read(input_path, eval_path)
	
	num_train = len(train_angles)
	num_valid = len(valid_angles)

	train_per_epoch = int((num_train*1.0)/BATCH_SIZE)
	valid_per_epoch = int((num_valid*1.0)/BATCH_SIZE)

	learning_rate_decay = tf.train.exponential_decay(learning_rate, global_step,30000, 0.80, staircase = True)
	tf.scalar_summary('learning_rate',learning_rate_decay)
	## pointer 
	train_pointer = 0
	valid_pointer = 0

	## inference build model
	prediction = pred_steer.inference(x, train_flag, drop_prob, wd)

	## calculate loss
	loss = pred_steer.loss(prediction, y)

	## build model per batch and update parameters
	train_op = pred_steer.train(loss, learning_rate_decay, global_step)

	## build initialization peration 
	init = tf.initialize_all_variables()
		## merge all summaries and initialize writer
		#summary_op = tf.merge_all_summaries()
		#train_writer = tf.train.SummaryWriter("./tensorboard", graph = tf.get_default_graph())

	tf.scalar_summary('train_RMSE', tf.sqrt(loss))
	#tf.scalar_summary('l2_norm', l2)
		#tf.scalar_summary('train_pred', tf.reduce_mean(prediction))
		#tf.scalar_summary('eval_pred', tf.reduce_mean(eval_pred))
		#tf.scalar_summary('train_angle', tf.reduce_mean(angles))
		#tf.scalar_summary('eval_angle', tf.reduce_mean(tf.string_to_number(eval_angs, out_type = tf.float32)))

	sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
	merged = tf.merge_all_summaries()
	writer = tf.train.SummaryWriter("./tensor/", sess.graph)
	saver = tf.train.Saver()
	sess.run(init)

	epoch = 0
		## start the queue runners
	#coord = tf.train.Coordinator()
	#enqueue_threads = tf.train.start_queue_runners(sess = sess, coord = coord)
	saver.restore(sess,'./save/my-model-121000')
	
	for step in range(1,400000):
		start_time = time.time()
		images_array, angles_array = read_data.Train_Batch(train_images, train_angles, BATCH_SIZE) #, train_pointer)
		_, summary = sess.run([train_op, merged], 
			feed_dict = {x: images_array, y: angles_array, train_flag:True, drop_prob:keep_prob, wd:weight_decay })
		if step%20 == 0:
			#train_images_sub, train_angles_sub = read_data.Train_Batch(train_images, train_angles, BATCH_SIZE)
			eval_images_array, eval_angles_array = read_data.Valid_Batch(valid_images, valid_angles, BATCH_SIZE) #, valid_pointer)
			#print("step: %d, eval_loss: %g"%(step, sess.run(loss, feed_dict = {
			#	x: eval_images_array, y:eval_angles_array, train_flag:False, drop_prob:1.0})))
			#train_out = sess.run(loss, feed_dict = {x: train_images_sub, y: train_angles_sub, train_flag:False, drop_prob:1.0, wd:0.0})
			out = sess.run(loss, feed_dict = {x: eval_images_array, y: eval_angles_array, train_flag:False, drop_prob:1.0, wd:0.0})
			print("step: "+ str(step)+ " loss: " + str(np.sqrt(out)))
			if step%2000 == 0:
				#checkpath = "./save/model.ckpt"
				filename = saver.save(sess, './save/my-model', global_step=global_step) 
				#filename = saver.save(sess, checkpath)
				print("Model saved in file: %s" %filename)
			# _, summary = sess.run([train_op, summary_op])
			#train_writer.add_summary(summary, step)
		#duration = time.time() - start_time
		writer.add_summary(summary, step)
		#print(str(step) + " time:"+ str(duration))# + " loss: " + str(loss_value))

		# if (train_pointer > num_train):
		# 	train_pointer = 0
		# 	train_images, train_angles = read_data.Shuffle(train_images, train_angles)
		# 	epoch += 1
		# 	print("Epoch " + str(epoch))

		# if (valid_pointer > num_valid):
		# 	valid_pointer = 0
		# 	valid_images, valid_angles = read_data.Shuffle(valid_images, valid_angles)
		# 	#print(pred)
	# coord.request_stop()
	# coord.join(enqueue_threads)

def main(argv = None):
	## argv[4] = {name_of_py_file, learning_rate, drop_prob, BATCH_SIZE}
	running(float(argv[1]), float(argv[2]), int(argv[3]), float(argv[4]))

if __name__=='__main__':
	tf.app.run()
