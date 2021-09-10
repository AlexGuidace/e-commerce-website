from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing, WatchList, Bid, ListingComment

from django.contrib.auth.decorators import login_required
from django import forms


#####################################
############### Forms ###############
#####################################


# A form that creates a blank form for a user to create a new listing.
class ListingForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea())
    starting_bid = forms.DecimalField(min_value=0)
    image_URL = forms.URLField(max_length=200)

    # Tuples of categories a user can choose from when they create a listing.
    CATEGORIES = (
        ("1", "Food"),
        ("2", "Home Appliances"),
        ("3", "Health"),
        ("4", "Tools"),
        ("5", "Books"),
        ("6", "Entertainment"),
        ("7", "Clothing"),
        ("8", "Sporting Goods")
    )

    category = forms.ChoiceField(choices=CATEGORIES)


# A form for making bids.
class BidForm(forms.Form):
    bid = forms.DecimalField(min_value=0)


#########################################
############### Functions ###############
#########################################


# Renders all active listings on the homepage.
def index(request):
    all_listings = AuctionListing.objects.all()
    listings = []

    for row in all_listings:
        # If the listing isn't closed, we will add it to the list of listings to be returned to the user.
        # The listing will still be available for a user to view if they have saved it to their watchlist.
        if not is_closed(row):
            listings.append(row)
            
    return render(request, "auctions/index.html", {
        "listings": listings
    })


# Logs in a user.
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


# Logs out a user.
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Registers a new user.
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
    else:
        return render(request, "auctions/register.html")


# Returns a page that shows all listings in a category, as well as the title of the category.
def category_listings(request, category):
    all_listings = AuctionListing.objects.all()
    listings = []

    for row in all_listings:
        category_field = row.category
        # If the listing isn't closed and the category passed in is equivalent to this row's category field, we will add 
        # it to the list of listings to be returned to the user.
        if not is_closed(row) and category_field == category:
            listings.append(row)
            
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })


# Returns a list of clickable listing category links to the user.
def categories(request):
    categories = [
        "Food",
        "Home Appliances",
        "Health",
        "Tools",
        "Books",
        "Entertainment",
        "Clothing",
        "Sporting Goods"
    ]
    
    return render (request, "auctions/categories.html", {
        "categories": categories
    })


# Renders a page that allows the user to create a new listing.
@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            # Get current user.
            user_ID = request.user

            # Get cleaned-up data fields from the submitted form.
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            current_price = form.cleaned_data["starting_bid"]
            image_URL = form.cleaned_data["image_URL"]
            category = form.cleaned_data["category"]
            # Make sure we have the English-language category and not just its number. I.E., "food" instead of "3".
            category = dict(form.fields["category"].choices)[category]
            
            # Instantiate a row that will contain the listing's data in our AuctionListing table.
            listing = AuctionListing()
            # Give cleaned fields to the AuctionListing table for this row.
            listing.user_ID = user_ID
            listing.title = title
            listing.description = description
            listing.current_price = current_price
            listing.image_URL = image_URL
            listing.category = category
            # Set the status of the item to ACTIVE.
            listing.status = "ACTIVE"
            # Save the row to the table.
            listing.save()

            return render(request, "auctions/success.html")

    # GET a blank listing form.
    form = ListingForm()
    return render (request, "auctions/create_listing.html", {
        "form": form
    })


# Gets a specific listing to display to the user.
def get_listing(request, listing_id):
    # See if currently logged-in user is the owner of the listing. If they are, the "Add to watchlist" button
    # will not be displayed.
    not_owner = is_owner(request, listing_id)
    # See if user needs the Remove button. If they do, we will return it the HTML.
    remove = watched(request, listing_id)

    # Send all listing information to listing.html for GET request. Dependent on ID that is passed in.
    listing = AuctionListing.objects.get(id=listing_id)

    closed = is_closed(listing)
    comments = ListingComment.objects.all()

    listing_comments = []
    for comment in comments:
        if comment.listing == listing:
            listing_comments.append(comment)

    return render (request, "auctions/listing.html", {
        "not_owner": not_owner,
        "remove": remove,
        "image_URL": listing.image_URL,
        "id": listing.id,
        "poster": listing.user_ID,
        "title": listing.title,
        "description": listing.description,
        "price": listing.current_price,
        "category": listing.category,
        "status": listing.status,
        "closed": closed,
        "winner": listing.winner,
        "comments": listing_comments
    })
    

