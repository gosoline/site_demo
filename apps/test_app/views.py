# Create your views here.
import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
import pandas as pd
import numpy as np
from pkgs.charts import scatter_json


def test(request: HttpRequest) -> HttpResponse:
    return render(request, 'test_app/test.html')


def get_data(request: HttpRequest) -> HttpResponse:
    request.GET['mod']
    context = {}
    df = pd.DataFrame({
        'x': np.arange(10),
        'y': np.random.randint(0, 10, (1, 10))[0]
    })
    context['chart1'] = scatter_json(df)
    context['id'] = 1

    # 打包为json，回传
    context = json.dumps(context)
    return HttpResponse(context)
