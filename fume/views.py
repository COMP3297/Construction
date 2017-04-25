
from django.shortcuts import render,redirect

# Create your views here.
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from fume.models import Game,Cart,Tag,User,Recommendation,Purchase,Platform,getUserPurchaseHistory,Reward,Recommendation
from fume.forms import LoginForm,NameForm,PlatformForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from fume.forms import SignUpForm
from django.contrib.auth.decorators import login_required




def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('home')
	else:
		form = SignUpForm()
	return render(request, 'registration/signup.html', {'form': form})

@login_required
def games(request, game_id):
	game = Game.objects.get(game_id=game_id)
	tags = Tag.objects.filter(game=game).all()
	imageList = game.getImageList()
	image1 = imageList[0]
	image2 = imageList[1]
	return render(request, 'fume/gamePage.html', {'tag_id':game_id, 'tags':tags,'game':game,'image1':image1,'image2':image2})

@login_required
def purchase(request, game_id):
	print("purchasing")
	user_id=request.user

	newgame=Game.objects.get(game_id=game_id)
	user = request.user
	print(user)
	try:
		this_cart = Cart.objects.get(user = user)
	except:
		this_cart = Cart(user = user)
		this_cart.save()
	this_cart.addGame(newgame)
	amount = this_cart.game.all().count()
	games = this_cart.game.all()
	totalAmount = this_cart.getTotal()
	form = PlatformForm(request.POST)

	return render(request, 'fume/purchase.html', {'games': games, 'amount': amount, 'totalAmount': totalAmount,"form":form})

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
	newPurchase.save()
	newPurchase.addGame(cart)

	cart.clearCart()
	return redirect('featured')

def tagedit(request, game_id):
	tag_id=game_id
	return render(request, 'fume/tag.html', {'tag_id':game_id})

@login_required
def home(request):
    return render(request, 'home.html')

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

@login_required
def featured(request):

	currentUser = request.user
	recmd = Recommendation(userId=currentUser)
	rcmdList = recmd.getRecommendationList()
	#Print Rewards
	try:
		rewards=Reward.objects.get(user=currentUser).amount
	except:
		rewardForNewuser=Reward(user=currentUser,amount=18)
		rewardForNewuser.receiveReward()
		rewards=rewardForNewuser
	amountToNextReward = Reward.getAmountToNextReward(currentUser)
	return render(request, 'fume/featured.html', {'rcmdList':rcmdList, 'rewards':rewards,'amountToNextReward':amountToNextReward})
