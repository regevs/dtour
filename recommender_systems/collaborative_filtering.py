#
# Recommender Algorithms - Collaborative Filtering
#
__all__ = []
__author__ = "Regev S"


import warnings
from numpy import *

# Self imports
import base

class SlopeOneRecommenderSystem(base.RecommenderSystem):

	def __init__(self, 
				 places_recommender_data,
				 users_recommender_data,
				 rating_recommender_data,
				 weighted = False):
		base.RecommenderSystem.__init__(self, places_recommender_data, users_recommender_data, rating_recommender_data)
		
		self.weighted = weighted
		self.CalculateDeviationMatrix()


	def CalculateDeviationMatrix(self):
		
		self.deviation_matrix = {}
		self.common_users = {}
		
		all_places_ids = self.places_recommender_data.keys()
		n_places = len(all_places_ids)

		for placeid_i in all_places_ids:
			self.deviation_matrix[placeid_i] = {}
			self.common_users[placeid_i] = {}
			for placeid_j in all_places_ids:
				self.deviation_matrix[placeid_i][placeid_j] = 0.0
				
		for i in range(n_places):
			for j in range(i):
				placeid_i = all_places_ids[i]
				placeid_j = all_places_ids[j]

				common_users = set(self.rating_recommender_data['by_place'].get(placeid_i, {}).keys()) & set(self.rating_recommender_data['by_place'].get(placeid_j, {}).keys())
				self.common_users[placeid_i][placeid_j] = len(common_users)
				self.common_users[placeid_j][placeid_i] = len(common_users)

				for userid in common_users:
					diff = (self.rating_recommender_data['by_place'][placeid_i][userid]['rating'] - self.rating_recommender_data['by_place'][placeid_j][userid]['rating'])

					self.deviation_matrix[placeid_i][placeid_j] += diff
					self.deviation_matrix[placeid_j][placeid_i] += (-diff)
				

	def PredictRatingRaw(self, userid, placeid, force_predict=False):

		placeid_j = placeid

		places_with_common_users = [placeid_i for placeid_i in self.rating_recommender_data['by_user'][userid].keys() \
											  if placeid_i != placeid_j and self.common_users[placeid_i][placeid_j] > 0]
											  
		if len(places_with_common_users) == 0:			
			# warnings.warn("Cannot predict - no common rating with anyone")
			averaged_prediction = -1
			
		else:
			total_prediction = 0.0
			total_weights = 0.0

			for placeid_i in places_with_common_users:
				dev = self.deviation_matrix[placeid_j][placeid_i] / float(self.common_users[placeid_j][placeid_i])
				user_rating = self.rating_recommender_data['by_user'][userid][placeid_i]['rating']

				if self.weighted:
					weight = float(self.common_users[placeid_j][placeid_i])
				else:
					weight = 1.0
				total_prediction += (dev + user_rating) * weight
				total_weights = weight


			averaged_prediction = total_prediction / total_weights

		return averaged_prediction



__all__.append("PearsonRecommenderSystem")
class PearsonRecommenderSystem(base.RecommenderSystem):	

	_case_amplification = 2.5
	_correction_ratio = 1

	def __init__(self, 
				 places_recommender_data,
				 users_recommender_data,
				 rating_recommender_data):
		base.RecommenderSystem.__init__(self, places_recommender_data, users_recommender_data, rating_recommender_data)
	
	
		self._default_average_rating = self._default_rating
		
		self.CalculateUserAverages()
		self.CalculateUserSimilarityMatrix()


	

	def CalculateUserAverages(self):

		self.user_averages = {}
		# self.user_sigmas = {}

		all_users = self.users_recommender_data.keys()

		for i, userid_i in enumerate(all_users):
			
			ratings = []			

			for placeid, info in self.rating_recommender_data['by_user'].get(userid_i, {}).iteritems():
				ratings.append(info['rating']				)
				
			n_rating = len(ratings)

			if n_rating == 0:
				self.user_averages[userid_i] = self._default_average_rating				
			else:
				self.user_averages[userid_i] = sum(ratings) / n_rating

			# if n_rating == 0:
			# 	self.user_sigmas[userid_i] = 1.0
			# else:
			# 	self.user_sigmas[userid_i] = sum([float(r - self.user_averages[userid_i])**2 / (n_rating*2) for r in ratings])**0.5
			# if self.user_sigmas[userid_i] == 0.0:
			# 	self.user_sigmas[userid_i] = 1.0
		

	def CalculateUserSimilarityMatrix(self):
		
		self.user_sim_matrix = {}

		all_users = self.users_recommender_data.keys()

		for i, userid_i in enumerate(all_users):
			self.user_sim_matrix[userid_i] = {}
			self.user_sim_matrix[userid_i][userid_i] = 0.0 # to avoid influence on your own predictions

			for j, userid_j in enumerate(all_users[:i]):

				common_places = set(self.rating_recommender_data['by_user'].get(userid_i, {}).keys()) & \
								set(self.rating_recommender_data['by_user'].get(userid_j, {}).keys())


				if len(common_places) == 0:
					correlation = 0.0
				
				else:
					# calculate pearson's correlation
					inner_product = sum([(self.rating_recommender_data['by_user'][userid_i][placeid]['rating'] - self.user_averages[userid_i]) * \
									 (self.rating_recommender_data['by_user'][userid_j][placeid]['rating'] - self.user_averages[userid_j]) for placeid in common_places])

					var_i = sum([(self.rating_recommender_data['by_user'][userid_i][placeid]['rating'] - self.user_averages[userid_i])**2 for placeid in common_places])
					var_j = sum([(self.rating_recommender_data['by_user'][userid_j][placeid]['rating'] - self.user_averages[userid_j])**2 for placeid in common_places])

					if var_i*var_j == 0:
						correlation = 0.0
					else:
						correlation = inner_product / (var_i * var_j)**0.5


				# idioitic correction
				correlation *= min(1.0, float(len(common_places)) / self._correction_ratio)

				# calculate the case amplification of the correlation
				gamma = abs(correlation)**self._case_amplification * correlation

				# this is the similarity
				self.user_sim_matrix[userid_i][userid_j] = gamma
				self.user_sim_matrix[userid_j][userid_i] = gamma


	def PredictRatingRaw(self, userid, placeid, force_predict=False):

		total_prediction = 0.0
		total_weights = 0.0

		for userid_v in self.rating_recommender_data['by_place'].get(placeid, {}).keys():
			
			dev =  self.rating_recommender_data['by_place'][placeid][userid_v]['rating'] - self.user_averages[userid_v]
			weight = self.user_sim_matrix[userid][userid_v]

			total_prediction += weight * dev 
			total_weights += abs(weight)

		averaged_prediction = self.user_averages[userid] 
		if total_weights > 0:
			averaged_prediction += total_prediction / total_weights

		return averaged_prediction
		