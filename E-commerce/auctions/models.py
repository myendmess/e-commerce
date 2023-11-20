from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name=models.CharField(max_length=30)


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=100)
    img_url = models.URLField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    list_create_time = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    starting_bid = models.DecimalField(max_digits=19, decimal_places=2)
    active = models.BooleanField(null=True)
    
    def __str__(self):
        return f"{self.id}: {self.title}"
    

class Bid(models.Model):
    price = models.DecimalField(max_digits=19, decimal_places=2)
    bid_time = models.DateTimeField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    

class Comment(models.Model):
    title = models.CharField(max_length=64)
    content = models.CharField(max_length=100)
    comment_time = models.DateTimeField()
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)


