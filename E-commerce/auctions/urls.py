from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_form, name="create"),
    path("listings/<int:listing_id>/add_watchlist", views.add_watchlist, name="add_watchlist"),
    path("listings/<int:listing_id>/remove_watchlist", views.remove_watchlist, name="remove_watchlist"),
    path("listings/<int:listing_id>/add_bid", views.add_bid, name="add_bid"),
    path("listings/<int:listing_id>/close_listing", views.close_listing, name="close_listing"),
    path("listings/<int:listing_id>/reopen_listing", views.reopen_listing, name="reopen_listing"),
    path("listings/<int:listing_id>/add_comment", views.add_comment, name="add_comment"),
    path("listings/<int:listing_id>/comments", views.comments, name="comments"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category")
]
