from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from .models import *
from django.contrib.auth.models import User
from django import utils
import os
import requests
import json
from datetime import datetime

def index(request):
    if request.method =="GET":
        if not request.user.is_authenticated:
            return render(request, "login.html", {"page": "login"})

        try:
            gamer = Gamer.objects.get(pk=request.user.id)
        except Gamer.DoesNotExist:
            gamer = None

        contents = {
            "gamer": gamer
        }
        return render(request, "gamers.html", contents)
    else:
        if request.POST["type"] == "login":
            username = request.POST["username"]
            password = request.POST["password"]
            username = username.lower()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "login.html", {"loginmessage": "Invalid credentials", "page": "login"})
        else:
            username = request.POST["username"]
            password = request.POST["password"]
            cpassword = request.POST["confpassword"]
            firstname = request.POST["firstname"]
            lastname = request.POST["lastname"]
            email = request.POST["email"]
            username = username.lower()
            valid = False
            validemail = False

            if not firstname.isalpha() or not lastname.isalpha():
                return render(request, "login.html", {"regmessage": "Invalid name", "page": "register"})

            firstname = firstname.lower()
            firstname = firstname.capitalize()
            lastname = lastname.lower()
            lastname = lastname.capitalize()
            email = email.lower()

            try:
                oldusername = User.objects.get(username=username)
            except User.DoesNotExist:
                valid = True

            try:
                oldemail = User.objects.get(email=email)
            except User.DoesNotExist:
                validemail = True

            if len(username) < 6:
                return render(request, "login.html", {"regmessage": "Username is too short", "page": "register"})

            if valid == False:
                return render(request, "login.html", {"regmessage": "Username is taken", "page": "register"})
            
            if validemail == False:
                return render(request, "login.html", {"regmessage": "Email is already registered", "page": "register"})
                
            if password != cpassword:
                return render(request, "login.html", {"regmessage": "Passwords do not match", "page": "register"})

            if len(password) < 6:
                return render(request, "login.html", {"regmessage": "Password is too short", "page": "register"})

            if email == "" or firstname == "" or lastname == "":
                return render(request, "login.html", {"regmessage": "An input field is missing", "page": "register"})
            
            if not "@" in email:
                return render(request, "login.html", {"regmessage": "Email is not valid", "page": "register"})
            
            newuser = User.objects.create_user(username, email, password)
            newuser.first_name = firstname
            newuser.last_name = lastname
            newuser.save()
            login(request, newuser)
            newid = Gamer_ID(user=request.user.id)
            newid.save()
            newgamer = Gamer(id=request.user.id)
            newgamer.save()

            return HttpResponseRedirect(reverse("index"))
       
def logoutpage(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def update_profile(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"page": "login"})
    if request.method == "POST":
        update_image = True
        bio = request.POST["bio"]

        try:
            image = request.FILES.popitem()
            image = image[1][0]
        except KeyError:
            update_image = False

        
        
        try:
            gamer = Gamer.objects.get(pk=request.user.id)

            if update_image:
                gamer.pp.delete()
                gamer.pp = image

            gamer.bio = bio

        except Gamer.DoesNotExist:
            gamer = Gamer(id=request.user.id)

            if update_image:
                gamer.pp = image

            gamer.bio = bio
            
        if update_image:
            ff = file_format(gamer.pp.name)

            gamer.pp.name = str(request.user.id) + ff

        gamer.save()
        return JsonResponse({"success":"success"})
    else:
        return HttpResponseRedirect(reverse("index"))

def search_games_manage(request, game):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"page": "login"})

    game = " ".join(game.split())
    result = Game.objects.filter(name__icontains=game)
    usergames = Gamer.objects.get(pk=request.user.id)
    usergames = usergames.games.all()
    games = []
    
    for game in usergames:
        result = result.exclude(name=game.name)

    length = len(result)

    if length == 0:
        return HttpResponse(json.dumps(["false"]))

    for i in range(length):
        games.append([])
        games[i].append(result[i].id)
        games[i].append(result[i].name)
        if i == 9:
            break

    return HttpResponse(json.dumps(games))

def add_game(request, game):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"page": "login"})
    
    game = Game.objects.get(pk=game)
    gamer = Gamer.objects.get(pk=request.user.id)
    usergames = gamer.games.all()

    if game in usergames:
        return HttpResponseRedirect(reverse("index"))
    
    gamer.games.add(game)
    gamerid = Gamer_ID.objects.get(pk=request.user.id)
    game.users.add(gamerid)
    game.save()
    gamer.save()

    return HttpResponse("success")

