#
# Recommender Algorithms
#
__all__ = []
__author__ = "Regev Schweiger"


import base

__all__.append("ExpertRating")
class ExpertRating(base.RecommenderSystem):

	_default_expert_rank = 3

	def __init__(self, places_recommender_data):
		base.RecommenderSystem.__init__(self, places_recommender_data)

	def PredictRating(self, userid, placeid, force_predict=False):
		expert_rank = self.places_recommender_data[placeid]['expert_rank']
		if expert_rank != None:
			return expert_rank
		else:
			return self._default_expert_rank


__all__.append("AverageRating")
class AverageRating(base.RecommenderSystem):

	def PredictRating(self, userid, placeid, force_predict=False):
		return self._default_rating

