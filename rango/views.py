from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hey there partner!\nAbout page: <a href='/rango/about/'>About</a>")

def about(request):
    return HttpResponse("Rango says here is the about page\n" + "Home page: <a href='/rango/'>About</a>")