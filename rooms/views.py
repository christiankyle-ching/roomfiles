# Django Core imports
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import random, string
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError, EmailMessage

# Generic/Specific forms import
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView
from django.views.generic.base import RedirectView
from .forms import RoomJoinForm, ContactForm

# Form-related imports
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import (
    user_postable_set_details,

    user_allowed_in_room,
    user_allowed_create_obj,
    user_allowed_view_object,
    user_allowed_edit_object,

    read_object,
    )

# Model imports
from .models import Room, File, Announcement
from users.models import Profile
from users.contenttypes import get_ann_contenttype, get_file_contenttype

# Rest Framework
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions



def home(request):
    if request.user.is_authenticated:
        if request.user.profile.room:
            return redirect(request.user.profile.room)
        else:
            return redirect('room-landing')
    
    return render(request, 'rooms/home.html')

@login_required
def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            subject = form.cleaned_data['subject']
            category = form.get_category_display(form.cleaned_data['category'])
            message = form.cleaned_data['message']

            try:
                subject = f'RoomFiles Support | {category}: {subject}'
                message = f'{category}\nFrom: {request.user.email}\n\n{message}'
                email = EmailMessage(
                    subject,
                    message,
                    from_email=request.user.email,
                    to=[settings.EMAIL_HOST_USER],
                    reply_to=[request.user.email]).send()
                
                return redirect('contact_success')
            except BadHeaderError:
                messages.error(request, 'Something went wrong.')

    return render(request, 'rooms/contact.html', { 'form':form })

def contact_success(request):
    return render(request, 'rooms/contact_success.html')

def about(request):
    return render(request, 'rooms/about.html')

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
        messages.add_message(self.request, messages.INFO, f'Successfully created "{form.instance.name}".')
        return super().form_valid(form)

    def test_func(self):
        return not self.request.user.profile.room

class RoomUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Room
    fields = ('name', 'description',)

    def test_func(self):
        return self.request.user.profile.room == self.get_object()
    
    def form_valid(self, form):
        # display success message
        messages.add_message(self.request, messages.INFO, f'Successfully updated "{form.instance.name}".')
        return super().form_valid(form)

class RoomDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Room

    def get_context_data(self, **kwargs):
        # call super().get_context_data to get context
        context = super().get_context_data(**kwargs)
        
        # Get query for files
        search_keyword = self.request.GET.get('search', '')
        files_qs = File.objects.filter(room=self.get_object())
        if search_keyword != '':
            files_qs = files_qs.filter(
                Q(posted_by__username__icontains=search_keyword) |
                Q(name__icontains=search_keyword) |
                Q(description__icontains=search_keyword)
            )
        
        files_qs = files_qs.order_by('-posted_datetime').defer('raw_file')
        context['total_files_count'] = files_qs.count()
        context['search'] = search_keyword
        
        # Paginate
        files_paginator = Paginator(files_qs, settings.FILE_PER_PAGE)
        files_page_number = self.request.GET.get('file_page', 1)
        files_page_obj = files_paginator.get_page(files_page_number)
        context['files'] = files_page_obj

        # Get query for announcements
        announcements_qs = Announcement.objects.filter(room=self.get_object()).order_by('-posted_datetime')
        announcements_qs_latest = announcements_qs[:settings.ANNOUNCEMENTS_PER_PAGE] # limit query to latest 10
        context['announcements'] = announcements_qs_latest
        context['total_announcements_count'] = announcements_qs.count()

        # Get User-liked announcements
        liked_anns_qs = announcements_qs.filter(liked_by__in=[self.request.user])
        context['liked_announcements'] = liked_anns_qs

        return context

    def test_func(self):
        return self.request.user.profile.room == self.get_object()



@login_required
def room_people_listview(request, pk, slug):
    room = get_object_or_404(Room, pk=pk)

    if request.user.profile.room != room:
        raise PermissionDenied('You cannot access this room.')

    if request.method == 'POST':
        if request.user == room.created_by:
            user_id = request.POST.get('user_id')
            if user_id == '':
                messages.error(request, 'Something went wrong. Please try again later.')
            else:
                response = room.toggle_ban(user_id)
                messages.success(request, response['message'])
        else:
            raise PermissionDenied('You do not have enough permissions to ban users.')
    
    people = Profile.objects.filter(room=room).order_by('user__username')
    return render(request, 'people.html', { 'people': people, 'room' : room, 'ban_status': False })

@login_required
def room_banned_people_listview(request, pk, slug):
    room = get_object_or_404(Room, pk=pk)

    if request.user != room.created_by:
        raise PermissionDenied('You cannot access ban list.')

    if request.method == 'POST':
        if request.user == room.created_by:
            user_id = request.POST.get('user_id')
            if user_id == '':
                messages.error(request, 'Something went wrong. Please try again later.')
            else:
                response = room.toggle_ban(user_id)
                messages.info(request, response['message'])
        else:
            raise PermissionDenied('You do not have enough permissions to ban users.')
    
    banned_people_qs = room.banned_users.all()
    banned_people = [user.profile for user in banned_people_qs]

    return render(request, 'people.html', { 'people': banned_people, 'room' : room, 'ban_status': True})



