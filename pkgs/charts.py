import math
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType
from pyecharts.charts.composite_charts.grid import Grid
import pandas as pd
from pyecharts.charts.basic_charts.scatter import Scatter


def scatter_json(data: pd.DataFrame, title: str = '', f_size: int = 15):
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
    chart_scatter = Scatter(init_opts=opts.InitOpts(
        # 关闭动画效果
        animation_opts=opts.AnimationOpts(animation=False),
    )).add_xaxis(  # 添加x轴数据
        xaxis_data=x_data).add_yaxis(  # 添加y轴数据
            # 数据系列名称
            series_name='',
            # 具体数据
            y_axis=y_data,
            # 颜色
            color='firebrick',
            # 标记大小
            symbol_size=math.floor(f_size * 0.6),
            # 设置不显示点数值
            label_opts=opts.LabelOpts(is_show=False),
        ).set_global_opts(  # 全局配置项
            # 设置标题
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(font_size=math.ceil(
                    f_size * 1.2), ),
                pos_left='50%',
                pos_top='1.5%',
                text_align='center',
                text_vertical_align='center',
            ),
            # 设置不显示图例
            legend_opts=opts.LegendOpts(is_show=False),
            # x轴上下限设置
            xaxis_opts=opts.AxisOpts(
                name=str(data.columns[0]),
                name_location='center',
                name_gap=math.ceil(f_size * 2),
                # min_=-x_bound,
                # max_=x_bound,
                min_=0,
                max_=10,
            ),
            # y轴上下限设置
            yaxis_opts=opts.AxisOpts(
                name=str(data.columns[1]),
                name_location='center',
                name_gap=math.ceil(f_size * 3),
                # min_=math.floor(y_data.min() * 0.9),
                # max_=math.ceil(y_data.max() * 1.1),
                min_=0,
                max_=10,
            ),
            # 设置鼠标移动到点上时不显示数值
            tooltip_opts=opts.TooltipOpts(is_show=False, ),
        )
    # 测试使用，会渲染成html文件查看效果
    # chart_scatter.render('scatter.html')
    return chart_scatter.dump_options_with_quotes()


def bar_json(
    data: pd.DataFrame,
    title: str = '',
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
    chart_bar = Bar().add_xaxis(data[data.columns[0]].to_list()).add_yaxis(
        str(data.columns[1]), data[data.columns[1]].to_list()).set_global_opts(
            xaxis_opts=opts.AxisOpts(
                name=str(data.columns[0]),
                axislabel_opts=opts.LabelOpts(rotate=-15)),
            yaxis_opts=opts.AxisOpts(name=str(data.columns[1]), ),
            title_opts=opts.TitleOpts(title=title),
        )
    # 测试使用，会渲染成html文件查看效果
    # chart_bar.render('bar.html')
    return chart_bar.dump_options_with_quotes()


if __name__ == '__main__':
    data = pd.DataFrame({'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10]})
    j = scatter_json(data)
    print(j)
