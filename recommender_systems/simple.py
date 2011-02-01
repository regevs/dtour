#
# Recommender Algorithms
#
__all__ = []
__author__ = "Regev Schweiger"


import base

#
# TODO: remove when stable
#
reload(base);

class ExpertRating(base.RecommenderSystem):

	_default_expert_rank = 3

	def __init__(self, places_recommender_data):
		self.places_recommender_data = places_recommender_data

	def PredictRating(self, userid, placeid):
		expert_rank = self.places_recommender_data[placeid]['expert_rank']
		if expert_rank != None:
			return expert_rank
		else:
			return self._default_expert_rank

