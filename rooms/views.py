from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages

from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from .forms import RoomJoinForm

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from .utils import is_file_owner, set_file_details, is_room_owner, set_room_details

from .models import Room, File
from users.models import Profile

import random, string


def home(request):
    if request.user.is_authenticated:
        if request.user.profile.room:
            return redirect(request.user.profile.room)
        else:
            return redirect('room-landing')
    
    return render(request, 'rooms/home.html')

def room_landing(request):
    return render(request, 'rooms/room-landing.html')


# Room Views
class RoomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Room
    fields = ('name', 'description',)
    
    def form_valid(self, form):
        # inject creator of room as request.user
        form.instance.created_by = self.request.user

        # display success message
        messages.add_message(self.request, messages.INFO, 'Successfully created "{}".'.format(form.instance.name))
        return super().form_valid(form)

    def test_func(self):
        return not self.request.user.profile.room

class RoomUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Room
    fields = ('name', 'description',)

    def test_func(self):
        return is_room_owner(self)
    
    def form_valid(self, form):
        form = set_room_details(self, form)

        # display success message
        messages.add_message(self.request, messages.INFO, 'Successfully updated "{}".'.format(form.instance.name))
        return super().form_valid(form)

class RoomDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Room

    def get_context_data(self, **kwargs):
        # call super().get_context_data to get context
        context = super().get_context_data(**kwargs)
        
        # inject Files in context, filter based on object of DetailView
        context['files'] = File.objects.filter(room=self.get_object()).order_by('-upload_datetime')

        # inject Profiles (People) on the room
        context['people'] = Profile.objects.filter(room=self.get_object()).order_by('last_name')

        return context

    def test_func(self):
        return self.request.user.profile.room == self.get_object()

@login_required
def leave_room(request):
    if not request.user.profile.room:
        return redirect('room-landing')

    if request.method == 'POST':
        if 'leave' in request.POST:
            request.user.profile.room = None
            request.user.profile.save()
            return redirect('room-landing')

    return render(request, 'rooms/room_leave.html')

@login_required
def join_room(request):
    if request.user.profile.room:
        messages.add_message(request, messages.ERROR, 'You already joined a room.')
        return redirect(request.user.profile.room)

    form = RoomJoinForm()

    if request.POST:
        form = RoomJoinForm(request.POST)

        if form.is_valid():
            # check if room exists
            _code = form.cleaned_data.get('code')
            _room = Room.objects.get(pk=_code)

            if _room == None:
                # if not, raise error
                raise ValidationError('Room does not exist.')
            
            # if exists, save
            request.user.profile.room = _room
            request.user.profile.save()

            # display message
            messages.add_message(request, messages.INFO, f'Successfully joined room "{_room.name}"')

            return redirect(_room)

    return render(request, 'rooms/room_join.html', { 'form' : form })


# File Views
class FileDetailView(LoginRequiredMixin, DetailView):
    model = File

class FileCreateView(LoginRequiredMixin, CreateView):
    model = File
    fields = ('name', 'description', 'raw_file')
    
    def form_valid(self, form):
        form = set_file_details(self, form)
        
        # display success message
        messages.add_message(self.request, messages.INFO, 'Successfully uploaded "{}".'.format(form.instance.name))
        return super().form_valid(form)

class FileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = File
    fields = ('name', 'description', 'raw_file')

    def test_func(self):
        return is_file_owner(self)
    
    def form_valid(self, form):
        form = set_file_details(self, form)

        # display success message
        messages.add_message(self.request, messages.INFO, 'Successfully updated "{}".'.format(form.instance.name))
        return super().form_valid(form)

class FileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = File
    
    def test_func(self):
        return is_file_owner(self)

    def delete(self, *args, **kwargs):
        _obj = self.get_object()
        messages.add_message(self.request, messages.INFO, 'Successfully deleted "{}".'.format(_obj.name))
        return super().delete(self, *args, **kwargs)

    def get_success_url(self):
        return self.request.user.profile.room.get_absolute_url()
