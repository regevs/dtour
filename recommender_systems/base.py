#
# Recommender Algorithms - Base class
#
__all__ = []
__author__ = "Regev S"

__all__.append("RecommenderSystem")
class RecommenderSystem(object):

	_default_rating = None
	_min_rating = 1
	_max_rating = 5

	def __init__(self, 
				 places_recommender_data,
				 users_recommender_data = {},
				 rating_recommender_data = {'by_user':{}, 'by_place':{}}):

		self.places_recommender_data = places_recommender_data
		self.users_recommender_data = users_recommender_data
		self.rating_recommender_data = rating_recommender_data

		self.SetDefaultRating()


	def SetDefaultRating(self):

		sum_rating = 0.0
		n_rating = 0.0

		for userid, rated_places in self.rating_recommender_data['by_user'].iteritems():
			for placeid, v in rated_places.iteritems():
				sum_rating += v['rating']
				n_rating += 1

		if n_rating != 0:
			average_rating = float(sum_rating) / n_rating
			self._default_rating = average_rating			
		else:
			self._default_rating = 1

	def PredictRating(self, userid, placeid, force_predict=False):
		raise NotImplementedError()


