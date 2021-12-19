from django.shortcuts import render
from .models import Event
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.http.response import JsonResponse
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.

def index(request):
    """
    Returns the list event to show users
    """
    filter_dict = {}
    filter_dict["published"] = True
    filter_dict["end_date__date__gte"] = datetime.today().date()
    filter_cat = Event.objects.values("categories").distinct()
    if request.method == "POST":
        start_date = request.POST.get("start_date", None)
        end_date = request.POST.get("end_date", None)
        category = request.POST.get("category")
        key = request.POST.get("keyword")
        
        if start_date and end_date:
            filter_dict["end_date__date__range"] = [start_date, end_date]
        if category:
            filter_dict["categories"] = category
        if key:
            keyword_search = Q()
            keyword_search |= Q(title__icontains=key)
            keyword_search |= Q(description__icontains=key)
            events = Event.objects.filter(Q(**filter_dict) & Q(keyword_search)).order_by('start_date')
        else:
            events = Event.objects.filter(**filter_dict).order_by(
                'start_date')
    else:
        events = Event.objects.filter(**filter_dict).order_by('start_date')
    if request.user.is_authenticated:

        for event in events:
            liked_ids = [like.id    for like in event.likes.all() if len(event.likes.all()) > 0]
            if request.user.id in liked_ids:
                event.liked = True

        for event in events:
            disliked_ids = [dislike.id for dislike in event.dislikes.all()  if len(event.dislikes.all()) > 0]
            if request.user.id in disliked_ids:
                event.disliked = True

    page = request.GET.get('page', 1)
    paginator = Paginator(events, 10)
    try:
        eventlist = paginator.page(page)
    except PageNotAnInteger:
        eventlist = paginator.page(1)
    except EmptyPage:
        eventlist = paginator.page(paginator.num_pages)

    return render(request, 'events.html', {'events': eventlist, 'category': filter_cat})


def like_event(request):
    """
    For user to like an event
    """
    if request.user.is_authenticated:
        body = json.loads(request.POST.get('datastring'))
        event_id = body['id']
        event = Event.objects.get(id=event_id)
        if request.user.id in event.likes.all():
            event.likes.remove(request.user.id)
        else:
            event.likes.add(request.user.id)
            event.dislikes.remove(request.user.id)



        event.save()

        return JsonResponse({"status": "succes", "message": "event liked"})
    else:
        return JsonResponse({"status": "failed", "message": "user not loggeed in"})


def dislike_event(request):
    """
    For user to dislike an event
    """
    if request.user.is_authenticated:
        body = json.loads(request.POST.get('datastring'))
        event_id = body['id']

        event = Event.objects.get(id=event_id)
        if request.user.id in event.dislikes.all():
            event.dislikes.remove(request.user.id)
        else:
            event.dislikes.add(request.user.id)
            event.likes.remove(request.user.id)

        if not UserEvent.objects.filter(user_id=request.user.id, event_id=event_id).exists():
            event = UserEvent.objects.create(user_id=request.user.id, event_id=event_id, dislike=True)
        else:
            event = UserEvent.objects.get(user_id=request.user.id, event_id=event_id)
            if not event.dislike:
                event.like = False
                event.dislike = True
            else:
                event.dislike = False
        event.save()

        return JsonResponse({"status": "succes", "message": "event disliked"})
    else:
        return JsonResponse({"status": "failed", "message": "user not loggeed in"})

