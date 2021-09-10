# Our database tables.

from django.contrib.auth.models import AbstractUser
from django.db import models

# Default primary key (ID) is provided by Django for each model created.
# Each class variable is a column in our table.

# A table for users that inherits from an abstract User class.
class User(AbstractUser):
    # Primary Key ID.

    # Username.
    username = models.CharField(max_length=30, unique=True)
    # Password.
    password = models.CharField(max_length=30)
    # Email address.
    email = models.EmailField()
    

# A table for auction listings.
class AuctionListing(models.Model):
    # Primary Key ID.

    # User ID (Foreign Key from User).
    # (models.Foreignkey() references another table.) 
    # (on_delete=models.CASCADE will delete this user_ID from 
    # the table, should the associated user that is referenced 
    # in the User table through this user_ID, be deleted themselves.)
    user_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    # Title.
    title = models.CharField(max_length=300)
    # Description.
    description = models.CharField(max_length=2000)
    # Current Price.
    current_price = models.DecimalField(max_digits=8, decimal_places=2)
    # Image URL.
    image_URL = models.CharField(max_length=300)
    # Status of listing (whether or not someone has won the bid--open or closed).
    status = models.CharField(max_length=10, default="ACTIVE")
    # Category.
    category = models.CharField(max_length=20, default="TBD")
    # The winner of a bid.
    winner = models.CharField(max_length=300, default="TBD")


# A table for listings a user is watching.
class WatchList(models.Model):
    # Primary Key ID.

    # FK to User table. This user is the owner of this WatchList.
    user_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    # FK to AuctionListing's table.
    # If the AuctionListing is deleted, delete this listing from the WatchList.
    single_listing_watched = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="listings_watched")


# A table for item bids.
class Bid(models.Model):
    # Primary Key ID.

    # User ID (Foreign Key) of bidder.
    user_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    # Listing that was bid on (Foreign Key).
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    # Amount bid by the bidder.
    amount_bid = models.DecimalField(max_digits=8, decimal_places=2)


# A table for user comments on listings.
class ListingComment(models.Model):
    # Primary Key ID.

    # User ID (Foreign Key).
    user_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    # Listing (Foreign Key).
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    # Comment.
    comment = models.CharField(max_length=300)