@login_required
def leave_room(request):
    if not request.user.profile.room:
        return redirect('room-landing')

    if request.method == 'POST':
        if 'leave' in request.POST:
            messages.info(request, f'You left the room "{request.user.profile.room.name}".')
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
            _room = get_object_or_404(Room, pk=_code)

            if request.user in _room.banned_users.all():
                messages.error(request, 'You cannot join this room.')
            else:
                # if exists, save
                request.user.profile.room = _room
                request.user.profile.save()

                # display message
                messages.add_message(request, messages.INFO, f'Successfully joined room "{_room.name}"')
                return redirect(_room)

    return render(request, 'rooms/room_join.html', { 'form' : form })




# File Views
class FileDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = File

    def test_func(self):
        return user_allowed_view_object(self.request.user, self.get_object())

    def get_object(self):
        file = super().get_object()

        # Read notification if opened
        user = self.request.user
        if not user == file.posted_by:
            read_object(user, get_file_contenttype(), file.id)
            
        return file

class FileCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = File
    fields = ('name', 'description', 'raw_file')
    
    def test_func(self):
        return self.request.user.profile.room
    
    def form_valid(self, form):
        form = user_postable_set_details(self, form)
        
        # display success message
        messages.add_message(self.request, messages.INFO, f'Successfully uploaded "{form.instance.name}".')
        return super().form_valid(form)

class FileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = File
    fields = ('name', 'description', 'raw_file')

    def test_func(self):
        return user_allowed_edit_object(self.request.user, self.get_object())
    
    def form_valid(self, form):
        form = user_postable_set_details(self, form)

        # display success message
        messages.add_message(self.request, messages.INFO, f'Successfully updated "{form.instance.name}".')
        return super().form_valid(form)

class FileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = File
    
    def test_func(self):
        return user_allowed_edit_object(self.request.user, self.get_object())

    def delete(self, *args, **kwargs):
        _obj = self.get_object()
        messages.add_message(self.request, messages.INFO, f'Successfully deleted "{_obj.name}".')
        return super().delete(self, *args, **kwargs)

    def get_success_url(self):
        return self.request.user.profile.room.get_absolute_url()



# Announcement Views
class AnnouncementCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Announcement
    fields = ('content',)

    def test_func(self):
        return self.request.user.profile.room

    def form_valid(self, form):
        form = user_postable_set_details(self, form)
        
        # display success message
        messages.add_message(self.request, messages.INFO, 'Posted new announcement.')
        return super().form_valid(form)

class AnnouncementUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Announcement
    fields = ('content',)

    def test_func(self):
        return user_allowed_edit_object(self.request.user, self.get_object())
    
    def form_valid(self, form):
        form = user_postable_set_details(self, form)

        # display success message
        messages.add_message(self.request, messages.INFO, 'Successfully edited announcement.')
        return super().form_valid(form)

class AnnouncementDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Announcement
    
    def test_func(self):
        return user_allowed_edit_object(self.request.user, self.get_object())

    def delete(self, *args, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Successfully deleted announcement.')
        return super().delete(self, *args, **kwargs)

    def get_success_url(self):
        return self.request.user.profile.room.get_absolute_url()

class AnnouncementListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'rooms/announcement_list.html'

    def test_func(self):
        _room = get_object_or_404(Room, pk=self.kwargs['pk'])
        return self.request.user.profile.room == _room

    def get_queryset(self):
        return Announcement.objects.filter(room=self.request.user.profile.room).order_by('-posted_datetime')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # Filter with search
        search_keyword = self.request.GET.get('search', '')
        ann_qs = self.get_queryset()
        if search_keyword != '':
            ann_qs = ann_qs.filter(
                Q(posted_by__username__icontains=search_keyword) |
                Q(content__icontains=search_keyword)
            )

        # Sorting
        sort_with = self.request.GET.get('sort', 'date-desc')
        ann_qs = ann_qs.order_by('-posted_datetime') if sort_with == 'date-desc' else ann_qs.order_by('posted_datetime')

        context['search'] = search_keyword
        context['sort_with'] = sort_with
        
        # Paginate
        ann_paginator = Paginator(ann_qs, settings.ANNOUNCEMENTS_PER_PAGE)
        page_number = self.request.GET.get('page', 1)
        ann_page_obj = ann_paginator.get_page(page_number)
        context['announcements'] = ann_page_obj

        # Get User-liked announcements
        liked_anns_qs = ann_qs.filter(liked_by__in=[self.request.user])
        context['liked_announcements'] = liked_anns_qs

        return context


# AJAX Calls
@api_view(['PUT'])
def api_toggle_like(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    user = request.user

    if request.method == 'PUT':
        if user.profile.room != ann.room:
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = ann.toggle_like(user)
        
        return Response(data, status=status.HTTP_200_OK)