def search_players_game(request, game, start, end):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"page": "login"})

    game = " ".join(game.split())
    result = Game.objects.filter(name__icontains=game)

    length = 0

    if len(result) != 0:
        users = result[0].users.all()
        for user in users:
            length += 1
    data = []

    index = 0

    if length == 0:
        return HttpResponse(json.dumps(["false"]))

    start = int(start)
    end = int(end)

    if (start + end) >= length:
        end =  length
    
    current_user = request.user.id
    current_user_friends = Gamer.objects.get(pk=current_user).friends.all()
    current_user_f_requests = Gamer.objects.get(pk=current_user).sent_friend_requests.all()
    current_user_my_f_requests = Gamer.objects.get(pk=current_user).my_friend_requests.all()

    sent_friend_requests = []
    l = len(current_user_f_requests)
    for i in range(l):
        sent_friend_requests.append(int(current_user_f_requests[i].user.user))

    my_friend_requests = []
    l = len(current_user_my_f_requests)
    for i in range(l):
        my_friend_requests.append(int(current_user_my_f_requests[i].user.user))
    
    my_friends = []
    l = len(current_user_friends)
    for i in range(l):
        my_friends.append(int(current_user_friends[i].user.user))

    for i in range(start, end):
        profile = int(users[i].user)
        if not profile == current_user:
            gamer = Gamer.objects.get(pk=profile)
            data.append([])
            data[index].append(result[0].name)
            if gamer.pp:
                data[index].append(gamer.pp.url)
            else:
                data[index].append("/static/hub.png")
            
            gamer_user = User.objects.get(pk=profile)
            data[index].append(gamer_user.username)
            data[index].append(gamer_user.first_name)
            data[index].append(gamer_user.last_name)
            data[index].append(profile)

            if profile in my_friends:
                data[index].append("Friends")
            elif profile in sent_friend_requests:
                data[index].append("Cancel Request")
            elif profile in my_friend_requests:
                data[index].append("Accept")
            else:
                data[index].append("Add Friend")

            index += 1

    return HttpResponse(json.dumps(data))

def users_manage(request, user, request_type):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"page": "login"})

    current_user = request.user.id
    user = int(user)

    if request_type == "Add Friend":
        
        current_id = Gamer_ID.objects.get(pk=current_user)
        target_id = Gamer_ID.objects.get(pk=user)
        current_gamer = Gamer.objects.get(pk=current_user)
        target_gamer = Gamer.objects.get(pk=user)

        try:
            current_user_fr = Friend_Request.objects.get(user=target_id)
        except Friend_Request.DoesNotExist:
            current_user_fr = Friend_Request(user=target_id)
            current_user_fr.save()
        
        try:
            target_user_fr = Friend_Request.objects.get(user=current_id)
        except Friend_Request.DoesNotExist:
            target_user_fr = Friend_Request(user=current_id)
            target_user_fr.save()

        if target_user_fr in target_gamer.my_friend_requests.all() or current_user_fr in current_gamer.sent_friend_requests.all():
            return HttpResponse(json.dumps(["false"]))
        
        try:
            target_friend = Friend.objects.get(user=target_id)
        except Friend.DoesNotExist:
            target_friend = Friend(user=target_id)
            target_friend.save()
        
        if target_friend in current_gamer.friends.all():
            return HttpResponse(json.dumps(["Friends"]))

        current_gamer.sent_friend_requests.add(current_user_fr)
        current_gamer.save()
        target_gamer.my_friend_requests.add(target_user_fr)
        target_gamer.save()

        return HttpResponse(json.dumps(["Cancel Request"]))
    
    elif request_type == "Cancel Request" or request_type == "Accept" or request_type == "Cancel" or request_type == "Remove":
        current_id = Gamer_ID.objects.get(pk=current_user)
        target_id = Gamer_ID.objects.get(pk=user)
        current_gamer = Gamer.objects.get(pk=current_user)
        target_gamer = Gamer.objects.get(pk=user)
        current_user_fr = Friend_Request.objects.get(user=target_id)
        target_user_fr = Friend_Request.objects.get(user=current_id)
        if request_type == "Cancel Request":
            current_gamer.sent_friend_requests.remove(current_user_fr)
            current_gamer.save()
            target_gamer.my_friend_requests.remove(target_user_fr)
            target_gamer.save()

            return HttpResponse(json.dumps(["Add Friend"]))
        
        current_gamer.my_friend_requests.remove(current_user_fr)
        current_gamer.save()
        target_gamer.sent_friend_requests.remove(target_user_fr)
        target_gamer.save()
        
        if request_type == "Cancel":
            return HttpResponse(json.dumps(["canceled"]))

        try:
            current_friend = Friend.objects.get(user=target_id)
        except Friend.DoesNotExist:
            current_friend = Friend(user=target_id)
            current_friend.save()

        try:
            target_friend = Friend.objects.get(user=current_id)
        except Friend.DoesNotExist:
            target_friend = Friend(user=current_id)
            target_friend.save()
        
        current_gamer.friends.add(current_friend)
        current_gamer.save()
        target_gamer.friends.add(target_friend)
        target_gamer.save()

        if request_type == "Remove":
            current_gamer.friends.remove(current_friend)
            current_gamer.save()
            target_gamer.friends.remove(target_friend)
            target_gamer.save()
            return HttpResponse(json.dumps(["removed"]))

        return HttpResponse(json.dumps(["Friends"])) 
    else:
        return HttpResponse(json.dumps(["Friends"]))

