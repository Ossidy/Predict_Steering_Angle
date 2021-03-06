#-*- coding: utf-8 -*-
# Model for predict steering
#
# *** Udacity Predict steering angle ****
#
# Copyright 2016 Xiao Wang, Zhaocheng Liu
# {xwang696, zcliu}@gatech.edu

import tensorflow as tf
import math
import numpy as np


def batch_norm(x, depth, train_flag, decay, mode, scope = 'bn'):
	""" Calaulate batch normalization to acelerate the learning process
	Args: 
		x : 2d or 4d input tensor
		depth: output dimensions
		train_flag: whether in the training phase or testing phase
		decay: parameters controls the calculation of mean and variance
		mode: 0 for 2d input, 1 for 4d input, all return the normalized version along the last dimension
		scope: name scope
	Output:
		normalized tensors with same dimension
	"""
	with tf.variable_scope(scope):
		beta = tf.Variable(tf.constant(1.0, shape = [depth]), name = 'beta'
			, trainable = True)
		gamma = tf.Variable(tf.constant(1.0, shape = [depth]), name = 'gamma'
			, trainable = True)
		if mode == 1:
			batch_mean, batch_variance = tf.nn.moments(x, [0,1,2], name = 'moments')
		elif mode == 0:
			batch_mean, batch_variance = tf.nn.moments(x, [0], name = 'moments')
		ema = tf.train.ExponentialMovingAverage(decay = decay)

		def with_update():
			ema_op = ema.apply([batch_mean, batch_variance])
			with tf.control_dependencies([ema_op]):
				return tf.identity(batch_mean), tf.identity(batch_variance)

		mean, var = tf.cond(train_flag, with_update, 
			lambda: (ema.average(batch_mean), ema.average(batch_variance)))
		normed = tf.nn.batch_normalization(x, mean, var, beta, gamma, 1e-3)
	return normed


