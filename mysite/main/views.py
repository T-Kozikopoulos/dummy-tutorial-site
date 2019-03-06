from django.shortcuts import render, redirect, HttpResponse
from .models import Tutorial, TutorialCategory, TutorialSeries
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm


def single_slug(request, single_slug):
    categories = [c.slug for c in TutorialCategory.objects.all()]
    if single_slug in categories:
        matching_series = TutorialSeries.objects.filter(category__slug=single_slug)
        series_urls = {}

        for m in matching_series.all():
            part_one = Tutorial.objects.filter(series__series=m.series).earliest('published')
            series_urls[m] = part_one.slug

        context = {
            'part_ones': series_urls
        }
        return render(request, 'main/category.html', context)

    tutorials = [t.slug for t in Tutorial.objects.all()]
    if single_slug in tutorials:
        this_tutorial = Tutorial.objects.get(slug=single_slug)
        tutorials_from_series = Tutorial.objects.filter(series__series=this_tutorial.series).order_by('published')

        this_tutorial_idx = list(tutorials_from_series).index(this_tutorial)

        context = {
            'tutorial': this_tutorial,
            'sidebar': tutorials_from_series,
            'this_tutorial_idx': this_tutorial_idx
        }
        return render(request, 'main/tutorial.html', context)

        return HttpResponse(f'{single_slug} is a tutorial!')

    return HttpResponse(f'{single_slug} does not correspond to anything')


def homepage(request):
    context = {
        "categories": TutorialCategory.objects.all
    }
    return render(request, 'main/categories.html', context)


def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created")
            login(request, user)
            messages.info(request, f"You are now logged in as {username}")
            # in urls.py, app_name=main & urlpatters has name='homepage'
            return redirect('main:homepage')
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

    form = NewUserForm()
    context = {
        'form': form
    }
    return render(request, 'main/register.html', context)


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('main:homepage')


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('main:homepage')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')

    form = AuthenticationForm()
    context = {
        'form': form
    }
    return render(request, 'main/login.html', context)
