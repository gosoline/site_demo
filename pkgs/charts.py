import math

import numpy as np
import pandas as pd
from pandas import DataFrame
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts.basic_charts.bar import Bar
from pyecharts.charts.basic_charts.gauge import Gauge
from pyecharts.charts.basic_charts.heatmap import HeatMap
from pyecharts.charts.basic_charts.line import Line
from pyecharts.charts.basic_charts.polar import Polar
from pyecharts.charts.basic_charts.scatter import Scatter
from pyecharts.charts.composite_charts.grid import Grid
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType

mycolors = (
    "#2A579A",
    "#FF7F0E",
    "#227447",
    "#D62728",
    "#9467BD",
    "#8C564B",
    "#E377C2",
    "#808080",
)


def scatter_json(data: pd.DataFrame, title: str = "", f_size: int = 15):
    """
    【散点图】自动生成前端echarts控件需要的图像选项

    Parameters
    ----------
    data : DataFrame ~ 需要绘制的数据
    title : str, optional ~ 图表标题，会显示在左上角, by default ''
    f_size : int, optional ~ 图表字体大小, by default 15

    Returns
    -------
    str ~ 已被打包好的json文本字符串，前端只要使用JSON.parse即可使用
    """
    # 处理数据获取x,y
    x_data = data[data.columns[0]].astype(float).to_numpy().round(4)
    y_data = data[data.columns[1]].astype(float).to_numpy().round(4)
    x_bound = math.ceil(max(abs(x_data.max()), abs(x_data.min()))) + 1
    # 创建绘画区
    chart_scatter = (
        Scatter(
            init_opts=opts.InitOpts(
                # 关闭动画效果
                animation_opts=opts.AnimationOpts(animation=False),
            )
        )
        .add_xaxis(xaxis_data=x_data)  # 添加x轴数据
        .add_yaxis(  # 添加y轴数据
            # 数据系列名称
            series_name="",
            # 具体数据
            y_axis=y_data,
            # 颜色
            color="firebrick",
            # 标记大小
            symbol_size=math.floor(f_size * 0.6),
            # 设置不显示点数值
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(  # 全局配置项
            # 设置标题
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=math.ceil(f_size * 1.2),
                ),
                pos_left="50%",
                pos_top="1.5%",
                text_align="center",
                text_vertical_align="center",
            ),
            # 设置不显示图例
            legend_opts=opts.LegendOpts(is_show=False),
            # x轴上下限设置
            xaxis_opts=opts.AxisOpts(
                name=str(data.columns[0]),
                name_location="center",
                name_gap=math.ceil(f_size * 2),
                # min_=-x_bound,
                # max_=x_bound,
                min_=0,
                max_=10,
            ),
            # y轴上下限设置
            yaxis_opts=opts.AxisOpts(
                name=str(data.columns[1]),
                name_location="center",
                name_gap=math.ceil(f_size * 3),
                # min_=math.floor(y_data.min() * 0.9),
                # max_=math.ceil(y_data.max() * 1.1),
                min_=0,
                max_=10,
            ),
            # 设置鼠标移动到点上时不显示数值
            tooltip_opts=opts.TooltipOpts(
                is_show=False,
            ),
        )
    )
    # 测试使用，会渲染成html文件查看效果
    # chart_scatter.render('scatter.html')
    return chart_scatter.dump_options_with_quotes()


def bar_json(
    data: pd.DataFrame,
    title: str = "",
    f_size: int = 15,
):
    """
    【柱状图】自动生成前端echarts控件需要的图像选项

    Parameters
    ----------
    data : DataFrame ~ 需要绘制的数据
    title : str, optional ~ 图表标题，会显示在左上角, by default ''
    f_size : int, optional ~ 图表字体大小, by default 15

    Returns
    -------
    str ~ 已被打包好的json文本字符串，前端只要使用JSON.parse即可使用
    """
    # 初始化绘图网格和折线绘图区
    chart_grid = Grid(
        init_opts=opts.InitOpts(
            # 关闭动画效果
            # animation_opts=opts.AnimationOpts(animation=False),
        )
    )
    chart_bar = (
        Bar()
        .add_xaxis(data[data.columns[0]].to_list())
        .add_yaxis(str(data.columns[1]), data[data.columns[1]].to_list())
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                name=str(data.columns[0]),
                axislabel_opts=opts.LabelOpts(rotate=-15, font_size=10),
            ),
            yaxis_opts=opts.AxisOpts(
                name=str(data.columns[1]),
            ),
            title_opts=opts.TitleOpts(title=title),
        )
    )
    # 全局图像配置
    chart_bar = chart_bar.set_global_opts(
        # 设置标题
        title_opts=opts.TitleOpts(
            title=title,
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=math.ceil(f_size * 1.2),
            ),
            pos_left="50%",
            pos_top="1.5%",
            text_align="center",
            text_vertical_align="center",
        ),
        # # 设置X轴通用属性
        # xaxis_opts=opts.AxisOpts(
        #     min_=0,
        #     max_=data.shape[0],
        # ),
        # # 设置Y轴通用属性
        # yaxis_opts=opts.AxisOpts(
        #     is_scale=True,
        #     boundary_gap='1%',
        #     splitline_opts=opts.SplitLineOpts(is_show=False),
        # ),
        # 图例属性，无边框，距离顶部3%
        legend_opts=opts.LegendOpts(
            border_width=0,
            pos_top="6%",
        ),
        # 鼠标移动到图像上显示任意节点数据
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        # 工具箱属性，允许便捷保存调整图像大小与缩放
        toolbox_opts=opts.ToolboxOpts(
            # is_show=False,
            pos_top="3%",
            # 不允许直接查看元数据以及变化图像类型
            feature=opts.ToolBoxFeatureOpts(
                restore=opts.ToolBoxFeatureRestoreOpts(is_show=False),
                data_view=opts.ToolBoxFeatureDataViewOpts(is_show=True),
                magic_type=opts.ToolBoxFeatureMagicTypeOpts(is_show=True),
                data_zoom=opts.ToolBoxFeatureDataZoomOpts(is_show=False),
            ),
        ),
    )
    # 折线图像添加到绘图网格中
    chart_grid.add(
        chart_bar,
        # 左右边距设置
        grid_opts=opts.GridOpts(),
        is_control_axis_index=True,
    )
    # 测试使用，会渲染成html文件查看效果
    # chart_bar.render('bar.html')
    return chart_grid.dump_options_with_quotes()