def my_frequests(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"page": "login"})
    
    gamer = Gamer.objects.get(pk=request.user.id)
    new_friends = gamer.my_friend_requests.all()
    data = []
    length = len(new_friends)
    index = 0
    ids = []

    if length == 0:
        return HttpResponse(json.dumps(["false"]))

    for i in range(length):
        current_id = int(new_friends[i].user.user)
        gamer = Gamer.objects.get(pk=current_id)
        data.append([])
        if gamer.pp:
            data[index].append(gamer.pp.url)
        else:
            data[index].append("/static/hub.png")
        
        gamer_user = User.objects.get(pk=current_id)
        data[index].append(gamer_user.username)
        data[index].append(gamer_user.first_name)
        data[index].append(gamer_user.last_name)
        data[index].append(current_id)
        index += 1
    
    return HttpResponse(json.dumps(data))

def my_friendlist(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"page": "login"})
    
    gamer = Gamer.objects.get(pk=request.user.id)
    friends = gamer.friends.all()
    data = []
    length = len(friends)
    index = 0
    ids = []

    if length == 0:
        return HttpResponse(json.dumps(["false"]))

    for i in range(length):
        current_id = int(friends[i].user.user)
        gamer = Gamer.objects.get(pk=current_id)
        data.append([])
        if gamer.pp:
            data[index].append(gamer.pp.url)
        else:
            data[index].append("/static/hub.png")
        
        gamer_user = User.objects.get(pk=current_id)
        data[index].append(gamer_user.username)
        data[index].append(gamer_user.first_name)
        data[index].append(gamer_user.last_name)
        data[index].append(current_id)
        index += 1
    
    return HttpResponse(json.dumps(data))

def chat_channel(request, type, channel):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"page": "login"})
    
    target_user = parse_users(channel)
    current_user = request.user.id

    if not target_user:
        return HttpResponse(json.dumps(["false"]))
    
    current_id = Gamer_ID.objects.get(pk=current_user)
    target_id = Gamer_ID.objects.get(pk=target_user)
    current_gamer = Gamer.objects.get(pk=current_user)
    chats = current_gamer.chats.all()
    chat = current_chat(chats, current_id, target_id, current_user, target_user)
    if type == "socket":
        messages = chat.messages.filter(broadcasted=False).all()
    else:
        messages = chat.messages.all()
    length = len(messages)

    if length == 0:
        return HttpResponse(json.dumps([]))

    new_messages = []
    index = 0

    if type == "socket":
        for i in range(length):
            if not (current_id == messages[i].sender):
                new_messages.append([])
                new_messages[index].append(messages[i].message)
                new_messages[index].append(False)
                messages[i].broadcasted = True
                messages[i].save()
                index += 1
    else:
        if length > 50:
            start = length - 50
        else:
            start = 0

        for i in range(start, length):
            new_messages.append([])
            new_messages[index].append(messages[i].message)
            if current_id == messages[i].sender:
                new_messages[index].append(True)
            else:
                new_messages[index].append(False)
            messages[i].broadcasted = True
            messages[i].save()
            index += 1
    
    return HttpResponse(json.dumps(new_messages))

def chat_message(request, user):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"page": "login"})
    if request.method == "POST":
        try:
            target_user = int(user)
        except KeyError:
            return HttpResponse(json.dumps(["false"]))

        message = request.POST["message"]

        current_user = request.user.id
        current_id = Gamer_ID.objects.get(pk=current_user)
        target_id = Gamer_ID.objects.get(pk=target_user)
        current_gamer = Gamer.objects.get(pk=current_user)
        target_gamer = Gamer.objects.get(pk=target_user)
        chats = current_gamer.chats.all()
        chat = current_chat(chats, current_id, target_id, current_user, target_user)


        message = Message(sender=current_id, message=message)
        message.save()
        chat.messages.add(message)
        chat.save()

        return HttpResponse(json.dumps(["false"]))
    else:
        return HttpResponse(json.dumps(["false"]))

def current_chat(chats, current_id, target_id, current_user, target_user):
    length = len(chats)

    condition = True
    for i in range(length):
        if (chats[i].user1 == current_id and chats[i].user2 == target_id) or (chats[i].user1 == target_id and chats[i].user2 == current_id):
            chat = chats[i]
            condition = False

    if condition:
        chat = Chat(user1=current_id, user2=target_id)
        chat.save()
        current_gamer = Gamer.objects.get(pk=current_user)
        target_gamer = Gamer.objects.get(pk=target_user)
        current_gamer.chats.add(chat)
        target_gamer.chats.add(chat)
        current_gamer.save()
        target_gamer.save()
    
    return chat

def parse_users(users):
    length = len(users)
    index = 0
    target_user = ""

    for i in range(length):
        if users[i] == ",":
            index = i
        
        if index != 0 and i > index:
            target_user += users[i]

    if index == 0:
        return False

    return target_user

def file_format(string):
    length = len(string)
    index = 0
    for i in range(length):
        if string[i] == ".":
            index = i

    fileformat = ""
    while (index < length):
        fileformat += string[index]
        index += 1
    
    return fileformat
    
    
