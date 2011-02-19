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

	def PreprocessWeights(self):
		pass

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

		# If the rating already exists, just return it, unless mentioned otherwise		
		if (not force_predict) and self.rating_recommender_data['by_user'][userid].has_key(placeid):
			return self.rating_recommender_data['by_user'][userid][placeid]['rating']

		averaged_prediction = self.PredictRatingRaw(userid, placeid)

		# post processing:
		# if we couldn't predict, return default value
		if averaged_prediction == -1:
			ret = self._default_rating

		# check boundaries
		elif averaged_prediction < self._min_rating:
			ret = self._min_rating
		elif averaged_prediction > self._max_rating:
			ret = self._max_rating
		else:
			ret = averaged_prediction

		return ret

	def PredictRatingRaw(self, userid, placeid):
		raise NotImplementedError()


