# Create your views here.
import json

import numpy as np
import pandas as pd
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from pkgs.charts import bar_json, line_json
from pkgs.fault import FaultStatistics
from pkgs.fault_offshore import FaultStatisticsOffshore
from pkgs.utils.tools import HiddenPrints


def root(request: HttpRequest) -> HttpResponse:
    # 跳转到index页面
    return redirect('/index')


def index(request: HttpRequest) -> HttpResponse:
    context = {}
    return render(request, 'test_app1/index.html', context=context)


def fault_statistics(request: HttpRequest) -> HttpResponse:
    context = {
        'start':
        (pd.to_datetime('now') - pd.to_timedelta('61d')).strftime('%Y-%m-%d'),
        'end':
        (pd.to_datetime('now') - pd.to_timedelta('1d')).strftime('%Y-%m-%d'),
    }
    return render(request, 'test_app1/fault_statistics.html', context=context)


def vibration_analysis(request: HttpRequest) -> HttpResponse:
    context = {
        'start':
        (pd.to_datetime('now') - pd.to_timedelta('61d')).strftime('%Y-%m-%d'),
        'end':
        (pd.to_datetime('now') - pd.to_timedelta('1d')).strftime('%Y-%m-%d'),
    }

    return render(request,
                  'test_app1/vibration_analysis.html',
                  context=context)


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
        context['chart'].append(bar_json(df[['故障名称_中文', y_label_0]],
                                         y_label_0))
        df = df.sort_values(by=y_label_1, ascending=False)
        context['chart'].append(bar_json(df[['故障名称_中文', y_label_1]],
                                         y_label_1))
        context['id'] = 1
        # 打包为json，回传
        context = json.dumps(context)
        return HttpResponse(context)

    if request.GET['view'] == 'test7':
        context = {}
        start = str(request.GET['start'])
        end = str(request.GET['end'])
        with HiddenPrints():
            fs = FaultStatisticsOffshore(fault_map_path='config/风机故障代码表.csv')
            df = fs.get_single(
                wt=f'00{request.GET["id"]}#',
                src_path=r'D:\风机数据\_公司网盘数据\粤电沙扒statuslog_',
                start=start,
                end=end,
            )
        df['持续时间'] = df['持续时间'].astype(float).round(2)
        df = df[df['持续时间'] > 0.1]
        context['table'] = df.to_html(
            classes='table table-bordered table-hover', index=False)

        context['chart'] = []
        df = df.sort_values(by='持续时间', ascending=False)
        context['chart'].append(
            bar_json(df[['故障描述_中文', '持续时间']].head(10), '故障时间(小时)'))

        df = df.sort_values(by='故障次数', ascending=False)
        context['chart'].append(
            bar_json(df[['故障描述_中文', '故障次数']].head(10), '故障次数'))
        context['id'] = 1
        # 打包为json，回传
        context = json.dumps(context)
        return HttpResponse(context)

    if request.GET['view'] == 'test8':
        context = {}
        start = str(request.GET['start'])
        end = str(request.GET['end'])
        context['chart'] = []
        df = pd.DataFrame()
        df['时间'] = pd.date_range(start=start, end=end,
                                 freq='1d').strftime('%Y-%m-%d')
        df['1p频率'] = np.random.randint(0, 100, len(df))
        df['3p频率'] = np.random.randint(0, 100, len(df))
        context['chart'].append(
            line_json(
                df.drop(columns=['时间']),
                df['时间'].to_list(),
                title='振动频率',
            ))
        context = json.dumps(context)
        return HttpResponse(context)