# Adds a listing to a user's watchlist.
@login_required
def add_listing(request, listing_id):
    # Send all listing information to listing.html for GET request.
    # Dependent on ID that is passed in.
    listing = AuctionListing.objects.get(id=listing_id)
    user = request.user

    # Add listing to user's watchlist.
    # Create a row that will be part of the watchlist for this user.
    watchlist = WatchList()
    watchlist.user_ID = user
    # The listing ID that was passed in.
    watchlist.single_listing_watched = AuctionListing.objects.get(pk=listing_id)
    watchlist.save()

    # Render the remove button to the HTML once the user adds the listing to their watchlist.
    remove = watched(request, listing_id)
    closed = is_closed(listing)
    not_owner = is_owner(request, listing_id)
    comments = ListingComment.objects.all()

    listing_comments = []
    for comment in comments:
        if comment.listing == listing:
            listing_comments.append(comment)

    # Return GET page signifying that the listing was added to the user's watchlist. 
    return render (request, "auctions/listing.html", {
        "remove": remove,
        "not_owner": not_owner,
        "added": "Successfully added to watchlist!",
        "image_URL": listing.image_URL,
        "id": listing.id,
        "poster": listing.user_ID,
        "title": listing.title,
        "description": listing.description,
        "price": listing.current_price,
        "category": listing.category,
        "status": listing.status,
        "closed": closed,
        "winner": listing.winner,
        "comments": listing_comments
    })


# Removes a listing from the user's watchlist and returns the GET page.
@login_required
def remove(request, listing_id):
    # Call watched() to get the value of remove. If remove is true that means we have an item in the watchlist
    # that can be removed.
    remove = watched(request, listing_id)

    user = request.user
    # If remove variable is set to true, then we remove the listing from a user's watchlist
    # when the user clicks the button. The user is then sent back to the GET page.
    if remove:
        for row in WatchList.objects.all():
            if row.user_ID == user and row.single_listing_watched.id == listing_id:
                primary_key = row.id
                WatchList.objects.filter(id=primary_key).delete()

    return get_listing(request, listing_id)


