(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  var months2025 = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
  var totalScore = [41453, 32526, 27508, 17743, 35340, 47572, 55428, 65153, 60730, 86306, 334508, 361822];
  var nfScore = [37500, 29000, 24700, 16300, 31800, 43800, 48800, 59347, 51274, 80300, 294000, 307000];
  var adScore = [3953, 3526, 2808, 1443, 3540, 3772, 6628, 5806, 9456, 6006, 40508, 54822];

  var chart1 = echarts.init(document.getElementById('chart-traffic-trend'), null, { renderer: 'svg' });
  chart1.setOption({
    title: { text: '2025年全年月度流量趋势', left: 'center', textStyle: { color: ink, fontSize: 15, fontWeight: 600 } },
    tooltip: { trigger: 'axis', appendToBody: true, backgroundColor: bg2, borderColor: rule, textStyle: { color: ink } },
    legend: { data: ['自然流量','广告流量','总流量'], bottom: 0, textStyle: { color: muted } },
    grid: { left: 50, right: 30, top: 60, bottom: 50 },
    xAxis: { type: 'category', data: months2025, axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted } },
    yAxis: { type: 'value', name: '流量分', nameTextStyle: { color: muted }, axisLine: { show: false }, splitLine: { lineStyle: { color: rule } }, axisLabel: { color: muted } },
    series: [
      { name: '自然流量', type: 'line', data: nfScore, smooth: true, itemStyle: { color: accent }, lineStyle: { width: 2 }, areaStyle: { color: accent + '15' } },
      { name: '广告流量', type: 'line', data: adScore, smooth: true, itemStyle: { color: accent2 }, lineStyle: { width: 2 } },
      { name: '总流量', type: 'line', data: totalScore, smooth: true, itemStyle: { color: muted }, lineStyle: { width: 1, type: 'dashed' } }
    ],
    animation: false
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  var chart2 = echarts.init(document.getElementById('chart-yoy-compare'), null, { renderer: 'svg' });
  chart2.setOption({
    title: { text: '2025 vs 2026 · 8~9月流量结构对比', left: 'center', textStyle: { color: ink, fontSize: 15, fontWeight: 600 } },
    tooltip: { trigger: 'axis', appendToBody: true, backgroundColor: bg2, borderColor: rule, textStyle: { color: ink }, formatter: function(p) { var s = p[0].name + '<br/>'; p.forEach(function(d) { s += d.marker + d.seriesName + ': ' + d.value + ' 分<br/>'; }); return s; } },
    legend: { data: ['自然流量','广告流量'], bottom: 0, textStyle: { color: muted } },
    grid: { left: 60, right: 30, top: 60, bottom: 50 },
    xAxis: { type: 'category', data: ['2025-08','2025-09','2026-08','2026-09*'], axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted } },
    yAxis: { type: 'value', name: '流量分', nameTextStyle: { color: muted }, axisLine: { show: false }, splitLine: { lineStyle: { color: rule } }, axisLabel: { color: muted } },
    series: [
      { name: '自然流量', type: 'bar', data: [59347, 51274, 57337, 3773], itemStyle: { color: accent }, barWidth: '35%' },
      { name: '广告流量', type: 'bar', data: [5806, 9456, 3825, 153], itemStyle: { color: accent2 }, barWidth: '35%' }
    ],
    animation: false
  });
  window.addEventListener('resize', function() { chart2.resize(); });

  var chart3 = echarts.init(document.getElementById('chart-search-volume'), null, { renderer: 'svg' });
  chart3.setOption({
    title: { text: 'homecoming mum supplies · 6年搜索量趋势', left: 'center', textStyle: { color: ink, fontSize: 15, fontWeight: 600 } },
    tooltip: { trigger: 'axis', appendToBody: true, backgroundColor: bg2, borderColor: rule, textStyle: { color: ink } },
    legend: { data: ['8月搜索量','9月搜索量'], bottom: 0, textStyle: { color: muted } },
    grid: { left: 60, right: 30, top: 60, bottom: 50 },
    xAxis: { type: 'category', data: ['2020','2021','2022','2023','2024','2025','2026'], axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted } },
    yAxis: { type: 'value', name: '搜索量', nameTextStyle: { color: muted }, axisLine: { show: false }, splitLine: { lineStyle: { color: rule } }, axisLabel: { color: muted } },
    series: [
      { name: '8月搜索量', type: 'bar', data: [3968, 22810, 44777, 36131, 36459, 39232, 36974], itemStyle: { color: accent }, barWidth: '30%' },
      { name: '9月搜索量', type: 'bar', data: [21378, 59377, 84699, 59358, 73414, 70626, null], itemStyle: { color: accent2 }, barWidth: '30%' }
    ],
    animation: false
  });
  window.addEventListener('resize', function() { chart3.resize(); });

  var chart4 = echarts.init(document.getElementById('chart-keyword-share'), null, { renderer: 'svg' });
  chart4.setOption({
    title: { text: '2025-08 核心关键词流量份额', left: 'center', textStyle: { color: ink, fontSize: 15, fontWeight: 600 } },
    tooltip: { trigger: 'axis', appendToBody: true, backgroundColor: bg2, borderColor: rule, textStyle: { color: ink }, formatter: function(p) { return p[0].name + ': ' + p[0].value + '%'; } },
    grid: { left: 150, right: 40, top: 40, bottom: 20 },
    xAxis: { type: 'value', max: 25, axisLine: { show: false }, splitLine: { lineStyle: { color: rule } }, axisLabel: { color: muted, formatter: '{value}%' } },
    yAxis: { type: 'category', data: ['mum supplies homecoming','mum supplies','christmas bells','jingle bells for crafting','homecoming mum supplies','bells for crafts','jingle bells','bells'], axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink } },
    series: [{
      type: 'bar',
      data: [1.88, 2.73, 6.33, 8.34, 9.23, 15.6, 19.26, 22.77],
      itemStyle: { color: function(p) { return p.dataIndex === 4 ? accent2 : accent; } },
      label: { show: true, position: 'right', formatter: '{c}%', color: ink, fontSize: 12 }
    }],
    animation: false
  });
  window.addEventListener('resize', function() { chart4.resize(); });

  var chart5 = echarts.init(document.getElementById('chart-ad-ratio'), null, { renderer: 'svg' });
  chart5.setOption({
    title: { text: '广告占总流量比 · 6个月趋势', left: 'center', textStyle: { color: ink, fontSize: 15, fontWeight: 600 } },
    tooltip: { trigger: 'axis', appendToBody: true, backgroundColor: bg2, borderColor: rule, textStyle: { color: ink }, formatter: '{b}<br/>{c}%' },
    grid: { left: 50, right: 30, top: 50, bottom: 30 },
    xAxis: { type: 'category', data: ['4月','5月','6月','7月','8月','9月'], axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted } },
    yAxis: { type: 'value', max: 20, axisLine: { show: false }, splitLine: { lineStyle: { color: rule } }, axisLabel: { color: muted, formatter: '{value}%' } },
    series: [{
      type: 'line',
      data: [21.8, 15.8, 6.0, 5.5, 6.3, 3.9],
      smooth: true,
      itemStyle: { color: accent2 },
      lineStyle: { width: 3 },
      areaStyle: { color: accent2 + '20' },
      label: { show: true, position: 'top', formatter: '{c}%', color: ink, fontSize: 11 }
    }],
    animation: false
  });
  window.addEventListener('resize', function() { chart5.resize(); });
})();
