from django.test import TestCase

# Create your tests here.
from django.shortcuts import render

# Create your views here.
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def test(request: HttpRequest) -> HttpResponse:
    return render(request, 'blog/test.html')
