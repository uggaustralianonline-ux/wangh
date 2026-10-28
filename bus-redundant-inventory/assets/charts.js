(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var danger = style.getPropertyValue('--danger').trim();

  // --- Chart 1: 冗余SKU 库存金额与月仓储费对比 ---
  var chart1 = echarts.init(document.getElementById('chart-redundant-compare'), null, { renderer: 'svg' });
  chart1.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true
    },
    legend: {
      data: ['库存金额($)', '月仓储费($)'],
      top: 0,
      textStyle: { color: muted, fontSize: 13 }
    },
    grid: { left: '8%', right: '8%', bottom: '15%', top: '15%' },
    xAxis: {
      type: 'category',
      data: ['168-3536\n感恩节易拉扣', '168-9893\n双面胶8x10mm', '168-9897\n双面胶100x25mm'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 12, interval: 0 }
    },
    yAxis: [
      {
        type: 'value',
        name: '库存金额($)',
        nameTextStyle: { color: muted, fontSize: 12 },
        axisLine: { show: false },
        axisLabel: { color: muted, fontSize: 12 },
        splitLine: { lineStyle: { color: rule } }
      },
      {
        type: 'value',
        name: '月仓储费($)',
        nameTextStyle: { color: muted, fontSize: 12 },
        axisLine: { show: false },
        axisLabel: { color: muted, fontSize: 12 },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '库存金额($)',
        type: 'bar',
        data: [4680, 324.8, 475.6],
        itemStyle: { color: accent, borderRadius: [4, 4, 0, 0] },
        barWidth: '30%',
        label: { show: true, position: 'top', color: ink, fontSize: 12, fontWeight: 700 }
      },
      {
        name: '月仓储费($)',
        type: 'bar',
        yAxisIndex: 1,
        data: [30.16, 6.71, 1.67],
        itemStyle: { color: accent2, borderRadius: [4, 4, 0, 0] },
        barWidth: '30%',
        label: { show: true, position: 'top', color: ink, fontSize: 12, fontWeight: 700 }
      }
    ]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // --- Chart 2: 可售天数排名分布 ---
  var chart2 = echarts.init(document.getElementById('chart-days-supply'), null, { renderer: 'svg' });
  chart2.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true,
      formatter: function(params) {
        var p = params[0];
        return p.name + '<br/>可售天数: ' + p.value + ' 天';
      }
    },
    grid: { left: '15%', right: '8%', bottom: '20%', top: '8%' },
    xAxis: {
      type: 'category',
      data: ['排名第1', '排名第2', '排名第3', '排名第4', '排名第5', '排名第21', '排名第22', '排名第23', '排名第24', '排名第41', '排名第42', '排名第43', '排名第44'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 11, rotate: 35, interval: 0 }
    },
    yAxis: {
      type: 'value',
      name: '可售天数',
      nameTextStyle: { color: muted, fontSize: 12 },
      axisLine: { show: false },
      axisLabel: { color: muted, fontSize: 12 },
      splitLine: { lineStyle: { color: rule } }
    },
    series: [{
      type: 'bar',
      data: [
        { value: 17709, itemStyle: { color: danger } },
        { value: 10179, itemStyle: { color: danger } },
        { value: 7769, itemStyle: { color: danger } },
        { value: 6069, itemStyle: { color: danger } },
        { value: 2830, itemStyle: { color: accent2 } },
        { value: 956, itemStyle: { color: accent2 } },
        { value: 943, itemStyle: { color: accent2 } },
        { value: 916, itemStyle: { color: accent2 } },
        { value: 890, itemStyle: { color: accent2 } },
        { value: 500, itemStyle: { color: accent } },
        { value: 490, itemStyle: { color: accent } },
        { value: 470, itemStyle: { color: accent } },
        { value: 458, itemStyle: { color: accent } }
      ],
      barWidth: '60%',
      label: {
        show: true,
        position: 'top',
        color: ink,
        fontSize: 10,
        formatter: function(p) {
          return p.value >= 1000 ? (p.value / 1000).toFixed(1) + 'k' : p.value;
        }
      },
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: danger, type: 'dashed', width: 1.5 },
        data: [{ yAxis: 365, name: '365天阈值' }],
        label: { formatter: '365天', color: danger, fontSize: 11, position: 'insideEndTop' }
      }
    }]
  });
  window.addEventListener('resize', function() { chart2.resize(); });

  // --- Chart 3: 重点SKU库龄分布 ---
  var chart3 = echarts.init(document.getElementById('chart-age-distribution'), null, { renderer: 'svg' });
  chart3.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true
    },
    legend: {
      data: ['0-90天', '91-180天', '181-270天', '271-330天', '331-365天', '365天以上'],
      top: 0,
      textStyle: { color: muted, fontSize: 12 },
      type: 'scroll'
    },
    grid: { left: '8%', right: '5%', bottom: '20%', top: '15%' },
    xAxis: {
      type: 'category',
      data: ['168-3536', '168-5015', '168-9893', '168-9897', '168-9928', '125-12681', '442-9705', '328-14867', '550-14612'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 11, rotate: 30, interval: 0 }
    },
    yAxis: {
      type: 'value',
      name: '库存数量(件)',
      nameTextStyle: { color: muted, fontSize: 12 },
      axisLine: { show: false },
      axisLabel: { color: muted, fontSize: 12 },
      splitLine: { lineStyle: { color: rule } }
    },
    series: [
      {
        name: '0-90天',
        type: 'bar',
        stack: 'age',
        data: [0, 6, 101, 3, 1, 0, 353, 298, 289],
        itemStyle: { color: accent },
        emphasis: { focus: 'series' }
      },
      {
        name: '91-180天',
        type: 'bar',
        stack: 'age',
        data: [1, 0, 1, 102, 1, 0, 0, 0, 0],
        itemStyle: { color: accent + 'cc' },
        emphasis: { focus: 'series' }
      },
      {
        name: '181-270天',
        type: 'bar',
        stack: 'age',
        data: [2, 3, 2, 2, 2, 3, 0, 0, 0],
        itemStyle: { color: accent2 },
        emphasis: { focus: 'series' }
      },
      {
        name: '271-330天',
        type: 'bar',
        stack: 'age',
        data: [183, 108, 127, 55, 106, 15, 0, 0, 0],
        itemStyle: { color: accent2 + 'cc' },
        emphasis: { focus: 'series' }
      },
      {
        name: '331-365天',
        type: 'bar',
        stack: 'age',
        data: [2, 0, 0, 0, 0, 0, 0, 0, 0],
        itemStyle: { color: danger + 'cc' },
        emphasis: { focus: 'series' }
      },
      {
        name: '365天以上',
        type: 'bar',
        stack: 'age',
        data: [0, 0, 0, 0, 0, 0, 0, 0, 0],
        itemStyle: { color: danger },
        emphasis: { focus: 'series' }
      }
    ]
  });
  window.addEventListener('resize', function() { chart3.resize(); });

})();
