/* B0DTFZRVQN 销量预估报告 — 图表初始化
   全部图表共用 :root 中的 --chart-* 调色板（Business Blue）。 */
(function () {
  'use strict';

  var root = document.documentElement;
  var css = getComputedStyle(root);
  var token = function (name) { return css.getPropertyValue(name).trim(); };

  var chartSeries = [token('--chart-series-1'), token('--chart-series-2'), token('--chart-series-3'), token('--chart-series-4')];
  var chartAccent = token('--chart-accent');
  var chartLabel = token('--chart-label');
  var chartGrid = token('--chart-grid');
  var chartTooltipBg = token('--chart-tooltip-bg');
  var ink = token('--ink');
  var rule = token('--rule');

  var axisText = { color: chartLabel, fontSize: 12 };
  var gridLine = { lineStyle: { color: chartGrid, width: 1 } };

  function tooltipBase() {
    return {
      trigger: 'axis',
      appendToBody: true,
      backgroundColor: chartTooltipBg,
      borderColor: rule,
      textStyle: { color: ink, fontSize: 12 },
      extraCssText: 'border-radius:8px;box-shadow:0 2px 8px rgba(31,35,40,0.12);'
    };
  }

  function baseGrid(extra) {
    return Object.assign({ left: 8, right: 16, top: 24, bottom: 8, containLabel: true }, extra || {});
  }

  function emptyState(container) {
    container.innerHTML = '<p class="chart-empty">暂无可用于绘图的数据。</p>';
  }

  var instances = [];

  function mount(id, option, hasData) {
    var el = document.getElementById(id);
    if (!el) return;
    if (!hasData) { emptyState(el); return; }
    var chart = echarts.init(el, null, { renderer: 'svg' });
    chart.setOption(option);
    instances.push(chart);
  }

  window.addEventListener('resize', function () {
    instances.forEach(function (c) { c.resize(); });
  });

  /* ---------- 图 1：历史销量与三情景预估 ---------- */
  var trendLabels = ['2025-10', '2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10', '2026-11', '2026-12'];
  var trendActual = [263, 79, 54, 32, 19, 101, 215, 279, 315, 294, 301, 622, null, null, null];
  var trendConservative = [null, null, null, null, null, null, null, null, null, null, null, null, 690, 225, 145];
  var trendBaseline = [null, null, null, null, null, null, null, null, null, null, null, null, 800, 270, 180];
  var trendOptimistic = [null, null, null, null, null, null, null, null, null, null, null, null, 960, 320, 220];

  function lineSeries(name, data, color, dashed, width) {
    return {
      name: name,
      type: 'line',
      data: data,
      connectNulls: false,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: { color: color, width: width || 2, type: dashed ? 'dashed' : 'solid' },
      itemStyle: { color: color },
      emphasis: { scale: 1.4, focus: 'series' }
    };
  }

  mount('chart-trend', {
    color: chartSeries,
    tooltip: Object.assign(tooltipBase(), {
      valueFormatter: function (v) { return v == null ? '—' : v + ' 件'; }
    }),
    legend: {
      bottom: 0,
      icon: 'roundRect',
      itemWidth: 14,
      itemHeight: 3,
      textStyle: { color: chartLabel, fontSize: 12 },
      data: ['实际销量', '保守预估', '基准预估', '乐观预估']
    },
    grid: baseGrid({ top: 20, bottom: 44 }),
    xAxis: {
      type: 'category',
      data: trendLabels,
      boundaryGap: false,
      axisLine: { lineStyle: { color: chartGrid } },
      axisTick: { show: false },
      axisLabel: Object.assign({}, axisText, { interval: 1, rotate: 0, formatter: function (v) { return v.replace('20', ''); } })
    },
    yAxis: {
      type: 'value',
      name: '件',
      nameTextStyle: { color: chartLabel, fontSize: 12, padding: [0, 0, 0, -28] },
      splitLine: gridLine,
      axisLabel: axisText
    },
    series: [
      lineSeries('实际销量', trendActual, chartSeries[0], false, 2.5),
      lineSeries('保守预估', trendConservative, chartSeries[1], true, 2),
      lineSeries('基准预估', trendBaseline, chartSeries[2], true, 3),
      lineSeries('乐观预估', trendOptimistic, chartSeries[3], true, 2)
    ]
  }, trendActual.some(function (v) { return v != null; }) || trendBaseline.some(function (v) { return v != null; }));

  /* ---------- 图 2：关键词搜索量季节性（pirate treasure, US） ---------- */
  var seasonMonths = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
  var seasonAvg = [4689, 4874, 6364, 6253, 7366, 7670, 8633, 8650, 9877, 12179, 6088, 6110];

  mount('chart-season', {
    color: chartSeries,
    tooltip: Object.assign(tooltipBase(), {
      trigger: 'item',
      formatter: function (p) { return p.name + '<br/>月均搜索量：<strong>' + p.value.toLocaleString('en-US') + '</strong>'; }
    }),
    grid: baseGrid({ top: 24, bottom: 8 }),
    xAxis: {
      type: 'category',
      data: seasonMonths,
      axisLine: { lineStyle: { color: chartGrid } },
      axisTick: { show: false },
      axisLabel: axisText
    },
    yAxis: {
      type: 'value',
      name: '月均搜索量',
      nameTextStyle: { color: chartLabel, fontSize: 12, padding: [0, 0, 0, -46] },
      splitLine: gridLine,
      axisLabel: Object.assign({}, axisText, {
        formatter: function (v) { return v >= 1000 ? (v / 1000) + 'k' : v; }
      })
    },
    series: [{
      type: 'bar',
      name: '月均搜索量',
      data: seasonAvg.map(function (v, i) {
        return {
          value: v,
          itemStyle: { color: i === 9 ? chartAccent : chartSeries[0], borderRadius: [4, 4, 0, 0] }
        };
      }),
      barMaxWidth: 34,
      label: {
        show: true,
        position: 'top',
        color: chartLabel,
        fontSize: 11,
        formatter: function (p) { return p.value >= 1000 ? (p.value / 1000).toFixed(1) + 'k' : p.value; }
      }
    }]
  }, seasonAvg.some(function (v) { return v != null; }));

  /* ---------- 图 3：三情景需求 vs 可覆盖供给 ---------- */
  var gapScenarios = ['保守情景', '基准情景', '乐观情景'];
  var gapDemand = [1060, 1250, 1500];
  var gapSupply = [934, 934, 934];

  mount('chart-gap', {
    color: chartSeries,
    tooltip: Object.assign(tooltipBase(), {
      valueFormatter: function (v) { return v + ' 件'; }
    }),
    legend: {
      bottom: 0,
      icon: 'roundRect',
      itemWidth: 14,
      itemHeight: 8,
      textStyle: { color: chartLabel, fontSize: 12 },
      data: ['预估需求（10–12 月）', '可覆盖供给（现货 + 已发在途）']
    },
    grid: baseGrid({ top: 24, bottom: 44 }),
    xAxis: {
      type: 'category',
      data: gapScenarios,
      axisLine: { lineStyle: { color: chartGrid } },
      axisTick: { show: false },
      axisLabel: axisText
    },
    yAxis: {
      type: 'value',
      name: '件',
      nameTextStyle: { color: chartLabel, fontSize: 12, padding: [0, 0, 0, -28] },
      splitLine: gridLine,
      axisLabel: axisText
    },
    series: [
      {
        name: '预估需求（10–12 月）',
        type: 'bar',
        data: gapDemand,
        barMaxWidth: 46,
        itemStyle: { color: chartSeries[0], borderRadius: [4, 4, 0, 0] },
        label: { show: true, position: 'top', color: chartLabel, fontSize: 11 }
      },
      {
        name: '可覆盖供给（现货 + 已发在途）',
        type: 'bar',
        data: gapSupply,
        barMaxWidth: 46,
        itemStyle: { color: chartSeries[1], borderRadius: [4, 4, 0, 0] },
        label: { show: true, position: 'top', color: chartLabel, fontSize: 11 }
      }
    ]
  }, gapDemand.length > 0);
})();