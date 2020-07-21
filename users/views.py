from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType

from .forms import UserRegisterForm, ProfileUpdateForm
from django.views.generic import ListView

from .models import Avatar, Notification
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
            messages.success(request, f'Account created!')

            return redirect('login')

    return render(request, 'users/register.html', { 'form' : form })

@login_required
def profile(request):
    p_form = ProfileUpdateForm(instance=request.user.profile)

    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        avatar_id = request.POST.get('avatar')
        
        if p_form.is_valid() and int(avatar_id) > 0:
            request.user.profile.avatar = get_object_or_404(Avatar, pk=avatar_id)
            p_form.save()

            messages.success(request, 'Successfully updated your profile.')

            return redirect('profile')

    context = { 'p_form': p_form }
    return render(request, 'users/profile.html', context)

@login_required
def settings(request):
    return render(request, 'users/settings.html')

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

@login_required
def close_account(request):
    if request.POST:
        if 'close-account' in request.POST:
            return close_account_done(request)

    return render(request, 'users/close_account.html')

def close_account_done(request):
    request.user.is_active = False
    request.user.save()
    return redirect('close_account_done.html')
    


# API Calls
@login_required
def api_seen_object(request, model):
    user = request.user
    content_type = ContentType.objects.get_by_natural_key('rooms', model)

    user_notifs = Notification.objects.filter(target=user, is_read=False)
    content_notifs =  user_notifs.filter(action_obj_contenttype=content_type)

    for notif in content_notifs:
        notif.read()
    
    return JsonResponse({ 'done' : True , 'unseen_object' : 0, 'unseen_total' : user_notifs.count() })

