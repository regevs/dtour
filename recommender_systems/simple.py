#
# Recommender Algorithms
#
__all__ = []
__author__ = "Regev S"


import base

__all__.append("ExpertRating")
class ExpertRating(base.RecommenderSystem):

	_default_expert_rank = 3

	def __init__(self, places_recommender_data):
		base.RecommenderSystem.__init__(self, places_recommender_data)

	def PredictRatingRaw(self, userid, placeid):
		expert_rank = self.places_recommender_data[placeid]['expert_rank']
		if expert_rank != None:
			return expert_rank
		else:
			return self._default_expert_rank







__all__.append("AverageRating")
class AverageRating(base.RecommenderSystem):

	def PredictRatingRaw(self, userid, placeid):
		return self._default_rating







__all__.append("AverageUserRating")
class AverageUserRating(base.RecommenderSystem):

	def __init__(self, 
				 places_recommender_data,
				 users_recommender_data,
				 rating_recommender_data):
		base.RecommenderSystem.__init__(self, places_recommender_data, users_recommender_data, rating_recommender_data)
	
	
		self._default_average_rating = self._default_rating
		
		self.CalculateUserAverages()

	def CalculateUserAverages(self):

		self.user_averages = {}

		all_users = self.users_recommender_data.keys()

		for i, userid_i in enumerate(all_users):
			
			total_rating = 0.0
			n_rating = 0

			for placeid, info in self.rating_recommender_data['by_user'].get(userid_i, {}).iteritems():
				total_rating += info['rating']				
				n_rating += 1
			
			if n_rating == 0:
				self.user_averages[userid_i] = self._default_average_rating
			else:
				self.user_averages[userid_i] = float(total_rating) / n_rating

	def PredictRatingRaw(self, userid, placeid):
		return self.user_averages[userid]

