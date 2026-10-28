/* N-US 店铺近30天广告投放效果归因 - 图表逻辑 */
(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var danger = style.getPropertyValue('--danger').trim();
  var warn = style.getPropertyValue('--warn').trim();

  var tooltipBase = { appendToBody: true, backgroundColor: bg2, borderColor: rule, textStyle: { color: ink } };

  /* 1. 广告类型结构：花费 vs 销售额 vs ACOS */
  var c1 = echarts.init(document.getElementById('chart-type'), null, { renderer: 'svg' });
  c1.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'axis' }, tooltipBase),
    legend: { data: ['广告花费', '广告销售额', 'ACOS'], textStyle: { color: muted }, top: 0 },
    grid: { left: 50, right: 50, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: ['SP', 'SB', 'SD'], axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink }, axisTick: { show: false } },
    yAxis: [
      { type: 'value', name: '金额 ($)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
      { type: 'value', name: 'ACOS (%)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { show: false } }
    ],
    series: [
      { name: '广告花费', type: 'bar', barWidth: 26, data: [18457.37, 860.44, 0], itemStyle: { color: accent, borderRadius: [6,6,0,0] } },
      { name: '广告销售额', type: 'bar', barWidth: 26, data: [51966.49, 2374.82, 0], itemStyle: { color: accent + '44', borderRadius: [6,6,0,0] } },
      { name: 'ACOS', type: 'line', data: [35.52, 36.23, 0], itemStyle: { color: accent2 }, yAxisIndex: 1, symbolSize: 8, lineStyle: { width: 2 } }
    ]
  });
  window.addEventListener('resize', function() { c1.resize(); });

  /* 2. 三类投放预算占比（SKU级） */
  var c2 = echarts.init(document.getElementById('chart-category'), null, { renderer: 'svg' });
  c2.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'item', formatter: '{b}<br/>花费 $<strong>{c}</strong> ({d}%)' }, tooltipBase),
    legend: { type: 'scroll', bottom: 0, textStyle: { color: muted } },
    color: [accent, warn, danger, muted + '99'],
    series: [{
      type: 'pie', radius: ['45%', '70%'], center: ['50%', '45%'],
      label: { formatter: '{b}\n{d}%', color: ink, fontSize: 12, lineHeight: 18 },
      labelLine: { length: 10, length2: 10 },
      data: [
        { name: '高效投放', value: 2191.07 },
        { name: '保本引流', value: 5399.24 },
        { name: '低效烧钱', value: 10637.94 },
        { name: '未归因（非SKU级）', value: 1089.56 }
      ]
    }]
  });
  window.addEventListener('resize', function() { c2.resize(); });

  /* 3. TOP 15 低效活动（横向柱图，按花费） */
  var badNames = [
    '326-N4118-SP-KW','328-N5691-SP-KW','235-N2509-SP-AUTO','328-N5691-SP-AUTO',
    '12-N2612-SP-KW','389-10386-N-SP-KW','168-14477-N-SP-AUTO','79-9110-N-SP-KW',
    '168-N4768 自动广告','168-6484-N-SB-VIDEO','326-N4118  自动','326-N4121  自动',
    '168-10774-N-SP-AUTO','340-N5656-SP-KW-E','125-N2689-SP-AUTO'
  ];
  var badSpends = [841, 564, 531, 520, 413, 315, 273, 239, 208, 198, 310, 611, 331, 371, 78];
  var badAcos  = [24.0, 52.6, 34.5, 72.7, 34.4, 44.7, 42.3, 65.3, 46.7, 42.6, 36.3, 44.7, 44.2, 55.7, 68.0];
  var c3 = echarts.init(document.getElementById('chart-bad'), null, { renderer: 'svg' });
  c3.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'axis', formatter: function(p){ return '<strong>'+p[0].name+'</strong><br/>花费: $'+p[0].value+'<br/>ACOS: '+p[1].value+'%'; } }, tooltipBase),
    grid: { left: 170, right: 60, top: 20, bottom: 24 },
    xAxis: { type: 'value', axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: { type: 'category', data: badNames.slice().reverse(), axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink, fontFamily: 'JetBrainsMono', fontSize: 11, width: 160, overflow: 'truncate' }, axisTick: { show: false } },
    series: [{
      type: 'bar', barWidth: 14,
      data: badSpends.slice().reverse().map(function(v, i){
        var a = badAcos.slice().reverse()[i];
        return { value: v, itemStyle: { color: a >= 50 ? danger : (a >= 35 ? warn : accent2) } };
      }),
      label: { show: true, position: 'right', color: ink, fontFamily: 'JetBrainsMono', fontSize: 11, formatter: '${c}' }
    }]
  });
  window.addEventListener('resize', function() { c3.resize(); });

  /* 4. TOP 15 高效活动 ROAS（横向柱图） */
  var goodNames = [
    '389-13540-N-SP-KW','168-14524-N-SP-KW','168-7213-N-SB-VIDEO','125-N4741-SP-KW-E',
    '168-14844-N-SP-AUTO','168-14844-N-SP-KW','389-10386-N-SP-AUTO','168-14064-N-SP-AUTO',
    '494-15004-N-SP-ASIN','168-14478-N-SP-ASIN','326-8639-N-SP-KW','168-10995-N-SP-AUTO',
    '89-11199-N-SP-KWE','168-11595-N-SP-KW-E','168-9808-N-SP-AUTO'
  ];
  var goodRoas = [10.34, 8.24, 7.62, 5.84, 5.75, 5.67, 5.40, 5.13, 4.93, 4.51, 4.42, 4.30, 4.18, 3.97, 3.78];
  var goodSpends = [4, 6, 6, 2, 19, 1, 41, 38, 33, 116, 276, 229, 165, 144, 241];
  var c4 = echarts.init(document.getElementById('chart-good'), null, { renderer: 'svg' });
  c4.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'axis', formatter: function(p){ return '<strong>'+p[0].name+'</strong><br/>ROAS: '+p[0].value+'<br/>当前花费: $'+p[1].value; } }, tooltipBase),
    grid: { left: 170, right: 60, top: 20, bottom: 24 },
    xAxis: { type: 'value', name: 'ROAS', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: { type: 'category', data: goodNames.slice().reverse(), axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink, fontFamily: 'JetBrainsMono', fontSize: 11, width: 160, overflow: 'truncate' }, axisTick: { show: false } },
    series: [{
      type: 'bar', barWidth: 14,
      data: goodRoas.slice().reverse(),
      itemStyle: { color: accent, borderRadius: [0,6,6,0] },
      label: { show: true, position: 'right', color: ink, fontFamily: 'JetBrainsMono', fontSize: 11, formatter: '{c}x' }
    }]
  });
  window.addEventListener('resize', function() { c4.resize(); });

  /* 5. 预算重分配瀑布图（花费变动） */
  var c5 = echarts.init(document.getElementById('chart-waterfall'), null, { renderer: 'svg' });
  c5.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'axis', formatter: '{b}<br/><strong>${c}</strong>' }, tooltipBase),
    grid: { left: 60, right: 30, top: 30, bottom: 60 },
    xAxis: { type: 'category', data: ['当前总花费', '低效活动削减', '高效活动加投', '优化后总花费'],
      axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink, rotate: 0, fontSize: 12 }, axisTick: { show: false } },
    yAxis: { type: 'value', axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    series: [{
      type: 'bar', barWidth: '40%',
      data: [
        { value: 19317.81, itemStyle: { color: accent }, label: { show: true, position: 'top', color: ink, formatter: '${c}' } },
        { value: -3255.88, itemStyle: { color: danger }, label: { show: true, position: 'bottom', color: danger, formatter: '-${c}' } },
        { value: 3150.26, itemStyle: { color: accent2 }, label: { show: true, position: 'top', color: ink, formatter: '+${c}' } },
        { value: 19212.19, itemStyle: { color: accent }, label: { show: true, position: 'top', color: ink, formatter: '${c}' } }
      ]
    }]
  });
  window.addEventListener('resize', function() { c5.resize(); });

  /* 6. 关键词 TOP 15 散点（ACOS vs 花费，气泡大小=订单） */
  var kwData = [
    ['hot tub scum absorber', 462.24, 57.9, 84],
    ['cat bathing bag (broad)', 311.19, 25.4, 80],
    ['cat bathing bag (exact)', 253.68, 22.8, 73],
    ['flower stencils for painting', 177.57, 52.8, 52],
    ['cat washing bag (phrase)', 118.20, 19.0, 40],
    ['back to school decorations', 89.33, 55.2, 19],
    ['apple stickers (auto)', 86.96, 35.1, 36],
    ['apple stickers (phrase)', 83.63, 28.8, 44],
    ['cat shower bag', 82.75, 16.5, 33],
    ['footprint stickers', 75.82, 66.6, 18],
    ['cat washing bag (exact)', 74.73, 34.3, 14],
    ['bat stickers', 70.29, 25.5, 44],
    ['hawaiian party decorations', 64.37, 43.0, 23],
    ['googly eyes for crafts', 61.97, 61.0, 12],
    ['cat bath bag', 61.36, 20.0, 20]
  ];
  var c6 = echarts.init(document.getElementById('chart-kw'), null, { renderer: 'svg' });
  c6.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'item', formatter: function(p){ return '<strong>'+p.data[0]+'</strong><br/>花费: $'+p.data[1]+'<br/>ACOS: '+p.data[2]+'%<br/>订单: '+p.data[3]; } }, tooltipBase),
    grid: { left: 50, right: 30, top: 30, bottom: 40 },
    xAxis: { type: 'value', name: '广告花费 ($)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: { type: 'value', name: 'ACOS (%)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    series: [{
      type: 'scatter',
      data: kwData.map(function(d){ return { value: [d[1], d[2], d[3]], symbolSize: Math.max(8, Math.sqrt(d[3])*5), itemStyle: { color: d[2] >= 50 ? danger : (d[2] >= 30 ? warn : accent) } }; }),
      label: { show: false }
    }],
    markLine: {
      silent: true,
      lineStyle: { color: rule, type: 'dashed' },
      data: [{ yAxis: 35, label: { formatter: 'ACOS=35%', color: muted } }]
    }
  });
  window.addEventListener('resize', function() { c6.resize(); });

  /* 7. 自然单带动：间接销售占比 TOP 活动 */
  var indirectNames = [
    '328-N5691-SP-KW','12-N2612-SP-KW','328-N5691-SP-AUTO','235-N2509-SP-AUTO',
    '326-N4118  自动','326-N4121  自动','168-N4768 自动广告','168-9602-N-SP-AUTO',
    '326-N4118-SP-KW','326-N4121-SP-KW','DeepBI_cat_washing_bag','cat bathing bag (broad)'
  ];
  var indirectShares = [45.5, 53.3, 41.9, 35.6, 39.7, 29.8, 30.5, 25.7, 27.3, 27.3, 29.9, 30.1];
  var indirectSales = [488, 54.15, 300, 549, 340, 407, 136, 144, 956, 427, 186, 369];
  var c7 = echarts.init(document.getElementById('chart-indirect'), null, { renderer: 'svg' });
  c7.setOption({
    animation: false,
    tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' },
      formatter: function(p){ return '<strong>'+p[0].name+'</strong><br/>间接销售占比: '+p[0].value+'%<br/>间接销售额: $'+p[1].value; } }, tooltipBase),
    legend: { data: ['间接销售占比', '间接销售额'], textStyle: { color: muted }, top: 0 },
    grid: { left: 170, right: 50, top: 40, bottom: 24 },
    xAxis: [
      { type: 'value', name: '占比 (%)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } }, max: 60 },
      { type: 'value', name: '金额 ($)', nameTextStyle: { color: muted }, axisLabel: { color: muted }, splitLine: { show: false } }
    ],
    yAxis: { type: 'category', data: indirectNames.slice().reverse(), axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink, fontFamily: 'JetBrainsMono', fontSize: 11, width: 160, overflow: 'truncate' }, axisTick: { show: false } },
    series: [
      { name: '间接销售占比', type: 'bar', barWidth: 12, data: indirectShares.slice().reverse(),
        itemStyle: { color: accent, borderRadius: [0,6,6,0] },
        label: { show: true, position: 'right', color: ink, fontFamily: 'JetBrainsMono', fontSize: 11, formatter: '{c}%' } },
      { name: '间接销售额', type: 'line', data: indirectSales.slice().reverse(), xAxisIndex: 1,
        itemStyle: { color: accent2 }, symbolSize: 6, lineStyle: { width: 2 } }
    ]
  });
  window.addEventListener('resize', function() { c7.resize(); });
})();