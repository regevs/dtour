#
# Recommender Algorithms - Evaluators
#
__all__ = []
__author__ = "Regev S"


class Evaluator(object):
	def Evaluate(self, recommender_system):
		raise NotImplementedError()

__all__.append("AllButOneMeanAverageError")
class AllButOneMeanAverageError(Evaluator):			

	def Evaluate(self, recommender_system):

		# go over all (rating) users
		n_users = len(recommender_system.rating_recommender_data['by_user'])
		total_averages = 0.0

		for userid, rated_places in recommender_system.rating_recommender_data['by_user'].iteritems():

			n_rated_places = len(rated_places)
			total_average_error = 0.0

			# go over all rated places for that user
			for placeid, v in rated_places.iteritems():

				# compare real rating to predicted rating
				user_rating = v['rating']
				predicted_rating = recommender_system.PredictRating(userid, placeid, force_predict=True)

				abs_diff = abs(user_rating - predicted_rating)

				total_average_error += abs_diff

			total_averages += (float(total_average_error) / n_rated_places)

		mae = total_averages / n_users

		return mae

