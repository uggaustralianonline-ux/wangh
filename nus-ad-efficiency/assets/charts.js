/* N-US 店铺近30天广告效率诊断 - 图表逻辑 */
(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var danger = style.getPropertyValue('--danger').trim();

  var tooltipBase = { appendToBody: true, backgroundColor: bg2, borderColor: rule, textStyle: { color: ink } };

  /* --- 1. 广告类型结构：花费 vs 销售额 (bar) --- */
  var chartType = echarts.init(document.getElementById('chart-type'), null, { renderer: 'svg' });
  chartType.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'axis' }, tooltipBase),
    legend: { data: ['广告花费', '广告销售额'], textStyle: { color: muted }, top: 0 },
    grid: { left: 50, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: ['SP', 'SB', 'SD'], axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink }, axisTick: { show: false } },
    yAxis: { type: 'value', name: '金额 ($)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    series: [
      { name: '广告花费', type: 'bar', barWidth: 28, data: [18457.37, 860.44, 0], itemStyle: { color: accent, borderRadius: [6,6,0,0] } },
      { name: '广告销售额', type: 'bar', barWidth: 28, data: [51966.49, 2374.82, 0], itemStyle: { color: accent + '55', borderRadius: [6,6,0,0] } }
    ]
  });
  window.addEventListener('resize', function() { chartType.resize(); });

  /* --- 2. 广告类型 ACOS/CTR/CVR (bar, 双 y 轴) --- */
  var chartAcctr = echarts.init(document.getElementById('chart-acctr'), null, { renderer: 'svg' });
  chartAcctr.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'axis' }, tooltipBase),
    legend: { data: ['ACOS', 'CTR', 'CVR'], textStyle: { color: muted }, top: 0 },
    grid: { left: 50, right: 50, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: ['SP', 'SB', 'SD'], axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink }, axisTick: { show: false } },
    yAxis: [
      { type: 'value', name: 'ACOS (%)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
      { type: 'value', name: 'CTR / CVR (%)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { show: false } }
    ],
    series: [
      { name: 'ACOS', type: 'bar', barWidth: 22, data: [35.52, 36.23, 0], itemStyle: { color: accent2 }, yAxisIndex: 0 },
      { name: 'CTR', type: 'line', data: [0.83, 1.16, 0], itemStyle: { color: accent }, yAxisIndex: 1, symbolSize: 8 },
      { name: 'CVR', type: 'line', data: [12.91, 17.59, 0], itemStyle: { color: ink }, yAxisIndex: 1, symbolSize: 8 }
    ]
  });
  window.addEventListener('resize', function() { chartAcctr.resize(); });

  /* --- 3. 假赚钱 SKU：广告费 / 净利比 (横向 bar) --- */
  var fakeSku = [
    ['168-N4768', '42.99'],
    ['168-10774-N', '19.12'],
    ['168-N2649', '17.83'],
    ['652-14754-N', '21.95'],
    ['389-10386-N', '4.08'],
    ['79-9110-N', '3.86'],
    ['326-N4118', '3.59'],
    ['235-N2509', '3.42'],
    ['125-N4741', '3.24'],
    ['12-N2613', '2.36'],
    ['326-N4121', '2.25']
  ];
  var chartFake = echarts.init(document.getElementById('chart-fake'), null, { renderer: 'svg' });
  chartFake.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'axis', formatter: '{b}<br/>广告费/净利 <strong>{c}x</strong>' }, tooltipBase),
    grid: { left: 110, right: 40, top: 10, bottom: 24 },
    xAxis: { type: 'value', name: '广告费 ÷ 净利 (倍)', nameLocation: 'middle', nameGap: 28, nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: { type: 'category', data: fakeSku.map(function(d){return d[0];}), axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink, fontFamily: 'JetBrainsMono' }, axisTick: { show: false } },
    series: [{
      name: '广告费/净利', type: 'bar', barWidth: 16,
      data: fakeSku.map(function(d){ return { value: d[1], itemStyle: { color: Number(d[1]) >= 10 ? danger : accent2 } }; }),
      label: { show: true, position: 'right', color: ink, fontFamily: 'JetBrainsMono', formatter: '{c}x' }
    }],
    markLineDisabled: true,
    graphic: [{ type: 'line', shape: { x1: 0, y1: 0, x2: 0, y2: 0 }, style: { stroke: 'transparent' } }]
  });
  window.addEventListener('resize', function() { chartFake.resize(); });

  /* --- 4. 假赚钱 SKU 广告花费分布 (donut) --- */
  var chartFakeDonut = echarts.init(document.getElementById('chart-fake-donut'), null, { renderer: 'svg' });
  chartFakeDonut.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'item', formatter: '{b}<br/>花费 $<strong>{c}</strong> ({d}%)' }, tooltipBase),
    legend: { type: 'scroll', orient: 'vertical', right: 0, top: 'center', textStyle: { color: muted, fontFamily: 'JetBrainsMono' } },
    color: [accent, accent2, danger, accent + '99', accent2 + '99', '#7a9a6e', '#d69a72', '#5b8370', '#c97f5a', '#8aa884', '#bd6a4a'],
    series: [{
      type: 'pie', radius: ['40%', '68%'], center: ['38%', '50%'],
      label: { show: false }, labelLine: { show: false },
      data: [
        { name: '326-N4118', value: 1391 },
        { name: '326-N4121', value: 1176 },
        { name: '235-N2509', value: 838 },
        { name: '389-10386-N', value: 481 },
        { name: '168-10774-N', value: 331 },
        { name: '79-9110-N', value: 239 },
        { name: '168-N4768', value: 235 },
        { name: '12-N2613', value: 189 },
        { name: '168-N2649', value: 186 },
        { name: '125-N4741', value: 132 },
        { name: '652-14754-N', value: 111 }
      ]
    }]
  });
  window.addEventListener('resize', function() { chartFakeDonut.resize(); });

  /* --- 5. 断货风险 SKU：库存 vs 广告花费 (scatter) --- */
  var stockData = [
    [37, 402, '494-14499-N'], [27, 374, '168-14478-N'], [5, 247, '168-7213-N'],
    [24, 220, '125-7172-N'], [25, 189, '12-N2613'], [14, 135, '389-14650-N'],
    [25, 111, '652-14754-N'], [18, 94, '168-14064-N'], [35, 51, '168-8579-N'],
    [0, 32, '168-9812-N'], [0, 30, '125-N4449M']
  ];
  var chartStock = echarts.init(document.getElementById('chart-stock'), null, { renderer: 'svg' });
  chartStock.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'item', formatter: function(p){ return '<strong>' + p.data[2] + '</strong><br/>库存: ' + p.data[0] + ' 件<br/>广告花费: $' + p.data[1]; } }, tooltipBase),
    grid: { left: 50, right: 30, top: 30, bottom: 40 },
    xAxis: { type: 'value', name: '当前库存 (件)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: { type: 'value', name: '广告花费 ($)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    series: [{
      type: 'scatter', symbolSize: 14,
      data: stockData.map(function(d){ return { value: d, itemStyle: { color: d[0] <= 10 ? danger : (d[0] <= 25 ? accent2 : accent) } }; }),
      label: { show: false }
    }]
  });
  window.addEventListener('resize', function() { chartStock.resize(); });

  /* --- 6. 亏损 SKU：净利 (bar, 正负分色) --- */
  var lossSku = [
    ['89-N3397', -1005], ['328-N5691', -1175], ['168-9806-N', -146],
    ['340-N5656', -125], ['125-6841-N', -113], ['652-14963-N', -97],
    ['168-6484-N', -60], ['12-N2612', -46], ['168-14477-N', -24],
    ['168-N2330', -4], ['125-7100-N', -5], ['168-10997-N', -1]
  ].sort(function(a,b){ return a[1] - b[1]; });
  var chartLoss = echarts.init(document.getElementById('chart-loss'), null, { renderer: 'svg' });
  chartLoss.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'axis', formatter: '{b}<br/>净利 <strong>${c}</strong>' }, tooltipBase),
    grid: { left: 110, right: 40, top: 10, bottom: 24 },
    xAxis: { type: 'value', axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: { type: 'category', data: lossSku.map(function(d){return d[0];}), axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink, fontFamily: 'JetBrainsMono' }, axisTick: { show: false } },
    series: [{
      type: 'bar', barWidth: 16,
      data: lossSku.map(function(d){ return { value: d[1], itemStyle: { color: danger } }; }),
      label: { show: true, position: 'right', color: ink, fontFamily: 'JetBrainsMono', formatter: '${c}' }
    }]
  });
  window.addEventListener('resize', function() { chartLoss.resize(); });
})();