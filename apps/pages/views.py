from django.shortcuts import render

def home(request):
    return render(request, "pages/index.html")

def api_docs(request):
    return render(request, "pages/api_docs.html")