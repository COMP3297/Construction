from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from PIL import Image
import operator
from django.utils import timezone

def getUserPurchaseHistory(user):     #take a user object as argument
	#this function woudl return a list of game objects
	purchases = Purchase.objects.all().filter(userId=user).order_by('-pTime')
	purchaselist = list(purchases)
	gamePurchased = []
	i = 0
	while len(gamePurchased) < 3 and i < len(purchaselist):
		games = purchaselist[i].game.all()
		for g in games:
			theGame = Game.objects.get(game=g)
			if theGame not in gamePurchased:
				gamePurchased.append(theGame)
				if len(gamePurchased) == 3:
					break
		i += 1
	return gamePurchased

def getGamePurchaseStatus(user,game):
	purchasedGameList = getUserPurchaseHistory(user)
	for purchasedGame in purchasedGameList:
		if game == purchasedGame:
			return True
	return False

# Create your models here.

# Class to maintain the list of featured games
# There should always be only one instance of this class, "ftr"
class FeaturedGame(models.Model):
	title = models.CharField(max_length=200, blank=True, null=True)
	def __str__(self):
		return self.title or u''


class Game(models.Model):
	game = models.CharField(max_length=200,blank=True, null=True)
	price = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)
	game_id = models.CharField(max_length=200,blank=True, null=True)
	gameDescription = models.TextField(blank=True)
	featuredGame = models.ForeignKey(FeaturedGame,blank=True, null=True)
	rTime = models.DateTimeField(auto_now = False, auto_now_add = False)
	def getImageList(self):
		images = GameImage.objects.filter(game=self).all()
		return images
	def __str__(self):
		return self.game
	def addTag(self,tag,creator):     #take a tag content as an argument
			try:
				tag_obj = Tag.objects.get(tag=tag)
			except:
				tag_obj = Tag(tag=tag,creator=creator)
				tag_obj.save()
			tag_obj.game.add(self)
	def relatedTags(self):
			tags = Tag.objects.filter(game=self)
			tagcontext = []
			for t in tags:
				tagcontext.append(t.tag)
			return tagcontext

class GameImage(models.Model):
	image = models.ImageField(upload_to='images',blank=True)
	game = models.ForeignKey(Game)
	def __str__(self):
		return self.image.name


class Tag(models.Model):
	tag = models.CharField(max_length=50,blank=True, null=True)
	creator = models.ForeignKey(User,blank=True, null=True)
	game = models.ManyToManyField(Game,blank=True)
	def __str__(self):
		return self.tag
	def getGameList(self):
		return self.game.all()


class Platform(models.Model):
	PlatformName = models.CharField(max_length=100,blank=True,null=True)
	def __str__(self):
		return self.PlatformName

class Purchase(models.Model):
	pTime = models.DateTimeField(auto_now = False, auto_now_add = False)
	userId = models.ForeignKey(User,blank=True, null=True)
	game = models.ManyToManyField(Game,blank=True)
	platform = models.ForeignKey(Platform,blank=True,null=True)
	def __str__(self):
		return str(self.pTime)
	def addGame(self,cart):
		games = cart.game.all()
		for gme in games:
			g = Game.objects.get(game=gme)
			self.game.add(g)


	def getGame(self):
		return self.game
	def getSpentAmount(user):
		amount = 0
		try:
			purchased = list(Purchase.objects.filter(userId=user).all())
			for p in purchased:
				for g in p.game.all():
					amount += g.price
		except:
			amount = 0
		return amount


class Cart(models.Model):
	user = models.ForeignKey(User,blank=True,null=True)
	game = models.ManyToManyField(Game,blank=True)
	def addGame(self,game):
		self.game.add(game)
	def getTotal(self):
		games = self.game.all()
		amount = self.game.all().count()
		totalAmount = 0
		for gme in games:
			price = Game.objects.get(game=gme).price
			totalAmount = totalAmount + price
		return totalAmount
	def getGameList(self):
			return self.game
	def clearCart(self):
		games = self.game.all()
		for g in games:
			self.game.remove(g)

	def deleteItem(self,game_id):
		theGame = Game.objects.get(game_id=game_id)
		self.game.remove(theGame)

class Reward(models.Model):
	user = models.ForeignKey(User,blank=True,null=True)
	timeReceived = models.DateTimeField(blank=True, null=True)
	expirationDate = models.DateTimeField(blank=True,null=True)
	amount = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)

	def receiveReward(self):                    # to record the time when the reward is received
			self.timeReceived = timezone.now()
			self.expirationDate = timeReceived + timedelta(days=120)
			self.save()
	def numberOfReward(user):
			count = Reward.objects.all().filter(user=user).count()
			return count
	def getAmountToNextReward(user):   # get the amount to next reward
			spent = Purchase.getSpentAmount(user)
			spent = int(spent)
			return 100-(spent+18)%100
	def updateReward(currentUser):  # update the reward when purchase
		spent = Purchase.getSpentAmount(currentUser)
	def useReward(self,amount): # use the reward and change the amountUseds
		self.delete()
	def getAllRewards(user):
		rewardList = Reward.objects.filter(user=user).all()
		rewardList = sorted(rewardList,key=lambda e:e.timeReceived,reverse=True)
		return rewardList




class Administrator(models.Model):
	adminID = models.CharField(max_length=200)

class Recommendation(models.Model):
	userId = models.ForeignKey(User)
	def __str__(self):
		return self.userId.first_name + self.userId.last_name
	def getRecommendationList(self):
		user = self.userId
		
		# Call the function to get purchase history (at most three recently purchased games)
		purchasedList = getUserPurchaseHistory(user)
		# Create a recommendation list
		rcmdList = []
		# Traverse through each targeted game
		for eachPurchasedGame in purchasedList:
			# Put all the related tags into tagList
			tagList = list(eachPurchasedGame.tag_set.all())
			# Create and initialize a dictionary for similarity count
			similarity_dic = {}
			gameList = Game.objects.all()
			for eachGame in gameList:
				similarity_dic[eachGame] = 0
			# Start counting
			for eachTag in tagList:
				for eachGame in eachTag.game.all():
					similarity_dic[eachGame] += 1
			# Sort similarity_dic according to count
			sorted_tup = sorted(similarity_dic.items(), key=operator.itemgetter(1))
			# Exclude the purchased game itself
			new_sorted_tup = []
			for tup in sorted_tup:
				if not tup[0] == eachPurchasedGame:
					new_sorted_tup.append(tup)
			# Put the most related games into temp
			temp = []
			for eachTup in new_sorted_tup:
				if eachTup[1] == new_sorted_tup[len(new_sorted_tup)-1][1]:
					temp.append(eachTup[0])
			# Put the most recently released game into rcmdList
			if sorted(temp, key=lambda eachGame: eachGame.rTime, reverse=True)[0] not in rcmdList:
				rcmdList.append(sorted(temp, key=lambda eachGame: eachGame.rTime, reverse=True)[0])
		# Check if any purchased game is in rcmdList
		purchaselist = list(Purchase.objects.all().filter(userId=user))
		gamePurchased = []
		for eachPurchase in purchaselist:
			games = eachPurchase.game.all()
			for g in games:
				theGame = Game.objects.get(game=g)
				if theGame not in gamePurchased:
					gamePurchased.append(theGame)
		for eachGamePurchased in gamePurchased:
			while eachGamePurchased in rcmdList:
				rcmdList.remove(eachGamePurchased)
		return rcmdList
