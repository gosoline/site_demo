# -*- coding: utf-8 -*-
"""
@File    : fault_statistics.py
@Time    : 2024/01/21 16:13:13
@Author  : WuHaiYue
@Version : 1.0
@Desc    : 故障分析模块
"""

from __future__ import annotations

import warnings
from pathlib import Path
from traceback import print_exc
from typing import Literal

import pandas as pd


def time_at(dt: pd.Timestamp | str, step: pd.Timedelta | str) -> pd.Timestamp:
    '''
    ~获取所在时间段

    Parameters
    ----------
    dt: 时间日期
    step: 时间步长
    '''
    dt: pd.DatetimeIndex = pd.to_datetime([dt])
    step: pd.Timedelta = pd.Timedelta(step)
    t = pd.to_datetime(
        ((dt.astype('int64') // 10**9) // int(step.total_seconds())) *
        int(step.total_seconds()),
        unit='s',
    )[0]
    return t


class FaultStatistics:
    '''
    ~用于分析故障代码
    '''

    # SC_TURBINE_AVAILABLE 故障复位时间
    # OC_BrakeProgramActive 停机时间

    turbine_start: Literal['SC_TURBINE_AVAILABLE'] = 'SC_TURBINE_AVAILABLE'
    '''启机 `SC_TURBINE_AVAILABLE`'''
    turbine_stop: Literal['OC_BrakeProgramActive'] = 'OC_BrakeProgramActive'
    '''停机 `OC_BrakeProgramActive`'''
    # 故障包含信息list
    _fault_info = [
        'wt_id', 'file_name', 'stop_row', 'fault_row', 'stop_time',
        'fault_time', 'code', 'fault_en', 'fault_cn', 'timedelta'
    ]
    _fault_simple_info = [
        'wt_id', 'code', 'count', 'fault_en', 'fault_cn', 'timedelta',
        'lose_file'
    ]

    def __init__(
        self,
        src_path: str,
        fault_map_path: str = None,
        wt_list: list[int | str] = None,
        start: str = None,
        end: str = None,
    ) -> None:
        '''
        ~初始化故障代码分析类

        Parameters
        ----------
        - src_path: 所有风机状态代码文件所在路径
        - fault_map_path: 故障代码映射表路径
        - wt_list: 风机列表，例如`wt_list=[1, 2, 3, 4]`
        - start: 开始日期，包含本天，例如`start='20231201'`，为None表示30天前
        - end: 结束日期，包含本天，例如`start='20231221'`，为None表示为昨天
        '''
        # 去除ParserWarning警告，该警告会在读取文件时出现，因为表头结尾无分隔符但是数据结尾有分隔符
        warnings.filterwarnings("ignore", category=pd.errors.ParserWarning)
        # 处理输入参数
        self.src_path = Path(src_path)
        self.fault_map_df: pd.DataFrame = None
        if not fault_map_path is None:
            # 故障映射表
            self.fault_map_df = pd.read_csv(
                fault_map_path,
                header=0,
                index_col=False,
            )
            self.fault_map_df.index = self.fault_map_df['故障代码']
        if wt_list is None:
            self.wt_list = [folder.name for folder in self.src_path.iterdir()]
        else:
            self.wt_list = [str(wt) for wt in wt_list]
        if start is None:
            start = pd.Timestamp.now() - pd.Timedelta('31d')
        else:
            start = pd.to_datetime(start)
        if end is None:
            end = pd.Timestamp.now() - pd.Timedelta('1d')
        else:
            end = pd.to_datetime(end)

        start = time_at(start, '1d')
        end = time_at(end, '1d')

        self.dt_list: pd.DatetimeIndex = pd.date_range(start, end)

        # 存储故障信息的DataFrame
        self.fault_df: pd.DataFrame = None
        # 存储简易故障信息的DataFrame
        self.fault_simple_df: pd.DataFrame = None
        # 存储丢失文件的dict
        self.lose_file: dict[str, list[str]] = None

    @classmethod
    def read_file(
        cls,
        path: str,
        wt_id: str = '_',
        file_name: str = '_',
    ) -> pd.DataFrame:
        '''
        ~读取单个状态代码文件,并筛选

        Parameters
        ----------
        - path: 状态代码文件路径
        - wt_id: 风机编号
        - file_name: 文件名称
        '''
        skiprows = 11
        df = pd.read_csv(
            path,
            skiprows=skiprows,
            header=0,
            index_col=False,
            sep='\t',
        )
        # 去除列索引前后空白字符
        df.columns = [col.strip() for col in df.columns]
        df = df[['TimeStampUTC', 'TrigKey']]
        # 去除数据前后空白字符
        df = df.map(lambda e: e.strip())
        # 时间列转化为Timestamp
        df['time'] = pd.to_datetime(df.pop('TimeStampUTC'),
                                    format='%d.%m.%Y %H:%M:%S,%f')
        # 将TrigKey列划分为代码列和英文描述列
        df[['code', 'fault_en']] = df.pop('TrigKey').str.split(expand=True)
        # 删除有nan值的行
        df = df.dropna(how='any')
        # 过滤非故障行
        df = df[df['fault_en'].apply(cls._filter)]
        # 原文件行数
        df['row_num'] = df.index + skiprows + 2
        # 风机编号
        df['wt_id'] = wt_id
        # 文件名称
        df['file_name'] = file_name
        # 重新排序列
        df.reindex(columns=[
            'wt_id', 'file_name', 'row_num', 'time', 'code', 'fault_en'
        ])

        return df

    @classmethod
    def _filter(cls, s: str) -> bool:
        '''
        ~用于过滤正常的状态代码

        Parameters
        ---------
        - s: 状态代码英文描述
        '''
        return s.lower().startswith('sc_') or s == cls.turbine_stop

    def _get_df_fault(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        ~获取单台风机的故障代码

        Parameters
        ----------
        - df: 状态代码数据
        '''
        # 按时间排序，重设索引
        df = df.sort_values('time').reset_index(drop=True)
        # 上次读取的状态（启机或停机）
        last: str = None
        # 存储启机和停机出新的索引行
        fault_row_list = []
        # 循环查找启机和停机所在行
        for idx in df.index:
            if df.loc[idx,
                      'fault_en'] in [self.turbine_start, self.turbine_stop]:
                # 判断是否为连续的启机或停机，连续出现视为一次
                if df.loc[idx, 'fault_en'] != last:
                    fault_row_list.append(idx)

                last = df.loc[idx, 'fault_en']
        # 如果最先出现启机则停机出现在前一天，无法判断停机的时间和原因，所以跳过
        if len(fault_row_list) > 0:
            if df['fault_en'].loc[fault_row_list[0]] == self.turbine_start:
                fault_row_list.pop(0)
        # 如果最后出现停机，则将本天后剩余时间视为故障时间
        if len(fault_row_list) > 0:
            if df['fault_en'].loc[fault_row_list[-1]] == self.turbine_stop:
                fault_row_list.append(df.index[-1])
        # 存储故障的各种信息
        fault_df = pd.DataFrame(columns=self._fault_info)

        ## 经过以上处理后fault_row_list始终为停机和启机交替出现，则停机和启机之间的时间为故障时间

        i = 0
        while i < len(fault_row_list) - 1:
            dfx = df.loc[fault_row_list[i]:fault_row_list[i + 1]]
            # 风机停机时刻
            turbine_stop_dt = dfx['time'].iloc[0]
            # 首触故障代码所在可能时间（取停机代码出现时间的前后一分钟）
            first_trigger_df = df[df['time'].between(
                turbine_stop_dt - pd.Timedelta('60s'),
                turbine_stop_dt + pd.Timedelta('60s'))]
            i = i + 2
            for idx in first_trigger_df.index:
                val = first_trigger_df.loc[idx, 'fault_en']
                # 以sc_开头并且不为启机代码的最先出现的代码为首触故障
                if val.lower().startswith('sc_') and val != self.turbine_start:
                    fault_zh = '_'
                    if not self.fault_map_df is None:
                        try:
                            fault_zh = self.fault_map_df.loc[
                                first_trigger_df.loc[idx, 'code'], '中文描述']
                        except:
                            fault_zh = '无中文映射'
                    fault_df.loc[dfx.index[0]] = [
                        dfx['wt_id'].iloc[0],  # 风机编号
                        dfx['file_name'].iloc[0],  # 状态代码文件名称
                        dfx['row_num'].iloc[0],  # 停机代码所在行
                        first_trigger_df.loc[idx, 'row_num'],  # 首触故障所在行
                        turbine_stop_dt,  # 风机停机时刻
                        *first_trigger_df.loc[idx,
                                              ['time', 'code', 'fault_en'
                                               ]],  # 首触故障时刻，状态代码，状态英文描述
                        fault_zh,  # 状态中文描述
                        dfx['time'].iloc[-1] - dfx['time'].iloc[0],  # 故障持续时长
                    ]
                    break
        fault_df = fault_df.reset_index(drop=True)

        return fault_df

    def get_fault(self) -> pd.DataFrame | None:
        '''
        ~获取实例故障代码汇总
        '''
        self.fault_df = pd.DataFrame(columns=self._fault_info)
        self.lose_file = {}
        all_df_list = []
        # 循环读取文件
        for wt in self.wt_list:
            wt_df_list = []
            for dt in self.dt_list:
                dt_str = dt.strftime("%Y%m%d")
                file = self.src_path / wt / f'BufferStatuscodes{dt_str}.txt'
                print(file)
                try:
                    print(f'风机: {wt:<6}文件名: {file.name:<40}', end='')
                    df = self.read_file(file, wt_id=wt, file_name=file.name)
                    wt_df_list.append(df)
                    print('--成功')
                except FileNotFoundError:
                    print('--不存在')
                    # 将该天加入丢失文件dict
                    if wt in self.lose_file:
                        self.lose_file[wt].append(dt_str)
                    else:
                        self.lose_file[wt] = [dt_str]
                except pd.errors.EmptyDataError:
                    print('--成功(空表)')
                except:
                    print('--失败')
                    print_exc()
            if len(wt_df_list) > 0:
                # 合并数据
                df = pd.concat(wt_df_list, axis=0, ignore_index=True)
                # 分析故障
                df = self._get_df_fault(df=df)
                all_df_list.append(df)
        if len(all_df_list) > 0:
            # 合并数据
            self.fault_df = pd.concat(all_df_list, axis=0, ignore_index=True)

        # 将丢失文件加入故障信息数据
        for wt in self.lose_file.keys():
            for dt in self.lose_file[wt]:
                self.fault_df.loc[self.fault_df.shape[0] + 1,
                                  ['wt_id', 'file_name']] = [wt, f'{dt}_lose']
        self.fault_df = self.fault_df[self.fault_df['fault_en'] !=
                                      'SC_WaitingForWind']

        self.fault_df['wt_id'] = self.fault_df['wt_id'].astype('int')
        self.fault_df = self.fault_df.sort_values('wt_id')

        return self.fault_df

    def get_fault_simple(self):
        '''
        ~获取实例故障代码汇总简表
        '''
        if self.fault_df is None:
            self.get_fault()
        self.fault_simple_df = pd.DataFrame(columns=self._fault_simple_info)
        for wt_id, dfx in self.fault_df.groupby('wt_id'):
            lose_file = dfx['file_name'][dfx['file_name'].str.endswith(
                'lose')].values.tolist()
            dfx = dfx[~(dfx['file_name'].str.endswith('lose'))]
            # ['wt_id', 'code', 'count', 'fault_en','fault_cn', 'timedelta', 'lose_file']
            for code, dfx1 in dfx.groupby('code'):
                self.fault_simple_df.loc[f'{wt_id}&{code}'] = [
                    wt_id,
                    code,
                    dfx1.shape[0],
                    dfx1['fault_en'].iloc[0],
                    dfx1['fault_cn'].iloc[0],
                    dfx1['timedelta'].sum(),
                    '_',
                ]
            self.fault_simple_df.loc[f'{wt_id}&lose',
                                     'lose_file'] = f"[{','.join(lose_file)}]"
            self.fault_simple_df.loc[f'{wt_id}&lose', 'wt_id'] = wt_id
        self.fault_simple_df['wt_id'] = self.fault_simple_df['wt_id'].astype(
            'int')
        self.fault_simple_df.sort_values('wt_id')
        return self.fault_simple_df
        ...


def fault_control(
    fault_map_path: str | Path,
    src_path: str | Path,
    dst_path: str | Path,
):
    """
    ~:故障统计

    Parameters
    ----------
    - fault_map_path: str | Path,故障代码映射表路径
    - src_path: str | Path,Statuscode文件夹路径
    - dst_path: str | Path,存储生成表的路径
    """
    today = pd.Timestamp.now()
    fs = FaultStatistics(
        src_path=src_path,
        # start='20231001',
        fault_map_path=fault_map_path,
        # wt_list=[1, 2],
    )
    fs.get_fault()
    fs.get_fault_simple()
    doc_path = dst_path
    # doc_path = Path('./')
    doc_path.mkdir(0o777, True, True)
    fs.fault_df.to_csv(
        doc_path /
        f'fault_{(today - pd.Timedelta("1d")).strftime("%Y%m%d")}.csv',
        index=False,
        encoding='gbk',
    )
    fs.fault_simple_df.to_csv(
        doc_path /
        f'fault_simple_{(today - pd.Timedelta("1d")).strftime("%Y%m%d")}.csv',
        index=False,
        encoding='gbk',
    )


if __name__ == '__main__':
    src_path = Path(r"D:\Statuscode")
    fs = FaultStatistics(
        src_path=src_path,
        # wt_list=[1, 2],
        start='20230701',
        # end='20230810',
        fault_map_path='fault_map.csv',
    )
    fs.get_fault()
    print(fs.fault_df)
