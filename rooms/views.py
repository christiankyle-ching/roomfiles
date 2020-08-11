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
from django.contrib.auth import get_user_model

# Generic/Specific forms import
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView
from django.views.generic.base import RedirectView
from .forms import RoomJoinForm, ContactForm

# Form-related imports
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import (
    user_postable_set_details,

    user_is_room_owner,
    user_allowed_in_room,
    user_allowed_enter_room,
    user_allowed_view_object,
    user_allowed_edit_object,

    read_object,
    )

# Model imports
from .models import Room, File, Announcement, RoomBackground
from users.models import Profile
from rooms.contenttypes import get_ann_contenttype, get_file_contenttype

# Rest Framework
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions



def home(request):
    if request.user.is_authenticated:
        if request.user.profile.user_rooms:
            return redirect('user-rooms')
        else:
            return redirect('user-rooms')
    
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



# Room Views
class RoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    fields = ('name', 'description',)
    
    def form_valid(self, form):
        # inject creator of room as request.user
        form.instance.created_by = self.request.user

        # display success message
        messages.add_message(self.request, messages.INFO, f'Successfully created "{form.instance.name}".')
        return super().form_valid(form)

class RoomUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Room
    pk_url_kwarg = 'room_pk'
    fields = ('name', 'description',)

    def test_func(self):
        return user_is_room_owner(self.request.user, self.get_object())
    
    def form_valid(self, form):
        # display success message
        messages.add_message(self.request, messages.INFO, f'Successfully updated "{form.instance.name}".')
        return super().form_valid(form)

class RoomDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Room
    pk_url_kwarg = 'room_pk'

    def get_context_data(self, **kwargs):
        # call super().get_context_data to get context
        context = super().get_context_data(**kwargs)
        room = self.get_object()
        user = self.request.user
        
        # Get query for files
        search_keyword = self.request.GET.get('search', '')

        files_qs = room.get_files(search=search_keyword) if search_keyword != '' else room.get_files()
        context['search'] = search_keyword
        
        # Paginate
        files_paginator = Paginator(files_qs, settings.FILE_PER_PAGE)
        files_page_number = self.request.GET.get('file_page', '1')
        files_page_obj = files_paginator.get_page(files_page_number)
        context['files'] = files_page_obj        

        # Get query for announcements
        announcements_qs = room.get_announcements()
        announcements_qs_latest = announcements_qs[:settings.ANNOUNCEMENTS_PER_PAGE] # limit query to latest 10
        if files_page_number == '1':
            context['announcements'] = announcements_qs_latest
            context['total_announcements_count'] = announcements_qs.count()

        # Get User-liked announcements
        liked_anns_qs = announcements_qs.filter(liked_by__in=[user])
        context['liked_announcements'] = liked_anns_qs

        # Get People
        context['people'] = room.get_people()
        context['banned_people'] = room.get_banned_people()

        # Get unread files and announcements
        unread_files = user.profile.get_unread_files(room).values('object_id')
        unread_anns = user.profile.get_unread_anns(room).values('object_id')
        # Then map to get id only
        unread_files = [item['object_id'] for item in unread_files]
        unread_anns = [item['object_id'] for item in unread_anns]

        context['unread_files'] = unread_files
        context['unread_anns'] = unread_anns

        # Room Backgrounds
        context['room_backgrounds'] = RoomBackground.objects.all()
        
        return context

    def post(self, request, *args, **kwargs):
        room = self.get_object()

        # Check if request.user is room owner
        if  user_is_room_owner(request.user, room):

            # If banning user
            if 'ban_user' in request.POST:
                user_id = request.POST.get('ban_user', 0)
                try:
                    user_to_ban = get_object_or_404(get_user_model(), pk=int(user_id))

                    if request.user != user_to_ban:
                        response = room.toggle_ban(user_to_ban)
                        messages.info(request, response['message'])
                    else:
                        messages.error(request, 'You cannot ban yourself.')

                except ValueError as e:
                    messages.error(request, 'Oops! Something went wrong.')
            
            if 'room_bg' in request.POST:
                try:
                    roombg_id = int(request.POST.get('room_bg_id', ''))
                    room.change_background(roombg_id)
                    messages.success(request, f"Changed {room.name}'s background'")
                except ValueError as e:
                    messages.error(request, 'Something went wrong.')
            
            

        else:
            messages.error(request, 'You cannot do that.')

        return redirect(room.get_absolute_url())

    def test_func(self):
        return user_allowed_in_room(self.request.user, self.get_object())

from .filters import get_item

