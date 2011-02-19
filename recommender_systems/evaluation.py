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

		self.rating_data = []

		for userid, rated_places in recommender_system.rating_recommender_data['by_user'].iteritems():

			n_rated_places = len(rated_places)
			total_average_error = 0.0

			# go over all rated places for that user
			for placeid, v in rated_places.iteritems():

				# compare real rating to predicted rating
				user_rating = v['rating']
				predicted_rating = recommender_system.PredictRating(userid, placeid, force_predict=True)

				# print userid, placeid, user_rating, predicted_rating

				abs_diff = abs(user_rating - predicted_rating)

				total_average_error += abs_diff

			total_averages += (float(total_average_error) / n_rated_places)

			self.rating_data.append((n_rated_places, (float(total_average_error) / n_rated_places)))

		mae = total_averages / n_users

		return mae


class Optimizer(object):
	def Optimize(self, recommender_system):
		raise NotImplementedError()

__all__.append("WeightOptimizer")
class WeightOptimizer(Optimizer):
	"assumes the recommender system has a dictionary of weights"

	_evaluator = AllButOneMeanAverageError()

	def Optimize(self, recommender_system):
	
		def optfunc(weights, recommender_system):
			for i,k in enumerate(recommender_system.weights.keys()):
				recommender_system.weights[k] = weights[i]
			
			
			recommender_system.PreprocessWeights()
			
			ret = self._evaluator.Evaluate(recommender_system)
			print weights, ret
			return ret
			
		import scipy.optimize

		x0 = [1.0] * len(recommender_system.weights)

		return scipy.optimize.fmin(optfunc, x0, args=(recommender_system,))

