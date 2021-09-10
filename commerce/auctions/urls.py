from django.urls import path

from . import views

urlpatterns = [
    # Homepage.
    path("", views.index, name="index"),
    # Log in a user.
    path("login", views.login_view, name="login"),
    # Log out a user.
    path("logout", views.logout_view, name="logout"),
    # Register a new user.
    path("register", views.register, name="register"),
    # Allow the user to create a new listing.
    path("create_listing", views.create_listing, name="create_listing"),
    # Get an individual listing.
    path("<int:listing_id>/get_listing", views.get_listing, name="get_listing"),
    # Add listing to a user's watchlist.
    path("<int:listing_id>/add_listing", views.add_listing, name="add_listing"),
    # Removes listing from WatchList table for a particular user.
    path("<int:listing_id>/remove", views.remove, name="remove"),
    # Allow the user to make a bid on a listing.
    path("<int:listing_id>/bid", views.bid, name="bid"),
    # Closes a bid.
    path("<int:listing_id>/close", views.close, name="close"),
    # Enables comments.
    path("<int:listing_id>/comment", views.comment, name="comment"),
    # Get a user's watchlist.
    path("watchlist", views.watchlist, name="watchlist"),
    # Displays a page with listing categories.
    path("categories", views.categories, name="categories"),
    # Get all active listings for a particular category.
    path("<str:category>/category_listings", views.category_listings, name="category_listings"),
]
