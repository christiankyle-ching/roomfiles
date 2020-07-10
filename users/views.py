from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.core.paginator import Paginator

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Avatar
from rooms.models import Notification
from django.http import JsonResponse


# Views
def register(request):
    form = UserRegisterForm()

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()

            # Get username and display in messages
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect('login')

    return render(request, 'users/register.html', { 'form' : form })

@login_required
def profile(request):
    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        avatar_id = request.POST.get('avatar')
        
        if u_form.is_valid() and p_form.is_valid() and int(avatar_id) > 0:
            u_form.save()
            
            request.user.profile.avatar = get_object_or_404(Avatar, pk=avatar_id)
            p_form.save()

            messages.success(request, 'Successfully updated your profile.')

            return redirect('profile')

    context = { 'u_form': u_form, 'p_form': p_form }
    return render(request, 'users/profile.html', context)

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'users/notification_list.html'
    context_object_name = 'notifications'
    
    def get_queryset(self):
        qs = Notification.objects.filter(target=self.request.user).order_by('-executed_datetime')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = self.get_queryset()

        # Paginate
        paginator = Paginator(qs, 10)
        page_number = self.request.GET.get('page', 1) # Gets page parameter on Ajax / Fetch calls
        page_obj = paginator.get_page(page_number)
        context['notifications'] = page_obj

        return context




# API Calls
def avatar_preview(request, pk):
    avatar = get_object_or_404(Avatar, pk=pk)
    user = request.user

    response = {
        'image_url' : avatar.image.url
    }

    return JsonResponse(response)
    



