from django.shortcuts import render
from .models import Event, UserEvent
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.http.response import JsonResponse
import json


# Create your views here.

def index(request):
    filter_cat = Event.objects.values("categories").distinct()
    if request.method == "POST":
        start_date = request.POST.get("start_date", None)
        end_date = request.POST.get("end_date", None)
        category = request.POST.get("category")
        key = request.POST.get("keyword")
        filter_dict = {}
        if start_date and end_date:
            filter_dict["end_date__date__range"] = [start_date, end_date]
        if category:
            filter_dict["categories"] = category
        if key:
            q = Q()
            q |= Q(title__icontains=key)
            q |= Q(description__icontains=key)
            events = Event.objects.filter(end_date__date__gte=datetime.today().date()).filter(**filter_dict).filter(
                q).order_by('start_date')
        else:
            events = Event.objects.filter(end_date__date__gte=datetime.today().date()).filter(**filter_dict).order_by(
                'start_date')
    else:
        events = Event.objects.filter(end_date__date__gte=datetime.today().date()).order_by('start_date')
    if request.user.is_authenticated:
        liked_events = UserEvent.objects.filter(user_id=request.user.id, like=True)
        liked_event_ids = [event.event_id for event in liked_events]
        for event in events:
            if event.id in liked_event_ids:
                event.liked = True
        disliked_events = UserEvent.objects.filter(user_id=request.user.id, dislike=True)
        disliked_event_ids = [event.event_id for event in disliked_events]
        for event in events:
            if event.id in disliked_event_ids:
                event.disliked = True

    return render(request, 'events.html', {'events': events, 'category': filter_cat})


def like_event(request):
    if request.user.is_authenticated:
        body = json.loads(request.POST.get('datastring'))
        event_id = body['id']
        if not UserEvent.objects.filter(user_id=request.user.id, event_id=event_id).exists():
            event = UserEvent.objects.create(user_id=request.user.id, event_id=event_id, like=True)
        else:
            event = UserEvent.objects.get(user_id=request.user.id, event_id=event_id)
            if not event.like:
                event.like = True
                event.dislike = False
            else:
                event.like = False
        event.save()

        return JsonResponse({"status": "succes", "message": "event liked"})
    else:
        return JsonResponse({"status": "failed", "message": "user not loggeed in"})


def dislike_event(request):
    if request.user.is_authenticated:
        body = json.loads(request.POST.get('datastring'))
        event_id = body['id']
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

