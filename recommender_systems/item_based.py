#
# Recommender Algorithms - Item-based methods
#
__all__ = []
__author__ = "Regev S"


# Self imports
import base


class ItemBasedRecommenderSystem(base.RecommenderSystem):

	def __init__(self, 
				 places_recommender_data,
				 users_recommender_data,
				 rating_recommender_data,
				 weighted = False):
		base.RecommenderSystem.__init__(self, places_recommender_data, users_recommender_data, rating_recommender_data)
		
		self.weighted = weighted
		self.CalculateDeviationMatrix()	


	def CalculateDeviationMatrix(self):
		raise NotImplementedError()

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





class SlopeOneRecommenderSystem(ItemBasedRecommenderSystem):

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
				

	
