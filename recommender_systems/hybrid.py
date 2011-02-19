#
# Recommender Algorithms - Hybrid methods
#
__all__ = []
__author__ = "Regev S"


# Self imports
import base

class LinearHybridRecommender(base.RecommenderSystem):

	def __init__(self,
				 recommender_system_objects = [], weights = None):

		self.recommender_system_objects = recommender_system_objects
		self.n_recommenders = len(self.recommender_system_objects)		
		if (self.n_recommenders == 0):
			raise InputError("No recommender systems given")

		base.RecommenderSystem.__init__(self, 
										self.recommender_system_objects[0].places_recommender_data,
										self.recommender_system_objects[0].users_recommender_data,
										self.recommender_system_objects[0].rating_recommender_data
										)

		if weights != None:
			self.weights = dict(zip(range(self.n_recommenders), weights))
		else:
			self.weights = dict(zip(range(self.n_recommenders), [0.5]*self.n_recommenders))

	def PredictRatingRaw(self, userid, placeid):
		ratings = []
		for obj in self.recommender_system_objects:
			ratings.append(obj.PredictRating(userid, placeid, force_predict=True))
		
		average_prediction =  sum([ratings[i] * self.weights[i] for i in range(self.n_recommenders)])

		return average_prediction