def inference(images, train_flag, drop_prob, wd):
	""" The network structure for the whole model
	Args:
		images: input 4d tensor
		train_flag: whether in training phase or testing phase
		dopr_prob: the keep_probability of dropout layer
		we: weight decay parameter
	Output:
		Predictions in tensor format
	"""
	batch_size = images.get_shape()[0].value

	with tf.variable_scope('conv1') as scope:
		### weights initialization
		weights = tf.Variable(
			tf.truncated_normal([3,3,3,24], stddev = math.sqrt(2.0/27.0), name='weights'))

		### weights decay 
		weight_decay = tf.mul(tf.nn.l2_loss(weights), wd)
		tf.add_to_collection('losses', weight_decay)

		biases = tf.Variable(tf.zeros([24]),
                      	name='biases')
		### convlutional computation
		conv = tf.nn.conv2d(images, weights,[1,2,2,1],padding = 'VALID')
		bias = tf.nn.bias_add(conv, biases)
		### batch normalization 
		normed = batch_norm(bias, 24, train_flag, 0.9, 1)
		#normed = bias
		##normed = tf.contrib.layers.batch_norm(bias, 0.8, epsilon = 1e-3, is_training=train_flag)
		### using normal relu adtivate functions
		conv_non = tf.nn.relu(normed, name = scope.name)

	#with tf.variable_scope('max_pool_1') as scope:
	#	pooled = tf.nn.max_pool(conv_non, [1,2,2,1], [1,2,2,1], padding= 'VALID')


	with tf.variable_scope('conv2') as scope:
		weights = tf.Variable(
			tf.truncated_normal([3,3,24,36], stddev = math.sqrt(2.0/216.0), name='weights'))

		### weights decay 
		weight_decay = tf.mul(tf.nn.l2_loss(weights), wd)
		tf.add_to_collection('losses', weight_decay)

		biases = tf.Variable(tf.zeros([36]),
                         name='biases')

		conv = tf.nn.conv2d(conv_non, weights,[1,2,2,1],padding = 'VALID')
		bias = tf.nn.bias_add(conv, biases)
		normed = batch_norm(bias, 36, train_flag, 0.9, 1)
		#normed = tf.contrib.layers.batch_norm(bias, 0.8, epsilon = 1e-3, is_training=train_flag)
		#normed = bias
		conv_non = tf.nn.relu(normed, name = scope.name)

	with tf.variable_scope('conv3') as scope:
		weights = tf.Variable(
			tf.truncated_normal([3,3,36,48], stddev = math.sqrt(2.0/324.0), name='weights'))

		### weights decay 
		weight_decay = tf.mul(tf.nn.l2_loss(weights), wd)
		tf.add_to_collection('losses', weight_decay)

		biases = tf.Variable(tf.zeros([48]),
                         name='biases')

		conv = tf.nn.conv2d(conv_non, weights,[1,2,2,1],padding = 'VALID')
		bias = tf.nn.bias_add(conv, biases)
		normed = batch_norm(bias, 48, train_flag, 0.9, 1)
		#normed = bias
		#normed = tf.contrib.layers.batch_norm(bias, 0.99, epsilon = 1e-3, is_training=train_flag)
		conv_non = tf.nn.relu(normed, name = scope.name)

	with tf.variable_scope('conv4') as scope:
		weights = tf.Variable(
			tf.truncated_normal([3,3,48,64], stddev = math.sqrt(2.0/432.0), name='weights'))

		### weights decay 
		weight_decay = tf.mul(tf.nn.l2_loss(weights), wd)
		tf.add_to_collection('losses', weight_decay)

		biases = tf.Variable(tf.zeros([64]),
                         name='biases')

		conv = tf.nn.conv2d(conv_non, weights,[1,2,2,1],padding = 'VALID')
		bias = tf.nn.bias_add(conv, biases)
		normed = batch_norm(bias, 64, train_flag, 0.9, 1)
		#normed = bias
		#normed = tf.contrib.layers.batch_norm(bias, 0.8, epsilon = 1e-3, is_training=train_flag)
		conv_non = tf.nn.relu(normed, name = scope.name)

	with tf.variable_scope('conv5') as scope:
		weights = tf.Variable(
			tf.truncated_normal([3,3,64,64], stddev = math.sqrt(2.0/576.0), name='weights'))

		### weights decay 
		weight_decay = tf.mul(tf.nn.l2_loss(weights), wd)
		tf.add_to_collection('losses', weight_decay)

		biases = tf.Variable(tf.zeros([64]),
                         name='biases')

		conv = tf.nn.conv2d(conv_non, weights,[1,2,2,1],padding = 'VALID')
		bias = tf.nn.bias_add(conv, biases)
		normed = batch_norm(bias, 64, train_flag, 0.9, 1)
		#normed = bias
		#normed = tf.contrib.layers.batch_norm(bias, 0.8, epsilon = 1e-3, is_training=train_flag)
		conv_non = tf.nn.relu(normed, name = scope.name)

	# with tf.variable_scope('conv6') as scope:
	# 	weights = tf.Variable(
	# 		tf.truncated_normal([5,5,64,64], stddev = math.sqrt(2.0/1600.0), name='weights'))
	# 	biases = tf.Variable(tf.zeros([64]),
 #                         name='biases')

	# 	conv = tf.nn.conv2d(conv_non, weights,[1,2,2,1],padding = 'VALID')
	# 	bias = tf.nn.bias_add(conv, biases)
	# 	normed = tf.contrib.layers.batch_norm(bias, 0.99, epsilon = 1e-3, is_training=train_flag)
	# 	conv_non = tf.nn.relu(normed, name = scope.name)

	with tf.variable_scope('local6') as scope:
		reshape = tf.reshape(conv_non,[batch_size,-1])
		dim = reshape.get_shape()[1].value
		weights = tf.Variable(
			tf.truncated_normal([dim, 600], stddev = math.sqrt(2.0/dim), name='weights'))

		### weights decay 
		weight_decay = tf.mul(tf.nn.l2_loss(weights), wd)
		tf.add_to_collection('losses', weight_decay)

		biases = tf.Variable(tf.zeros([600]),
                         name='biases')
		bias = tf.matmul(reshape, weights)+biases
		normed = batch_norm(bias, 600, train_flag, 0.9, 0)
		#normed = tf.contrib.layers.batch_norm(bias, 0.8, epsilon = 1e-3, is_training=train_flag)
		#normed = bias
		local = tf.nn.relu(normed, name = scope.name)
		## drop out
		df = tf.nn.dropout(local, drop_prob)



	with tf.variable_scope('local7') as scope:
		weights = tf.Variable(
			tf.truncated_normal([600, 100], stddev = math.sqrt(2.0/600), name='weights'))

		### weights decay 
		weight_decay = tf.mul(tf.nn.l2_loss(weights), wd)
		tf.add_to_collection('losses', weight_decay)

		biases = tf.Variable(tf.zeros([100]),
                         name='biases')
		bias = tf.matmul(df, weights)+biases
		#normed = bias
		normed = batch_norm(bias, 100, train_flag, 0.9, 0)
		#normed = tf.contrib.layers.batch_norm(bias, 0.8, epsilon = 1e-3, is_training=train_flag)
		local = tf.nn.relu(normed, name = scope.name)
		df = tf.nn.dropout(local, drop_prob)

	with tf.variable_scope('local8') as scope:
		weights = tf.Variable(
			tf.truncated_normal([100, 20], stddev = math.sqrt(2.0/100.0), name='weights'))

		### weights decay 
		weight_decay = tf.mul(tf.nn.l2_loss(weights), wd)
		tf.add_to_collection('losses', weight_decay)

		biases = tf.Variable(tf.zeros([20]),
                         name='biases')
		bias = tf.matmul(df, weights)+biases
		normed = batch_norm(bias, 20, train_flag, 0.9, 0)
		#normed = bias
		#normed = tf.contrib.layers.batch_norm(bias, 0.8, epsilon = 1e-3, is_training=train_flag)
		local = tf.nn.relu(normed, name = scope.name)


	with tf.variable_scope('linear_regression') as scope:
		weights = tf.Variable(
			tf.truncated_normal([20, 1], stddev = math.sqrt(2.0/20), name='weights'))

		### weights decay 
		weight_decay = tf.mul(tf.nn.l2_loss(weights), wd)
		tf.add_to_collection('losses', weight_decay)

		biases = tf.Variable(tf.zeros([1]),
                         name='biases')
		output = tf.matmul(local, weights) + biases
	return output
		