class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    context_object_name = 'user_rooms'

    def get_queryset(self):
        return self.request.user.profile.user_rooms.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Insert Available backgrounds
        context['room_backgrounds'] = RoomBackground.objects.all()

        user_rooms = context['user_rooms']
        user = self.request.user

        # Get notification counts for each room
        notif_counts = {}
        for room in user_rooms:
            notif_counts[room.pk] = user.profile.get_notification_count_in_room(room)
        context['notif_counts'] = notif_counts

        return context

    def post(self, request, *args, **kwargs):
        room = get_object_or_404(Room, pk=request.POST.get('room_id', ''))
        
        if user_is_room_owner(request.user, room):

            if 'room_bg' in request.POST:
                try:
                    roombg_id = int(request.POST.get('room_bg_id', ''))
                    room.change_background(roombg_id)
                    messages.success(request, f"Changed {room.name}'s background'")
                except ValueError as e:
                    messages.error(request, 'Something went wrong.')
            
        else:
            messages.error(request, 'You cannot do that.')

        return redirect('user-rooms')



@login_required
def leave_room(request, room_pk, room_slug):
    room = get_object_or_404(Room, pk=room_pk)

    if request.method == 'POST':
        if 'leave' in request.POST:
            messages.info(request, f'You left the room "{room.name}".')
            request.user.profile.leave_room(room)
            
            return redirect('home')

    return render(request, 'rooms/room_leave.html', { 'room': room })

@login_required
def join_room(request):
    form = RoomJoinForm()

    if request.POST:
        form = RoomJoinForm(request.POST)

        if form.is_valid():
            # check if room exists
            _code = form.cleaned_data.get('code')
            _room = get_object_or_404(Room, pk=_code)

            
            if not user_allowed_enter_room(request.user, _room):
                messages.error(request, 'You cannot join this room.')
            else:
                # if user is allowed to enter room
                request.user.profile.join_room(_room)

                # display message
                messages.add_message(request, messages.INFO, f'Successfully added room "{_room.name}"')
                return redirect(_room)

    return render(request, 'rooms/room_join.html', { 'form' : form })




# File Views
class FileDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = File
    pk_url_kwarg = 'file_pk'

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
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        return user_allowed_in_room(self.request.user, room)
    
    def form_valid(self, form):
        user = self.request.user
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        form = user_postable_set_details(form, user, room)
        
        # display success message
        messages.add_message(self.request, messages.INFO, f'Successfully uploaded "{form.instance.name}".')
        return super().form_valid(form)

class FileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = File
    pk_url_kwarg = 'file_pk'
    fields = ('name', 'description', 'raw_file')

    def test_func(self):
        return user_allowed_edit_object(self.request.user, self.get_object())
    
    def form_valid(self, form):
        # display success message
        messages.add_message(self.request, messages.INFO, f'Successfully updated "{form.instance.name}".')
        return super().form_valid(form)

class FileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = File
    pk_url_kwarg = 'file_pk'

    def test_func(self):
        return user_allowed_edit_object(self.request.user, self.get_object())

    def delete(self, *args, **kwargs):
        _obj = self.get_object()
        messages.add_message(self.request, messages.INFO, f'Successfully deleted "{_obj.name}".')
        return super().delete(self, *args, **kwargs)

    def get_success_url(self):
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        return room.get_absolute_url()



# Announcement Views
class AnnouncementCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Announcement
    fields = ('content',)

    def test_func(self):
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        return user_allowed_in_room(self.request.user, room)

    def form_valid(self, form):
        user = self.request.user
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        form = user_postable_set_details(form, user, room)
        
        # display success message
        messages.add_message(self.request, messages.INFO, 'Posted new announcement.')
        return super().form_valid(form)

class AnnouncementUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Announcement
    pk_url_kwarg = 'ann_pk'
    fields = ('content',)

    def test_func(self):
        return user_allowed_edit_object(self.request.user, self.get_object())
    
    def form_valid(self, form):
        # display success message
        messages.add_message(self.request, messages.INFO, 'Successfully edited announcement.')
        return super().form_valid(form)

class AnnouncementDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Announcement
    pk_url_kwarg = 'ann_pk'
    
    def test_func(self):
        return user_allowed_edit_object(self.request.user, self.get_object())

    def delete(self, *args, **kwargs):
        messages.add_message(self.request, messages.INFO, 'Successfully deleted announcement.')
        return super().delete(self, *args, **kwargs)

    def get_success_url(self):
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        return room.get_absolute_url()

class AnnouncementListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'rooms/announcement_list.html'

    def test_func(self):
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        return user_allowed_in_room(self.request.user, room)

    def get_queryset(self):
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])

        search_keyword = self.request.GET.get('search', '')
        sort_with = self.request.GET.get('sort', 'date-desc')

        if search_keyword != '':
            return room.get_announcements(search=search_keyword, sort=sort_with)
        else:
            return room.get_announcements(sort=sort_with)


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        search_keyword = self.request.GET.get('search', '')
        sort_with = self.request.GET.get('sort', 'date-desc')
        context['search'] = search_keyword
        context['sort_with'] = sort_with

        ann_qs = self.get_queryset()
        
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
def api_toggle_like(request, room_pk, room_slug, ann_pk):
    ann = get_object_or_404(Announcement, pk=ann_pk)
    user = request.user

    if request.method == 'PUT':
        if user_allowed_in_room(request.user, ann.room):
            data = ann.toggle_like(user)
            return Response(data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)

