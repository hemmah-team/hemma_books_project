from django.db import models

# Create your models here.
from account.models import User
from products.models import Product


class Conversation(models.Model):
    chatter = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="chatter", null=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="product_chatter",
    )

    support = models.BooleanField(default=False)


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    text = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to="media")
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
