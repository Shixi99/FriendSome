from django.shortcuts import render, redirect
from .models import Room, Topic, Message, User
from .forms import RoomForm, MessageForm, CreateRoomForm, UserForm, MyUserCreationForm
from django.db.models import Q
# from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# from django.contrib.auth.forms import UserCreationForm


# rooms = [
#     {'id': 1, 'name': 'Lets learn python'},
#     {'id': 2, 'name': 'Design with me'},
#     {'id': 3, 'name': 'Front end developers'},
# ]
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
    context = {'page': page}
    return render(request, 'base/login_register.html', context=context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error has occurred during registration')
    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:8]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(
        room__topic__name__icontains=q
    ))
    context = {'rooms': rooms,
               'topics': topics,
               'room_count': room_count,
               'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    # my_room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         my_room = i
    my_room = Room.objects.get(id=pk)
    room_messages = my_room.message_set.all()
    participants = my_room.participants.all()
    participants_list = [val for val in participants]

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=my_room,
            body=request.POST.get('body')
        )
        my_room.participants.add(request.user)
        return redirect('room', pk=my_room.id)

    context = {'room': my_room, 'room_messages': room_messages,
               'participants': participants, 'participants_list': participants_list}
    return render(request, ['base/room.html', 'base/activity_component.html', 'base/feed_component.html'], context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    # topics = user.room_set.all()
    topics = Topic.objects.all()
    my_context = {'user': user, 'rooms': rooms,
                  'room_messages': room_messages,
                  'topics': topics}
    # bio = User.objects.

    return render(request, 'base/profile.html', my_context)


@login_required(login_url='login')
def createRoom(request):
    form = CreateRoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        # form = CreateRoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    my_room = Room.objects.get(id=pk)
    form = RoomForm(instance=my_room)
    topics = Topic.objects.all()
    if request.user != my_room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        my_room.name = request.POST.get('name')
        my_room.topic = topic
        my_room.description = request.POST.get('description')
        my_room.save()
        return redirect('room', pk=my_room.id)
    context = {'form': form, 'topics': topics, 'room': my_room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateMessage(request, pk):
    my_message = Message.objects.get(id=pk)
    form = MessageForm(instance=my_message)

    if request.user != my_message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=my_message)
        if form.is_valid():
            form.save()
            return redirect('room', pk=my_message.room.id)
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    my_room = Room.objects.get(id=pk)
    if request.user != my_room.host:
        return HttpResponse('You are not allowed here!')
    if request.method == "POST":
        my_room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': my_room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    my_message = Message.objects.get(id=pk)
    if request.user != my_message.user:
        return HttpResponse('<script>alert(You are not allowed here!)</script>')
    if request.method == "POST":
        my_message.delete()
        # return redirect('room', my_message.room.id)
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': my_message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {'form': form}
    return render(request, 'base/update-user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    topics = Topic.objects.filter(
        name__icontains=q
    )
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
