#
# Recommender Algorithms - Hybrid methods
#
__all__ = []
__author__ = "Regev S"


# Self imports
import base

__all__.append('LinearHybridRecommender')
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

__all__.append('FeatureAugmentRecommender')
class FeatureAugmentRecommender(base.RecommenderSystem):

	def __init__(self,
				content_based_recommender_system_class,
				other_recommender_system,
				categorical_keywords = [],
				numerical_keywords = []				
				):

		self.content_based_recommender_system_class = content_based_recommender_system_class
		self.other_recommender_system = other_recommender_system
		self.categorical_keywords = categorical_keywords
		self.numerical_keywords = numerical_keywords

		self.last_userid = None

		base.RecommenderSystem.__init__(self, 
										self.other_recommender_system.places_recommender_data,
										self.other_recommender_system.users_recommender_data,
										self.other_recommender_system.rating_recommender_data
										)

	
	def PredictRatingRaw(self, userid, placeid):
		
		# Add prediction from ther inside RS as an extra feature
		if self.last_userid != userid:
			for placeid_j in self.places_recommender_data.keys():
				self.places_recommender_data[placeid_j]['augmented_feature'] = self.other_recommender_system.PredictRating(userid, placeid_j)

		# Create a new predictor, with the other rating as a feature
		self.content_based_recommender_system_obj = self.content_based_recommender_system_class(
														self.places_recommender_data,
														self.users_recommender_data,
														self.rating_recommender_data,
														self.categorical_keywords,
														self.numerical_keywords + ['augmented_feature'])

		
		prediction = self.content_based_recommender_system_obj.PredictRatingRaw(userid, placeid)

		return prediction

