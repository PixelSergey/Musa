from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
import requests
import random
import re

music = []
current = {}
e = "^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"

with open("admins.txt", "r") as f:
    admins = f.readlines()

def is_admin(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip in admins


def getredirect(loc, **kwargs):
    resp = redirect(loc)
    resp["Location"] += "?"
    for key, val in kwargs.items():
        resp["Location"] += key + "=" + val + "&"
    resp["Location"] = resp["Location"][:-1]
    print(resp["Location"])
    return resp


def index(request):
    if request.method != "GET":
        raise PermissionDenied
    
    msg = request.GET["msg"] if "msg" in request.GET else None

    return render(request, "player/index.html", {
        "music" : music,
        "current" : current,
        "msg" : msg,
        "admin" : is_admin(request),
        })


def add(request):
    if request.method != "POST":
        raise PermissionDenied

    if not "url" in request.POST or request.POST["url"] == "":
        return getredirect("/", msg="Unohtuko linkki?")

    url = request.POST["url"].strip()

    vidid = re.findall(e, url)
    if not vidid or len(vidid[0]) < 7 or len(vidid[0][6]) != 11:
        print("Invalid URL", url)
        return getredirect("/", msg="Linkkisi taitaa olla vähän rikki")

    url = "https://www.youtube.com/watch?v=" + vidid[0][6]
    r = requests.get("https://www.youtube.com/oembed?format=json&url=" + url)
    data = r.json()
    
    if data["author_name"].endswith(" - Topic"):
        data["author_name"] = data["author_name"][:-8]
    if len(data["title"]) >= 68:
        data["title"] = data["title"][:65] + "..."
    if len(data["author_name"]) >= 17:
        data["author_name"] = data["author_name"][:14] + "..."

    music.append({"id":random.randint(0, 2147483647),"url":url, "title":data["title"], "author":data["author_name"], "thumbnail":data["thumbnail_url"]})
    print("Added to playlist:", music[-1])
    return redirect("/")


@csrf_exempt
def next(request):
    global current
    if request.method != "POST":
        raise PermissionDenied
    
    if not is_admin(request):
        raise PermissionDenied

    if not music:
        current = {}
        return HttpResponse("NULL", content_type="text/plain")
    
    current = music.pop(0)
    return HttpResponse(current["url"], content_type="text/plain")


@csrf_exempt
def delete(request):
    global music
    if request.method != "POST":
        raise PermissionDenied

    if not is_admin(request):
        raise PermissionDenied

    if not "id" in request.POST:
        return getredirect("/", msg="ID puuttuu")

    music = [biisi for biisi in music if str(biisi["id"]) != request.POST["id"]]
    
    return redirect("/")


@csrf_exempt
def stop(request):
    global current
    if request.method != "POST":
        raise PermissionDenied
    
    if not is_admin(request):
        raise PermissionDenied

    current = {}
    return HttpResponse("Stopped", content_type="text/plain")