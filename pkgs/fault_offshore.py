# -*- coding: utf-8 -*-
"""
@File    : fault_offshore.py
@Time    : 2024/09/05 10:00:38
@Author  : WHY
@Version : 1.0
@Desc    : None
"""
from __future__ import annotations
from traceback import print_exc
import pandas as pd
from pathlib import Path
import csv


class FaultStatisticsOffshore:

    def __init__(self, fault_map_path: str | Path) -> None:

        self.header = {
            'SeqNo': '序号',
            'TriggerTime': '触发时间',
            'Description': '故障描述_英文',
            'OperationMode': '运行模式',
            'WindSpeed': '风速',
            'RotorSpeed': '转速',
            'GeneratorSpeed': '发电机转速',
            'PowerOutPut': '发电机功率',
            'PitchPosition': '俯仰角',
            'PowerSetPoint': '功率设定值',
            'Res': '复位时间',
            'Error': '持续时间'
        }
        self.fault_map_df = self.get_map(fault_map_path)

    def get_single(self, wt: str, src_path: str | Path, start: str, end: str):
        src_path = Path(src_path)
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)
        df_list = []
        for file in (src_path / 'Statuscode' / wt).iterdir():
            if file.name.startswith('ErrorList') and file.suffix == '.csv':
                try:
                    dt = pd.to_datetime(file.stem[9:])
                    if start <= dt <= end:
                        print(file)
                        df = pd.read_csv(
                            file,
                            skiprows=8,
                            skipfooter=1,
                            encoding='utf8',
                            header=None,
                            engine='python',
                        )
                        df_list.append(df)
                except:
                        print_exc()
        df = pd.concat(df_list, axis=0, ignore_index=True)
        df.columns = self.header.values()
        df[['触发时间', '故障描述_英文', '复位时间',
            '持续时间']] = df[['触发时间', '故障描述_英文', '复位时间',
                           '持续时间']].apply(lambda x: x.str.strip())
        df['持续时间'] = -pd.to_timedelta(df['持续时间'])
        df = df[df['持续时间'] > pd.to_timedelta(0)]
        df['故障代码'] = df['故障描述_英文'].str.split('_SC_', expand=True)[0]
        df.index = df['故障代码']
        df['故障描述_中文'] = self.fault_map_df.loc[df['故障代码'], '故障描述_中文']
        df['故障等级'] = self.fault_map_df.loc[df['故障代码'], '故障等级']

        result_df = pd.DataFrame(
            columns=['故障代码', '故障描述_英文', '故障描述_中文', '故障次数', '持续时间'])
        for error_code, group in df.groupby(df['故障代码']):
            result_df.loc[error_code, '故障代码'] = error_code
            result_df.loc[error_code, '故障描述_英文'] = group['故障描述_英文'].iloc[0]
            result_df.loc[error_code, '故障描述_中文'] = group['故障描述_中文'].iloc[0]
            result_df.loc[error_code, '故障等级'] = group['故障等级'].iloc[0]
            result_df.loc[error_code, '故障次数'] = len(group)
            result_df.loc[error_code,
                          '持续时间'] = group['持续时间'].sum().total_seconds() / 3600
        return result_df

    def get_map(self, fault_map_path: str | Path) -> pd.DataFrame:
        fault_map_df = pd.read_csv(
            fault_map_path,
            header=0,
            index_col=False,
            encoding='utf8',
            dtype={'故障代码': str},
        )
        fault_map_df.index = fault_map_df['故障代码']
        # from collections import Counter
        # print(Counter(fault_map_df.index))
        return fault_map_df

    @staticmethod
    def get_map_csv():
        df = pd.read_excel(r"D:\Users\117483\桌面\海上项目场控点表-20240606.xlsx",
                           sheet_name='风机故障代码表')
        df.rename(columns={
            '故障描述': '故障描述_中文',
            '故障描述.1': '故障描述_英文'
        },
                  inplace=True)
        df[['故障描述_中文',
            '故障描述_英文']] = df[['故障描述_中文',
                              '故障描述_英文']].apply(lambda x: x.str.strip())
        df['故障代码'] = df['故障描述_英文'].str.split('_SC_', expand=True)[0]
        df.index = df['故障代码']
        df.to_csv(r'./config/风机故障代码表.csv', index=False, quoting=csv.QUOTE_ALL)


if __name__ == '__main__':

    src_path = r'D:\风机数据\_公司网盘数据\粤电沙扒statuslog_'
    fault_map_path = r'./config/风机故障代码表.csv'
    start = '2024-06-01'
    end = '2024-07-08'
    wt = '001#'

    fs = FaultStatisticsOffshore(fault_map_path=fault_map_path)
    df = fs.get_single(wt=wt, src_path=src_path, start=start, end=end)
    print(df)
    # df.to_csv(f'./tmp/{wt}_{start}_{end}.csv', index=False)
