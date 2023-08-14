from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.http import HttpResponse

from django.db.models import Q
from django.contrib.auth import authenticate, login, logout


# rooms= [
#     {'id':1, 'name':'Lets learn python'},
#     {'id':2, 'name':'Web Development'},
#     {'id':3, 'name':'FrontEnd Developers'},
# ]

def loginPage(request):
    page='login'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username= request.POST.get('username').lower()
        password= request.POST.get('password')

        try:
            user= User.objects.get(username= username)
        except:
            messages.error(request, "User not found!!")
            
        user= authenticate(request, username= username, password= password)

        if user is not None:
            login(request, user)
            return redirect ('home')
        else:
            messages.error(request, "Username and password does not match")

    return render(request, 'base/login_register.html',{
        'page':page,
    })

def logoutUser(request):
    logout(request)
    
    return redirect ('home')

def registerPage(request):
    form= UserCreationForm()

    if request.method == "POST":
        form= UserCreationForm(request.POST)
        if form.is_valid():
            user= form.save(commit=False)   #saving the form but freezing in time, just for the moment so that when the form is valid,we can access the user, just created, right away
            user.username= user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration!! please double check!!!')

    return render(request, 'base/login_register.html', {
        'form':form,
    })

def home(request):

    q=request.GET.get('q') if request.GET.get('q')!= None else ''

    rooms= Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) | 
        Q(description__icontains=q) 
        )
    
    topics= Topic.objects.all()[:4]     #to get only 4 topics

    room_count= rooms.count()   #no. of rooms after filtering
    room_messages= Message.objects.filter(room__topic__name__icontains= q) # filter from the models begining from Message(models) that goes into room, then, into topic into name 
    # print(room_messages)
    return render(request, 'base/home.html', {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
    })

def room (request, pk):
    # room= None
    # for i in rooms:
    #     if i['id']==pk:
    #         room=i
    
    room_obj= Room.objects.get(id=pk)
    print(room_obj)
    # room_messages= Message.objects.filter(room= room)
    room_messages= room_obj.message_set.all()    #same job as above line, gets all the message related to this room_obj
    # print(room_messages) 
    participants= room_obj.participants.all()
    # print(participants)

    if request.method== "POST":
        message= Message.objects.create(
            user= request.user,
            body= request.POST.get('body'),  #this 'body' represents name= 'body' in input of form(templates)
            room= room_obj
        )
        room_obj.participants.add(request.user) #to add the user who are not in the participants list before commenting
        return redirect('room',pk= room_obj.id)

    return render(request, 'base/room.html',{
        'room_obj': room_obj,
        'room_messages': room_messages,
        'participants': participants,
    })

def userProfile(request, pk):
    user= User.objects.get(id=pk)
    print(user)
    
    rooms= user.room_set.all()              #returns all Room objects related to User 
    print(list(rooms))
    room_messages= user.message_set.all()   #returns all Message objects related to User 
    print(list(room_messages))
    
    topics= Topic.objects.all()

    return render(request,'base/profile.html', {
        'user': user,
        'rooms':rooms,
        'room_messages': room_messages,
        'topics': topics,
    })

@login_required(login_url='login')
def createRoom(request):
    form= RoomForm    #this is empty form intialization, but we'll see example to update form later in updateRoom function
    topics= Topic.objects.all()

    if request.method =='POST':
        topic_name= request.POST.get('topic')
        topic, created= Topic.objects.get_or_create(name=topic_name)

        Room.objects.create (
            host= request.user,
            topic= topic,
            name= request.POST.get('name'),
            description= request.POST.get('description')
        )
        # print(request.POST)
        # form= RoomForm(request.POST)
        # if form.is_valid():
        #     room= form.save(commit= False)
        #     room.host= request.user
        #     room.save()
        return redirect ('home')   #this home name taken from urls.py
    
    context= {
        'form':form,
        'topics':topics,
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room= Room.objects.get(id=pk)
    form= RoomForm(instance= room) #In this way we can update the empty form, using the instance 'room', substituting the value of room in form.
    topics= Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('you are not allowed here because not your room')
    
    if request.method == 'POST':    #this will get the data after submit is clicked
        topic_name= request.POST.get('topic')
        topic, created= Topic.objects.get_or_create(name= topic_name)
        room.name= request.POST.get('name')
        room.topic= topic
        room.description= request.POST.get('description')
        room.save()

        # form= RoomForm(request.POST, instance= room)    #update new data into the intialized 'form', here, if (instance=room) is not given, then, it will simply update data into new form 
        # if form.is_valid():
        #     form.save()

        return redirect('home')
    
    context= {
        'form': form,
        'topics': topics,
        'room': room,
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom (request, pk):
    room= Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('you are not allowed here because not your room')

    if request.method == 'POST':
        room.delete()
        return redirect ('home')
    
    return render(request, 'base/delete.html', {
        'obj': room
    })

@login_required(login_url= 'login')
def deleteMessage(request, pk):
    message= Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render (request, 'base/delete.html', {
        'obj': message,
    })

@login_required(login_url= 'login')
def updateUser(request):
    user= request.user
    # print('request.user=', user)

    #the (instance= user) substitute the value of user( =request.user) in the form
    form= UserForm(instance= user)  
    # print("form_before: ", form)

    if request.method == "POST":
        form= UserForm(request.POST, instance= user)
        # print(".POST=", request.POST)
        # print("form_after = ", form)
        if form.is_valid():
            form.save()
            return redirect ('user-profile', pk= user.id)

    return render(request, 'base/update-user.html', {
        'form': form,
    })


def topicsPage (request):
    q=request.GET.get('q') if request.GET.get('q')!= None else ''
    topics= Topic.objects.filter(name__icontains= q)
    return render (request, 'base/topics.html',{
        'topics': topics,
    })

def activityPage(request):
    room_messages= Message.objects.all()

    return render (request, 'base/activity.html',{
        'room_messages': room_messages
    })