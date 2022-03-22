![license](https://img.shields.io/badge/license-MIT-brightgreen?style=flat-square)
<a href="https://alexguidace.github.io/">
    <img alt="Portfolio Website Badge" src="https://img.shields.io/badge/Portfolio-alexguidace.github.io-brightgreen?style=flat-square">
</a>

# **E-Commerce Website**

# Description
A web application focusing mainly on the backend using Python and Django.

Through this ebay-like app, you can do many of the things an ebay user would be able to do: post items to bid on, view items, bid on items, add and remove items to and from your watchlist, and browse categories for items.

I built this project for [Harvard CS50's Web Course](https://cs50.harvard.edu/web/2020/), a hands-on course that teaches students how to build websites.

[Click here to watch a video demo of this app.](https://www.youtube.com/watch?v=IGk8WadB1Gs)
#

# Project Files
The following links contain summary overviews of each file created or modified by me in the project. Please refer to a file's code directly for specific implementation and details regarding that file.

* [models.py](#models.py)
* [admin.py](#admin.py)
* [urls.py](#urls.py)
* [views.py](#views.py)
* [categories.html](#categories.html)
* [listing.html](#listing.html)
* [success.html](#success.html)
* [watchlist.html](#watchlist.html)
* [category_listings.html](#category_listings.html)
* [create_listing.html](#create_listing.html)
* [index.html](#index.html)
* [layout.html](#layout.html)

## models.py
Where we store the Django models used for the website.

## admin.py
Where we register our models.

## urls.py
Where we store our url paths in order to manage different views.

## views.py
Where we store the functions that give the website its main functionality.

## categories.html
A page that displays a list of clickable categories. Each link takes the user to a page
that displays all active listings in the respective category.

## listing.html
A page that is reached from clicking on an active listing. Shows all details about an
individual listing.

## success.html
A message that alerts the user after they've successfully taken an action.

## watchlist.html
A page that displays a logged-in user's watchlist.

## category_listings.html
Shows all active listings belonging to a category.

## create_listing.html
A page that allows a logged-in user to create a new listing.

## index.html
The homepage showing all active listings.

## layout.html
The foundational page for all other html files.

# License & Copyright
© Alex Guidace

Licensed under the [MIT License](License).
