from django.http import HttpResponse

def index(request):
    return HttpResponse("Manager home")

def blogHome(request):