def loss(output, angles):
	""" Calculate the RMSE of prediction angles and labeled angles
	Args:
		output:  prediction tensor, float [batch_size]
		angles:  label tesor, float [batch_size]

	Returns:
		loss: Loss tensor of type float
	"""
	batch_size = output.get_shape()[0].value
	
	reshape = tf.reshape(angles, [batch_size,1])

	#angs = tf.string_to_number(angles, out_type = tf.float32)
	angs = reshape
	### calculate square sum
	#angs = tf.sigmoid(angle)
	sum_square = tf.square(tf.sub(angs, output))
	### calculate mean square mean
	mean_square = tf.reduce_mean(sum_square)
	loss = mean_square
	### do not take square root here! It has influence on the backprobagation
	#tf.add_to_collection('losses', mean_square)
	#loss = tf.add_n(tf.get_collection('losses'), name='total_loss')
	#tf.scalar_summary('RMSE', loss)
	return loss #, loss - mean_square #mean_square

def train(loss, learning_rate, global_step):
	""" Setting the training operation
	Args: 
		loss: loss tensor, from loss()
		learning_rate: the learning reate for gradient descent 
	"""
	### creat the optimizer using learing_rate
	optimizer = tf.train.AdamOptimizer(learning_rate)
	#optimizer = tf.train.RMSPropOptimizer(learning_rate,decay = 0.9, momentum = 0.9)
	#grads = optimizer.compute_gradients(loss)


	#for var in tf.trainable_variables():
	#	tf.histogram_summary(var.op.name, var)

	#for grad, var in grads:
	#	if grad is not None:
	#		tf.histogram_summary(var.op.name+"/gradients",grad)
	###  creat a global variable
	# global_step = tf.Variable(0, name = 'global_step',trainanle = False)
	### note use global step to track trainging step
	train_op = optimizer.minimize(loss, global_step = global_step)
	return train_op