# A function that allows a logged-in user to make a bid on a listing.
@login_required
def bid(request, listing_id):

    listing = AuctionListing.objects.get(id=listing_id)
    comments = ListingComment.objects.all()

    listing_comments = []
    for comment in comments:
        if comment.listing == listing:
            listing_comments.append(comment)

    if request.user.is_authenticated:
        if request.method == "POST":
            form = BidForm(request.POST)
            if form.is_valid():
                # Get current user.
                user = request.user

                # Get the submitted bid int.
                amount = form.cleaned_data["bid"]

                # Check to see that the amount passed in is greater than the current listing price.
                # If it less than or equal to the current listing price, we pass back an error message with the
                # rest of the HTML page and its required variables.
                not_enough = enough(amount, listing_id)
                not_owner = is_owner(request, listing_id)
                remove = watched(request, listing_id)
                closed = is_closed(listing)

                if not_enough:
                    return render (request, "auctions/listing.html", {
                        "not_owner": not_owner,
                        "remove": remove,
                        "not_enough": not_enough,
                        "image_URL": listing.image_URL,
                        "id": listing.id,
                        "poster": listing.user_ID,
                        "title": listing.title,
                        "description": listing.description,
                        "price": listing.current_price,
                        "category": listing.category,
                        "status": listing.status,
                        "closed": closed,
                        "comments": listing_comments
                    })
                
                # Otherwise, the amount is greater than the current listing price, so we put a record of it
                # in our Bid table and change the current price to this bid price in our AuctionListings table.
                # This bid will be greater than any other bid in the table for this listing by necessity of it 
                # having to be larger than the current price.
                # Add new row to bids table for this bid.
                bid = Bid()
                bid.user_ID = user
                # The listing ID that was passed in.
                bid.listing = AuctionListing.objects.get(pk=listing_id) 
                # Amount bid.
                bid.amount_bid = amount
                bid.save()
                # Change the current_price of this listing to the bid amount and display the new amount,
                # along with a success message.
                listing.current_price = amount
                listing.save(update_fields=['current_price'])

                # Ensure the table was updated and return the HTML page.
                if listing.current_price == amount:
                    updated = True

                    closed = is_closed(listing)
                
                    return render (request, "auctions/listing.html", {
                            "updated": updated,
                            "not_owner": not_owner,
                            "remove": remove,
                            "not_enough": not_enough,
                            "image_URL": listing.image_URL,
                            "id": listing.id,
                            "poster": listing.user_ID,
                            "title": listing.title,
                            "description": listing.description,
                            "price": listing.current_price,
                            "category": listing.category,
                            "status": listing.status,
                            "closed": closed,
                            "winner": listing.winner,
                            "comments": listing_comments
                        })
            # If nothing entered in the form, set amount from None to zero, and return warning to user.
            else:
                amount = 0
                not_enough = enough(amount, listing_id)
                listing = AuctionListing.objects.get(id=listing_id)
                not_owner = is_owner(request, listing_id)
                remove = watched(request, listing_id)
                closed = is_closed(listing)
                if not_enough:
                    return render (request, "auctions/listing.html", {
                        "not_owner": not_owner,
                        "remove": remove,
                        "not_enough": not_enough,
                        "image_URL": listing.image_URL,
                        "id": listing.id,
                        "poster": listing.user_ID,
                        "title": listing.title,
                        "description": listing.description,
                        "price": listing.current_price,
                        "category": listing.category,
                        "status": listing.status,
                        "closed": closed,
                        "comments": listing_comments
                    })
  

# Allows owner to close their listing and announce the highest bidder as the winner.
@login_required
def close(request, listing_id):
    # Set the status of this listing to CLOSED in AuctionListings table.
    listing = AuctionListing.objects.get(id=listing_id)
    listing.status = "CLOSED"
    listing.save(update_fields=['status'])

    not_owner = is_owner(request, listing_id)
    remove = watched(request, listing_id)
    closed = is_closed(listing)
    comments = ListingComment.objects.all()

    listing_comments = []
    for comment in comments:
        if comment.listing == listing:
            listing_comments.append(comment)

    # Fetch the highest bidder based on the highest bid in the bids table.
    listing_bids = []
    for row in Bid.objects.all():
        if row.listing == listing:
            listing_bids.append(row.amount_bid)
    
    # If no one has bid on the listing yet, allow the owner to close the listing anyway.
    if len(listing_bids) == 0:
        return render (request, "auctions/listing.html", {
            "winner": listing.winner,
            "closed": closed,
            "not_owner": not_owner,
            "remove": remove,
            "image_URL": listing.image_URL,
            "id": listing.id,
            "poster": listing.user_ID,
            "title": listing.title,
            "description": listing.description,
            "price": listing.current_price,
            "category": listing.category,
            "status": listing.status,
            "comments": listing_comments
        })

    listing_bids.sort(reverse=True)

    # Select the winning bid, and find the user who has that bid amount for this listing.
    winning_bid = listing_bids[0]
    for row in Bid.objects.all():
        if row.listing == listing and row.amount_bid == winning_bid:
            winner = str(row.user_ID)
    
    # Update the listing's row in the DB with the winner.
    listing.winner = winner
    listing.save(update_fields=['winner'])

    return render (request, "auctions/listing.html", {
        "winner": listing.winner,
        "closed": closed,
        "not_owner": not_owner,
        "remove": remove,
        "image_URL": listing.image_URL,
        "id": listing.id,
        "poster": listing.user_ID,
        "title": listing.title,
        "description": listing.description,
        "price": listing.current_price,
        "category": listing.category,
        "status": listing.status,
    })


