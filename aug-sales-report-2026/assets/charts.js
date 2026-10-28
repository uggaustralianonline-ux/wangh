/* charts.js — 事业一部 & 事业三部 2026-08 销售与新品月报图表 */
(function () {
  var palette = {
    series1: '#0969DA',
    grid: getComputedStyle(document.documentElement).getPropertyValue('--chart-grid').trim() || 'rgba(22,35,59,0.12)',
    axis: '#5C6B85',
    label: '#5C6B85',
    tooltipBg: '#FFFFFF'
  };

  function fmt(n) {
    return n.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
  }

  function makeBarChart(el, data) {
    var names = data.map(function (d) { return d.name; });
    var values = data.map(function (d) { return d.value; });

    var chart = echarts.init(el, null, { renderer: 'svg' });
    chart.setOption({
      animation: false,
      grid: { left: 8, right: 64, top: 8, bottom: 4, containLabel: true },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        appendToBody: true,
        backgroundColor: palette.tooltipBg,
        borderColor: palette.grid,
        textStyle: { color: '#16233B', fontSize: 12 },
        formatter: function (params) {
          return '<b>' + params[0].name + '</b><br/>净销售额：' + fmt(params[0].value);
        }
      },
      xAxis: {
        type: 'value',
        axisLabel: { color: palette.label, formatter: function (v) { return v >= 1000 ? (v / 1000) + 'k' : v; } },
        splitLine: { lineStyle: { color: palette.grid } },
        axisLine: { show: false },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'category',
        data: names,
        axisLabel: { color: palette.axis, fontSize: 12 },
        axisLine: { show: false },
        axisTick: { show: false },
        inverse: true
      },
      series: [{
        type: 'bar',
        data: values,
        itemStyle: { color: palette.series1, borderRadius: [0, 4, 4, 0] },
        barWidth: '58%',
        label: {
          show: true,
          position: 'right',
          formatter: function (p) { return fmt(p.value); },
          color: palette.label,
          fontSize: 11
        }
      }]
    }, true);
    return chart;
  }

  function mount() {
    var charts = [];
    var dom1 = document.getElementById('chart-yyb-top10');
    var dom2 = document.getElementById('chart-sb');
    var dom3 = document.getElementById('chart-kf');

    if (dom1) {
      charts.push(makeBarChart(dom1, [
        { name: '范昌娟', value: 437419.66 },
        { name: '吴跃', value: 355064.60 },
        { name: '张淑珍', value: 351701.48 },
        { name: '张颖', value: 337291.33 },
        { name: '丁惠敏', value: 316844.25 },
        { name: '范雅晴', value: 281599.55 },
        { name: '袁雪丽', value: 216678.59 },
        { name: '丁道理', value: 193660.24 },
        { name: '秦书月', value: 185296.76 },
        { name: '刘雨晴', value: 153083.91 }
      ]));
    }

    if (dom2) {
      charts.push(makeBarChart(dom2, [
        { name: '董思敏', value: 44684.16 },
        { name: '倪锐', value: 43210.77 },
        { name: '孙莹', value: 31016.18 },
        { name: '鲍远娇', value: 30967.05 },
        { name: '无推广人', value: 5809.45 }
      ]));
    }

    if (dom3) {
      charts.push(makeBarChart(dom3, [
        { name: '李新雅', value: 8753.31 },
        { name: '吴正', value: 6947.01 },
        { name: '王婷婷', value: 4203.68 },
        { name: '黄利园', value: 4106.73 },
        { name: '车彩霞', value: 3511.70 },
        { name: '徐亮', value: 3040.28 },
        { name: '卢文莲', value: 2067.64 },
        { name: '钱程', value: 2043.49 },
        { name: '刘朱', value: 2006.65 },
        { name: '代焰住', value: 1130.87 },
        { name: '贾闪闪', value: 369.43 }
      ]));
    }

    function resize() { charts.forEach(function (c) { c.resize(); }); }
    if (window.addEventListener) window.addEventListener('resize', resize);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();