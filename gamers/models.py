from django.db import models

# Create your models here.

class Gamer_ID(models.Model):
    user = models.IntegerField(primary_key=True)

    def __str__(self):
        return f"{self.user}"

class Platform(models.Model):
    platform = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.platform}"

class Category(models.Model):
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category}"

class Game(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10, null=True, blank=True)
    category = models.ManyToManyField(Category)
    plateforms = models.ManyToManyField(Platform)
    users = models.ManyToManyField(Gamer_ID, blank=True)

    def __str__(self):
        return f"{self.name}"


class Friend(models.Model):
    user = models.ForeignKey(Gamer_ID, related_name="friend_user", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"

class Friend_Request(models.Model):
    user = models.ForeignKey(Gamer_ID, related_name="friend_request_user", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"

class Message(models.Model):
    sender = models.ForeignKey(Gamer_ID, related_name="chat_sender", on_delete=models.CASCADE)
    message = models.CharField(max_length=400)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    broadcasted = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('timestamp',)

class Chat(models.Model):
    user1 = models.ForeignKey(Gamer_ID, related_name="chat_user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(Gamer_ID, related_name="chat_user2", on_delete=models.CASCADE)
    messages = models.ManyToManyField(Message)

class Gamer(models.Model):
    id = models.IntegerField(primary_key=True)
    pp = models.ImageField(upload_to="pp/", blank=True, null=True)
    bio = models.CharField(max_length=150, default="")
    games = models.ManyToManyField(Game, blank=True)
    friends = models.ManyToManyField(Friend, blank=True)
    chats = models.ManyToManyField(Chat)
    sent_friend_requests = models.ManyToManyField(Friend_Request, blank=True)
    my_friend_requests = models.ManyToManyField(Friend_Request, related_name="my_friend_request_user", blank=True)

    def __str__(self):
        return f"{self.id}"