# Enables the logged-in user to make a comment on a listing and returns updated comments.
@login_required
def comment(request, listing_id):
    comments = ListingComment.objects.all()
    listing = AuctionListing.objects.get(id=listing_id)
    not_owner = is_owner(request, listing_id)
    remove = watched(request, listing_id)
    closed = is_closed(listing)

    if request.method == "POST":
            # Get current user.
            user_ID = request.user

            # Get cleaned-up data fields from the submitted form.
            comment_text = request.POST.get('textarea')
            
            # Instantiate and populate a row that will contain the comment's data in our ListingComment table.
            comment = ListingComment()
            comment.user_ID = user_ID
            comment.listing = listing
            comment.comment = comment_text
            comment.save()

            listing_comments = []
            for comment in comments:
                if comment.listing == listing:
                    listing_comments.append(comment)

            # Return all comments with the updated comment to the listing page.
            return render(request, "auctions/listing.html", {
                        "not_owner": not_owner,
                        "remove": remove,
                        "image_URL": listing.image_URL,
                        "id": listing.id,
                        "poster": listing.user_ID,
                        "title": listing.title,
                        "description": listing.description,
                        "price": listing.current_price,
                        "category": listing.category,
                        "status": listing.status,
                        "closed": closed,
                        "comments": listing_comments
            })

    # GET all of the listing's comments from the DB.
    listing_comments = []
    for comment in comments:
        if comment.listing == listing:
            listing_comments.append(comment)

    return render (request, "auctions/listing.html", {
        "not_owner": not_owner,
        "remove": remove,
        "image_URL": listing.image_URL,
        "id": listing.id,
        "poster": listing.user_ID,
        "title": listing.title,
        "description": listing.description,
        "price": listing.current_price,
        "category": listing.category,
        "status": listing.status,
        "closed": closed,
        "comments": listing_comments
    })


# Returns a user's watchlist to them.
@login_required
def watchlist(request):
    user_ID = request.user

    # Get all rows watched by the logged-in user.
    listings = []
    for row in WatchList.objects.all():
        if row.user_ID == user_ID:
            # This row's single_listing_watched field's foreign key is the primary key of the actual listing,
            # so we can reference that listing and all its fields through that foreign key id.
            listing = AuctionListing.objects.get(pk=row.single_listing_watched.id)
            # We then attach that referenced listing to a list to be used in the Django templating language.
            listings.append(listing)
            
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


################################################
############### Helper Functions ###############
################################################ 


# Helper function to define if a listing is closed or not.
def is_closed(listing):
    closed = False
    if listing.status == "CLOSED":
        closed = True

    return closed


# Helper function for bid() fuction that determines if an amount of a bid is greater than the current 
# listing price of a listing.
def enough(amount, listing_id):
    if amount <= AuctionListing.objects.get(pk=listing_id).current_price or amount is None:
        not_enough = True
    else:
        not_enough = False
        
    return not_enough


# A helper function that defines whether the listing is already in the user's watchlist, if it's already being "watched".
def watched(request, listing_id):
    # If the table is empty, give remove a value of false.
    if not WatchList.objects.exists():
            remove = False

    user = request.user

    for row in WatchList.objects.all():
        if row.user_ID == user and row.single_listing_watched.id == listing_id:
            remove = True
            return remove
        else:
            remove = False
    
    return remove


# A helper function that determines if a page listing is owned by the currently logged-in user.
def is_owner(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    user = request.user

    # If the user_id of the page listing is not equivalent to the user id of the logged-in user,
    # then we return a boolean signifying that we should add a "Add to Watchlist" button in
    # the HTML since the logged-in user doesn't own the page listing.
    if not listing.user_ID == user:
        not_owner = True
    else:
        not_owner = False

    return not_owner
