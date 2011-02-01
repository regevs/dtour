#
# Recommender Algorithms - Base class
#
__all__ = []
__author__ = "Regev Schweiger"

__all__.append("RecommenderSystem")
class RecommenderSystem:
	def PredictRating(self, userid, placeid):
		raise NotImplementedError()


