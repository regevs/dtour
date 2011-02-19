#
# Recommender Algorithms - Item-based methods
#
__all__ = []
__author__ = "Regev S"


# Self imports
import base

# python imports
import sys

class ItemBasedRecommenderSystem(base.RecommenderSystem):
	pass
		
		
		



	





class SlopeOneRecommenderSystem(ItemBasedRecommenderSystem):

	def __init__(self, 
				 places_recommender_data,
				 users_recommender_data,
				 rating_recommender_data,
				 weighted = False):
		ItemBasedRecommenderSystem.__init__(self, places_recommender_data, users_recommender_data, rating_recommender_data)

		self.weighted = weighted
		self.CalculateDeviationMatrix()	
	

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
				
	def PredictRatingRaw(self, userid, placeid):

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
	
class TFIDFRecommenderSystem(ItemBasedRecommenderSystem):
	
	def __init__(self, 
				 places_recommender_data,
				 users_recommender_data,
				 rating_recommender_data,
				 categorical_keywords = [],
				 numerical_keywords = []):
		ItemBasedRecommenderSystem.__init__(self, places_recommender_data, users_recommender_data, rating_recommender_data)

		self.categorical_keywords = categorical_keywords
		self.numerical_keywords = numerical_keywords

		self.InitFeatures()
		self.InitWeights()		
		self.CalculatePlaceRepresentations()
		self.PreprocessWeights()
		

	def InitFeatures(self):

		# add all the features 
		self.features = set([])

		# add all the categorical keywords. Each option for each keyword is a boolean feature
		self.possible_values = {}

		for categorical_keyword in self.categorical_keywords:

			self.possible_values[categorical_keyword] = set([])

			# check all the possible options
			for placeid, info in self.places_recommender_data.data.iteritems():

				# add the feature if it doesn't exist
				feature = (categorical_keyword, info[categorical_keyword])

				if feature not in self.features:
					self.possible_values[categorical_keyword].add(info[categorical_keyword])
					self.features.add(feature)

		# add all the numerical keywords as is
		for numerical_keyword in self.numerical_keywords:
			self.features.add(numerical_keyword)
				

	def InitWeights(self):

		# do something trivial
		self.weights = {}
		for feature in self.features:
			self.weights[feature] = 1.0 

	def CalculatePlaceRepresentations(self):
		
		# calc the representations for all the place ids, over all features
		self.representations = {}
		for placeid in self.places_recommender_data.keys():
			self.representations[placeid] = {}

		# add all the categorical keywords. Each option for each keyword is a boolean feature
		for categorical_keyword in self.categorical_keywords:			
			for placeid, info in self.places_recommender_data.data.iteritems():
				for possible_value in self.possible_values[categorical_keyword]:
					feature = (categorical_keyword, possible_value)
					if info[categorical_keyword] == possible_value:
						self.representations[placeid][feature] = 1
					else:
						self.representations[placeid][feature] = 0

		# add all the numerical keywords, normalize by largest
		for numerical_keyword in self.numerical_keywords:
			
			# find min and max 
			all_values = [float(info[numerical_keyword]) for placeid, info in self.places_recommender_data.data.iteritems() if info[numerical_keyword] != None]
			max_value = max(all_values)		
			min_value = min(all_values)
				
			# put the value
			for placeid, info in self.places_recommender_data.data.iteritems():
				if info[numerical_keyword] == None:
					self.representations[placeid][numerical_keyword] = min_value
				else:
					# self.representations[placeid][numerical_keyword] = (float(info[numerical_keyword]) - min_value) / (max_value - min_value)
					self.representations[placeid][numerical_keyword] = float(info[numerical_keyword])

	def PreprocessWeights(self):
		self.norms = {}
		for placeid, rep in self.representations.iteritems():
			self.norms[placeid] = sum([self.weights[feature] * rep[feature]**2 for feature in self.features])**0.5
		
		self.inners = {}
		for placeid, rep in self.representations.iteritems():
			for placeid_j, rep_j in self.representations.iteritems():
				 self.inners[(placeid, placeid_j)] = sum([self.weights[feature] * rep[feature] * rep_j[feature] for feature in self.features])

				
		
	def PredictRatingRaw(self, userid, placeid):

		epsilon = 10**-7

		# all the other places the user rated
		rated_places = self.rating_recommender_data.data['by_user'][userid].keys()
		rated_places = [placeid_j for placeid_j in rated_places if placeid_j != placeid]

		if len(rated_places) == 0:
			return -1

		self.total_weights = {}
		self.total_rating = {}

		for placeid_j in rated_places:
		
			# the other rating
			rating_j = self.rating_recommender_data.data['by_user'][userid][placeid_j]['rating']

			# cosine similarity			
			inner_product = self.inners[(placeid, placeid_j)]
			cosine_weight = inner_product / (self.norms[placeid] * self.norms[placeid_j]) + epsilon

			self.total_weights[placeid_j] = cosine_weight
			self.total_rating[placeid_j] = rating_j

		averaged_prediction = sum([self.total_weights[placeid_j]*self.total_rating[placeid_j] for placeid_j in rated_places]) / sum(self.total_weights.values())

		return averaged_prediction
		


