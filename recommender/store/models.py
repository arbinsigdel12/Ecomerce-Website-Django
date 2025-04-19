from django.utils import timezone 
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) 
    purchase_date = models.DateTimeField(auto_now_add=True) 
    
    class Meta:
        unique_together = ('user', 'product') 
    
    def __str__(self):
        return f"{self.user.username}'s purchase of {self.product.name}"

class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # Now this will work
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - {self.get_rating_display()} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Feedback"