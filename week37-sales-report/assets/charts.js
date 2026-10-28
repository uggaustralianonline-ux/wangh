/* charts.js — 事业一部 & 事业三部 2026-W37 销售与新周报图表 */
(function () {
  // 读取同一套 Business Blue 图表配色（具体值，供 ECharts 运行时读取）
  var palette = {
    series1: '#0969DA',
    series2: '#8250DF',
    series3: '#06B6D4',
    series4: '#BF3989',
    grid: 'rgba(22,35,59,0.12)',
    axis: '#5C6B85',
    label: '#5C6B85',
    tooltipBg: '#FFFFFF'
  };
  var css = {
    grid: getComputedStyle(document.documentElement).getPropertyValue('--chart-grid').trim()
  };
  if (css.grid) palette.grid = css.grid;

  function fmt(n) {
    return n.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
  }

  function makeBarChart(el, data, opts) {
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

    if (opts && opts.takeaway) {
      // 标题与 takeaway 已在 HTML 中承载
    }

    return chart;
  }

  function mount() {
    var charts = [];
    var dom1 = document.getElementById('chart-yyb-top10');
    var dom2 = document.getElementById('chart-sb');
    var dom3 = document.getElementById('chart-kf');

    if (dom1) {
      charts.push(makeBarChart(dom1, [
        { name: '范昌娟', value: 144235.11 },
        { name: '张淑珍', value: 105759.90 },
        { name: '张颖', value: 102109.17 },
        { name: '吴跃', value: 93433.07 },
        { name: '丁惠敏', value: 88159.62 },
        { name: '袁雪丽', value: 84927.24 },
        { name: '范雅晴', value: 78618.42 },
        { name: '丁道理', value: 58859.25 },
        { name: '秦书月', value: 55757.62 },
        { name: '刘雨晴', value: 55032.72 }
      ]));
    }

    if (dom2) {
      charts.push(makeBarChart(dom2, [
        { name: '董思敏', value: 15829.22 },
        { name: '倪锐', value: 11114.20 },
        { name: '孙莹', value: 7176.42 },
        { name: '鲍远娇', value: 5827.12 },
        { name: '无推广人', value: 1632.39 }
      ]));
    }

    if (dom3) {
      charts.push(makeBarChart(dom3, [
        { name: '车彩霞', value: 98952.57 },
        { name: '徐亮', value: 80951.94 },
        { name: '王婷婷', value: 80137.21 },
        { name: '刘朱', value: 71601.33 },
        { name: '李新雅', value: 65919.95 },
        { name: '黄利园', value: 65694.53 },
        { name: '吴正', value: 52794.14 },
        { name: '钱程', value: 52130.68 },
        { name: '卢文莲', value: 40097.27 },
        { name: '代焰住', value: 22387.32 },
        { name: '贾闪闪', value: 15041.06 }
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