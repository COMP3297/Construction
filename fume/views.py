
from django.shortcuts import render,redirect

# Create your views here.
from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from fume.models import FeaturedGame,Game,Cart,Tag,User,Recommendation,Purchase,Platform,getUserPurchaseHistory,Reward,getGamePurchaseStatus
from fume.forms import LoginForm,NameForm,PlatformForm,RewardChoosingForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from fume.forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory


def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('featured')
	else:
		form = SignUpForm()
	return render(request, 'registration/signup.html', {'form': form})

@login_required
def games(request, game_id):
	currentUser = request.user
	game = Game.objects.get(game_id=game_id)
	tags = Tag.objects.filter(game=game).all()
	imageList = game.getImageList()
	image1 = imageList[0]
	image2 = imageList[1]
	purchased = getGamePurchaseStatus(currentUser,game)
	return render(request, 'fume/gamePage.html', {'tag_id':game_id, 'tags':tags,'game':game,'image1':image1,'image2':image2, 'purchased':purchased})

@login_required
def purchase(request, game_id):
	print("purchasing")
	user_id=request.user
	user = request.user
	print(user)
	gme_id = game_id


	try:
		this_cart = Cart.objects.get(user = user)
	except:
		this_cart = Cart(user = user)
		this_cart.save()

	index=Cart.objects.get(user=user)
	index=index.game.all().count()
	rangeList = range(index)
	RewardFormSet = formset_factory(RewardChoosingForm, extra=index)
	
	if ( gme_id != "0" ):
		newgame=Game.objects.get(game_id=gme_id)
		this_cart.addGame(newgame)

	amount = this_cart.game.all().count()
	games = this_cart.game.all()

	totalGameList = zip(games, RewardFormSet)

	totalAmount = this_cart.getTotal()
	form = PlatformForm(request.POST)
	RewardFormSet = formset_factory(RewardChoosingForm,extra=amount)
	formset = RewardFormSet()
	rewardAmount = Reward.numberOfReward(user)
	ran = []
	i = 0
	for f in formset:
		ran.append(games[i])
		ran.append(f.as_table())
		i= i + 1
	return render(request, 'fume/purchase.html', {'games': games,


'amount': amount, 'totalAmount': totalAmount,"form":form, 'cart': this_cart,'rewardAmount':rewardAmount,'formset':RewardFormSet,'range':ran})


def deleteGame(request, game_id, cart_id):
	thiscart=Cart.objects.get(id=cart_id)
	thiscart.deleteItem(game_id)
	return redirect('purchase', 0)

@login_required
def purchaseAll(request):
	user = request.user
	print(user)
	cart = Cart.objects.get(user=user)
	game = cart.getGameList()

	form = PlatformForm(request.POST)
	platform = form['platform'].data
	print(platform)

	platformObj = Platform.objects.get(PlatformName=platform)
	ptime = datetime.now()
	newPurchase = Purchase(pTime=ptime,userId=user,platform=platformObj)
	oldspent = Purchase.getSpentAmount(user)
	neededAmount = Reward.getAmountToNextReward(user)
	newPurchase.save()
	newPurchase.addGame(cart)
	newspent = Purchase.getSpentAmount(user)
	if newspent - oldspent - neededAmount > 0:
		r = Reward(user=user,amount=1)
		r.receiveReward()
	newRewardAmount = ((newspent-oldspent) - neededAmount)/100
	newRewardAmount = int(newRewardAmount)
	if newRewardAmount > 0:
		for i in range(newRewardAmount):
			r = Reward(user=user,amount=1)
			r.receiveReward()
	cart.clearCart()
	return redirect('featured')

def tagedit(request, game_id):
	tag_id=game_id
	return render(request, 'fume/tag.html', {'tag_id':game_id})

@login_required
def home(request):
    return render(request, 'fume/featured.html',{})

@login_required
def addtag(request, game_id):
	user = request.user
	print(user)
	print ("adding tag")
# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:

		form = NameForm(data = request.POST)
		# check whether it's valid:
		print(form.is_valid())
		if form.is_valid():
				# process the data in form.cleaned_data as required
				# ...

			tag = form['tag_name'].data;
			creator = user
			this_game = Game.objects.get(game_id=game_id)
			#creator = request.POST.get('creator','')
			this_game.addTag(tag,creator)

			print ("tag added")

			# redirect to a new URL:
		return redirect('games',game_id=game_id)


	# if a GET (or any other method) we'll create a blank form
	else:
		return redirect('games',game_id=game_id)


def featured(request):
	currentUser = request.user
	# Get featured game list for general users
	ftr = FeaturedGame.objects.all().filter(title="ftr")[0]
	ftrList = Game.objects.all().filter(featuredGame=ftr)

	if request.user.is_authenticated():
		# Get recommended game list for individual user
		recmd = Recommendation(userId=currentUser)
		rcmdList = recmd.getRecommendationList()

		#Print Rewards
		rewards = Reward.getAllRewards(currentUser)
		amountToNextReward = Reward.getAmountToNextReward(currentUser)
	else:
		recmd = None
		rcmdList = None
		rewards = None
		amountToNextReward = None

	return render(request, 'fume/featured.html', {'ftrList':ftrList,'rcmdList':rcmdList, 'rewards':rewards,'amountToNextReward':amountToNextReward})

@login_required
def browse(request):
	currentUser = request.user
	tags = Tag.objects.all()
	games = Purchase.objects.all().filter(userId=currentUser).all()
	#imageList = game.getImageList()
	#image1 = imageList[0]
	return render(request, 'fume/browse.html', {'tags':tags, 'games':games})

@login_required
def browseBy(request, tag_id):
	currentUser = request.user
	allTags = Tag.objects.all()
	tag = Tag.objects.filter(id=tag_id)[0]
	#imageList = game.getImageList()
	#image1 = imageList[0]
	return render(request, 'fume/browseBy.html', {'allTags':allTags, 'tag':tag})
