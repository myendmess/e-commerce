from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from datetime import datetime
from .models import User, Listing, Bid, Comment, Watchlist, Category


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
   
    return render(request, "auctions/register.html")


@login_required
def create_form(request):
    if request.method == "POST" :
        # create listing, save data to db, then redirect to listing page
        if request.POST.get("category"):
            category_name = request.POST.get("category")
            listing = Listing(
                title=request.POST.get("title"), 
                active=True,
                description=request.POST.get("description"), 
                starting_bid=request.POST.get("starting_bid"),
                img_url=request.POST.get("img_url"),
                category=Category.objects.filter(name=category_name)[0],
                list_create_time=datetime.now(),
                author=request.user,
                )
            listing.save()
            return redirect(f"/listings/{listing.id}")
        else:
            listing = Listing(
                title=request.POST.get("title"), 
                active=True,
                description=request.POST.get("description"), 
                starting_bid=request.POST.get("starting_bid"),
                img_url=request.POST.get("img_url"),
                category=None,
                list_create_time=datetime.now(),
                author=request.user,
                )
            listing.save()
            return redirect(f"/listings/{listing.id}")
    
    return render(request, "auctions/create_form.html", {})


@login_required
def add_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    # Add to Watchlist if not existing with current logged in user + listing_id
    has_watchlist = Watchlist.objects.filter(listing=listing, user=request.user).exists()
    if has_watchlist:
        return redirect(f"/listings/{listing_id}")
    
    watchlist = Watchlist(
        user = request.user,
        listing = listing,
    )
    watchlist.save()
    return redirect(f"/listings/{listing_id}")


@login_required
def remove_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    updated_listing = Watchlist.objects.filter(listing_id=listing_id).delete()
    # Remove from Watchlist if already existing with current logged in user + listing_id
    has_watchlist = Watchlist.objects.filter(listing=listing, user=request.user).exists()
    if has_watchlist:
        watchlist = Watchlist(
            user = request.user,
            listing = updated_listing,
        )
        watchlist.save()
        return redirect(f"/listings/{listing_id}")

    return redirect(f"/listings/{listing_id}")


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    top_bid = Bid.objects.filter(listing_id = listing_id).order_by("price").last()

    if request.user.is_authenticated:
        # user needs to log in to see Watchlist
        has_watchlist = Watchlist.objects.filter(listing=listing, user=request.user).exists()
        return render(request, "auctions/one_listing.html",{
            "error": request.GET.get("error"),
            "top_bid": top_bid,
            "listing": listing,
            "has_watchlist": has_watchlist,
            "user": request.user,
            "comments": Comment.objects.filter(listing=listing_id),
            "active": listing.active,
        })

    return render(request, "auctions/one_listing.html",{
            "top_bid": top_bid,
            "listing": listing,
            "comments": Comment.objects.all(),
        })

   
     
@login_required
def add_bid(request, listing_id):
    # place bid on a listing when logged in
    listing = Listing.objects.get(pk=listing_id)
    top_bid = Bid.objects.filter(listing_id=listing_id).order_by("price").last()
    new_price = float(request.POST.get("price"))
    starting_bid = listing.starting_bid
    
    # New bid must be >= starting bid, and must be > any other bids that have been placed (if no bid, same as new bid) 
    if (top_bid is None and new_price >= starting_bid) or (top_bid and new_price > top_bid.price) :
        bid = Bid(
            price = new_price,
            bidder = request.user,
            listing = listing,
            bid_time = datetime.now(),
        )
        bid.save()
        return redirect(f"/listings/{listing_id}")  
    
    # If the bid doesn’t meet those criteria, the user should be presented with an error.
    if new_price < starting_bid or new_price <= top_bid.price:
        return redirect(f"/listings/{listing_id}?error=invalid_bid") 


@login_required
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    # able to close auction if is the author of the listing when logged in
    if listing.author == request.user:
        listing.active = False
        listing.save(update_fields=['active'])
        return redirect(f"/listings/{listing_id}")  
    else:
        return render(request, "auctions/error.html",{
            "message" : "Sorry, you don't have the permission to close this listing.",
        }) 


@login_required
def reopen_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if listing.author == request.user:
        listing.active = True
        listing.save(update_fields=["active"])
        return redirect(f"/listings/{listing_id}")  
    else:
        return render(request, "auctions/error.html",{
            "message" : "Sorry, you don't have the permission to reopen this listing.",
        }) 


@login_required
def add_comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    # create comment for a listing
    comment = Comment(
        commenter = request.user,
        title = request.POST.get("title"),
        content = request.POST.get("content"),
        comment_time = datetime.now(),
        listing = listing,
    )
    comment.save()
    return redirect(f"/listings/{listing_id}")  


def comments(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    # show comments of a listing on the listing page
    return render(request, "auctions/comments.html", {
        "comments": Comment.objects.filter(listing=listing_id),
        "listing": listing,
    })


@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "listings": [watchlist.listing for watchlist in Watchlist.objects.filter(user=request.user)],
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all(),
    })


def category(request, category_id):
    return render(request, "auctions/category.html", {
        "category": Category.objects.get(id=category_id).name,
        "active_listings": Listing.objects.filter(active=True, category_id=category_id),
    })