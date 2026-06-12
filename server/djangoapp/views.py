from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .restapis import analyze_review_sentiments, get_request, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": "", "status": "Logged out"})


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data.get("userName")
    password = data.get("password")
    first_name = data.get("firstName", "")
    last_name = data.get("lastName", "")
    email = data.get("email", "")

    if User.objects.filter(username=username).exists():
        return JsonResponse({"userName": username, "error": "Already Registered"})

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    login(request, user)
    return JsonResponse({"userName": username, "status": "Registered"})


# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    reviews = get_request(f"/fetchReviews/dealer/{dealer_id}")
    for review in reviews:
        review["sentiment"] = analyze_review_sentiments(review.get("review", ""))
    reviews = sorted(reviews, key=lambda review: review.get("id", 0), reverse=True)
    return JsonResponse({"status": 200, "reviews": reviews})


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    dealer = get_request(f"/fetchDealer/{dealer_id}")
    return JsonResponse({"status": 200, "dealer": dealer})


# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request):
    review = json.loads(request.body)
    if request.user.is_authenticated:
        review["user_id"] = request.user.id
        review["name"] = (
            request.user.get_full_name()
            or review.get("name")
            or request.user.username
        )
    saved_review = post_review(review)
    return JsonResponse({"status": 200, "review": saved_review})


def get_cars(request):
    car_models = CarModel.objects.select_related("car_make").all()
    data = [
        {
            "CarMake": car_model.car_make.name,
            "CarModel": car_model.name,
            "CarYear": car_model.year,
            "CarType": car_model.type,
        }
        for car_model in car_models
    ]
    return JsonResponse({"status": 200, "CarModels": data})


def analyze_review(request, text):
    return JsonResponse({"sentiment": analyze_review_sentiments(text)})
