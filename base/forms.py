from django.forms import ModelForm
from .models import Room, Message, User
from django.contrib.auth.forms import UserCreationForm


# from django.contrib.auth.models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants', 'topic']


class CreateRoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
        exclude = ['host', 'participants', 'user', 'room']


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']
