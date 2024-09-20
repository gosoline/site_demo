# Create your views here.
import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
import pandas as pd
import numpy as np
from pkgs.charts import bar_json
from pkgs.fault import FaultStatistics
from pkgs.utils.tools import HiddenPrints


def test(request: HttpRequest) -> HttpResponse:
    context = {
        'start':
        (pd.to_datetime('now') - pd.to_timedelta('61d')).strftime('%Y-%m-%d'),
        'end':
        (pd.to_datetime('now') - pd.to_timedelta('1d')).strftime('%Y-%m-%d'),
    }
    return render(request, 'test_app/test1.html', context=context)


def get_data(request: HttpRequest) -> HttpResponse:
    if request.GET['view'] == 'test1':
        context = {}
        start = str(request.GET['start'])
        end = str(request.GET['end'])
        with HiddenPrints():
            fs = FaultStatistics(
                src_path=r'D:\风机数据\PLCdata\Statuscode',
                start=start,
                end=end,
                # start='20240401',
                # end='20240601',
                fault_map_path='config/fault_map.csv',
                wt_list=[20],
            )
            fs.get_fault()
            df = fs.get_fault_simple()

        # lose_file = df['lose_file'].iloc[-1]
        df = df.drop(df.index[-1], axis=0).drop('lose_file', axis=1)
        df['timedelta'] = (
            pd.to_timedelta(df['timedelta']).dt.total_seconds() /
            3600).round(2)
        df = df.rename(
            columns={
                'wt_id': '风机编号',
                'code': '故障代码',
                'fault_en': '故障名称_英文',
                'fault_cn': '故障名称_中文',
                'count': '故障次数',
                'timedelta': '故障时间(小时)',
            },
            inplace=False,
        )[['风机编号', '故障代码', '故障名称_中文', '故障名称_英文', '故障次数', '故障时间(小时)']]

        context['table'] = df.to_html(
            classes='table table-bordered table-hover', index=False)
        y_label_0 = '故障时间(小时)'
        y_label_1 = '故障次数'
        context['chart'] = []
        df = df.sort_values(by=y_label_0, ascending=False)
        context['chart'].append(bar_json(df[['故障名称_中文', y_label_0]], y_label_0))
        df = df.sort_values(by=y_label_1, ascending=False)
        context['chart'].append(bar_json(df[['故障名称_中文', y_label_1]], y_label_1))
        context['id'] = 1
        # 打包为json，回传
        context = json.dumps(context)
        return HttpResponse(context)