def line_json(
    data: DataFrame,
    xdata: list,
    title: str = "",
    f_size: int = 15,
    colors: list = mycolors,
):
    """
    【直角坐标折线图】自动生成前端echarts控件需要的图像选项

    Parameters
    ----------
    data : DataFrame ~ 要显示的数据
    xdata: list~横轴显示时间
    title : str ~ 可选，图表标题，默认为''
    f_size : int ~ 可选，字体大小，默认为15
    colors : list ~ 可选，曲线颜色列表

    Returns
    -------
    str ~ 已被打包好的json文本字符串，前端只要使用JSON.parse即可使用
    """
    if not data.empty:
        # 初始化绘图网格和折线绘图区
        chart_grid = Grid(
            init_opts=opts.InitOpts(
                # 关闭动画效果
                # animation_opts=opts.AnimationOpts(animation=False),
            )
        )
        chart_line = Line(
            init_opts=opts.InitOpts(
                # 关闭动画效果
                animation_opts=opts.AnimationOpts(animation=False),
            )
        ).add_xaxis(
            # x轴数据导入
            xdata
        )
        # 记录绘制曲线数，用于最后调整图表样式
        line_count = 0
        # 设置最大仅显示8条曲线

        for i in range(min(len(data.columns), 8)):
            # 该列数据不为数字
            if not isinstance(data[data.columns[i]][0], np.number):
                continue
            # 取出数据并取四位小数
            y_data = data[data.columns[i]].to_numpy().astype(float).round(4).tolist()
            # 设置y轴样式
            chart_line = chart_line.extend_axis(
                yaxis=opts.AxisOpts(
                    # 奇数Y轴在左侧，偶数在右侧
                    position="left" if i % 2 == 0 else "right",
                    # 其他Y轴添加偏移
                    offset=math.floor(i / 2) * 50,
                    # 各类颜色设置，与曲线颜色一致
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(color=colors[i])
                    ),
                    axistick_opts=opts.AxisTickOpts(
                        linestyle_opts=opts.LineStyleOpts(color=colors[i])
                    ),
                    axislabel_opts=opts.LabelOpts(color=colors[i]),
                )
            )
            # 添加Y轴
            chart_line = chart_line.add_yaxis(
                # 数据名称
                series_name=str(data.columns[i]),
                # 绑定数据
                y_axis=y_data,
                # 不显示节点数值
                label_opts=opts.LabelOpts(is_show=False),
                # Y轴编号，从1开始
                yaxis_index=i + 1,
                # 设置曲线颜色
                color=colors[i],
            )
            line_count += 1
        # 全局图像配置
        chart_line = chart_line.set_global_opts(
            # 设置标题
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=math.ceil(f_size * 1.2),
                ),
                pos_left="50%",
                pos_top="1.5%",
                text_align="center",
                text_vertical_align="center",
            ),
            # 设置X轴通用属性
            xaxis_opts=opts.AxisOpts(
                min_=0,
                max_=data.shape[0],
            ),
            # 设置Y轴通用属性
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                boundary_gap="1%",
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            # 图例属性，无边框，距离顶部3%
            legend_opts=opts.LegendOpts(
                border_width=0,
                pos_top="3%",
            ),
            # 鼠标移动到图像上显示任意节点数据
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            # 工具箱属性，允许便捷保存调整图像大小与缩放
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                pos_top="3%",
                # 不允许直接查看元数据以及变化图像类型
                feature=opts.ToolBoxFeatureOpts(
                    data_view=opts.ToolBoxFeatureDataViewOpts(is_show=False),
                    magic_type=opts.ToolBoxFeatureMagicTypeOpts(is_show=False),
                ),
            ),
        )
        # 折线图像添加到绘图网格中
        chart_grid.add(
            chart_line,
            # 左右边距设置
            grid_opts=opts.GridOpts(
                pos_left=math.ceil(line_count / 2) * 50,
                pos_right=math.floor(line_count / 2) * 50,
            ),
            is_control_axis_index=True,
        )
        # 测试使用，会渲染成html文件查看效果
        # chart_grid.render('line_chart.html')
        return chart_grid.dump_options_with_quotes()


if __name__ == "__main__":
    data = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]})
    j = scatter_json(data)
    print(j)
