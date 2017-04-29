from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from PIL import Image
import operator
from django.utils import timezone

def getUserPurchaseHistory(user):     #take a user object as argument
	#this function woudl return a list of game objects
	purchases = Purchase.objects.filter(userId=user).all()
	purchaselist = list(purchases)
	gamePurchased = []
	for p in purchaselist:
		games = p.game.all()
		for g in games:
			theGame = Game.objects.get(game=g)
			if theGame in gamePurchased:
				print("already in ")
			else:
				gamePurchased.append(theGame)

	return gamePurchased
def getGamePurchaseStatus(user,game):
	purchasedGameList = getUserPurchaseHistory(user)
	for purchasedGame in purchasedGameList:
		if game == purchasedGame:
			return True
	return False
# Create your models here.
class Game(models.Model):
	game = models.CharField(max_length=200,blank=True, null=True)
	price = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)
	game_id = models.CharField(max_length=200,blank=True, null=True)
	gameDescription = models.TextField(blank=True)
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



class Platform(models.Model):
	PlatformName = models.CharField(max_length=100,blank=True,null=True)
	def __str__(self):
		return self.PlatformName

class Purchase(models.Model):
	pTime = models.CharField(max_length=100,blank=True,null=True)
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
	def getSpentAmount(user):
		amount = 0
		try:
			purchased = list(Purchase.objects.filter(userId=user).all())
			for p in purchased:
				for g in p.game.all():
					amount += g.price
		except:
			amount = 0





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
	amount = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)

	def receiveReward(self):                    # to record the time when the reward is received
			self.timeReceived = timezone.now()
			self.save()
	def numberOfReward(user):
			Reward.objects.all().filter(user=user)
			return
	def getAmountToNextReward(user):   # get the amount to next reward
			spent = Purchase.getSpentAmount(user)
			amount = Reward.objects.get(user=user).amount

			if spent ==0 :
				return 18
			else:
				return 100-(amount-int(amount))*100
	def getRewardForUser(currentUser):    # get the reward amount
		spent = Purchase.getSpentAmount(currentUser)
		if spent == 0 :
			rewardForNewuser=Reward(user=currentUser,amount=0.18)
			rewardForNewuser.receiveReward()
			rewards=rewardForNewuser
			amountToNextReward = rewardForNewuser.getAmountToNextReward(currentUser)
			return 0
		else :
			amount = Reward.objects.get(user=currentUser).amount
			re = int(amount)
			return re
	def updateReward(currentUser):  # update the reward when purchase
		spent = Purchase.getSpentAmount(currentUser)
	def useReward(self,amountUsed): # use the reward and change the amountUseds
		self.amount = self.amount - amountUsed
	def useReward(user,amountUsed): # used to update amount outside the class
		r = Reward.objects.get(user=user)
		r.useReward(amountUsed)




class Administrator(models.Model):
	adminID = models.CharField(max_length=200)

class Recommendation(models.Model):
    .
	userId = models.ForeignKey(User)
	def __str__(self):
		return self.userId.first_name + self.userId.last_name
	def getRecommendationList(self):
		user = self.userId
		### Get a list of tags from user purchase history ###
		tagList = []
		print("getting recommendation")
		# Call the function to get purchase history
		purchasedList = getUserPurchaseHistory(user)
		# Put all the related tags into tagList
		for eachPurchasedGame in purchasedList:
			for eachRelatedTag in eachPurchasedGame.tag_set.all():
				if eachRelatedTag not in tagList:
					tagList.append(eachRelatedTag)

		### Look for four games that are most affliated with the tags ###
		# Create a recommendation list
		rcmdList = []
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

		# Put four games into rcmdList if the game is not yet purchased
		i = 0
		while len(rcmdList) < 4:
			if sorted_tup[len(sorted_tup)-i-1][0] not in purchasedList:
				rcmdList.append(sorted_tup[len(sorted_tup)-i-1][0])
			i += 1
		return rcmdList
class FeaturedGame(models.Model): #class to maintain the list of featured games
    games=[]              # always maintain 4 games
    def getFeaturedGame(self):
        if len(games) == 0:
            allgames = Game.objects.all()
            games=allgames[0:3:1]      # get default games
        return games
    def setFeaturedGame(self,gamelist): # take a list of games as argument
        amount = len(gamelist)
        if amount == 0:
            return
        elif amount == 4:
            games = gamelist
        elif amount < 4:
            for i in range(amount):
                games[i] = gamelist[i]
