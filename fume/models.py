from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from PIL import Image


def getUserPurchaseHistory(user):     #take a user object as argument
    #this function is to get the purchase history of a user
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


class Administrator(models.Model):
    adminID = models.CharField(max_length=200)

class Recommendation(models.Model):
	userId = models.ForeignKey(User)
	def __str__(self):
		return self.userId.first_name + self.userId.last_name
    
