(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var warn = '#e67e22';
  var danger = '#e74c3c';
  var success = '#27ae60';

  // --- Chart: Cost Structure (Pie) ---
  var chartCost = echarts.init(document.getElementById('chart-cost'), null, { renderer: 'svg' });
  chartCost.setOption({
    animation: false,
    tooltip: { trigger: 'item', appendToBody: true, formatter: '{b}: ${c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: muted, fontSize: 11 } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{d}%', fontSize: 11, color: ink },
      data: [
        { value: 1519.63, name: 'FBA配送费', itemStyle: { color: danger } },
        { value: 660.10, name: '佣金', itemStyle: { color: warn } },
        { value: 542.15, name: '采购成本', itemStyle: { color: accent } },
        { value: 225.41, name: '头程物流', itemStyle: { color: accent2 } },
        { value: 171.81, name: '仓储费', itemStyle: { color: muted } },
        { value: 597.36, name: '毛利', itemStyle: { color: success } }
      ]
    }]
  });

  // --- Chart: Ad Efficiency (Gauge-like bar) ---
  var chartAd = echarts.init(document.getElementById('chart-ad'), null, { renderer: 'svg' });
  chartAd.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    grid: { left: 80, right: 30, top: 30, bottom: 40 },
    xAxis: {
      type: 'category',
      data: ['广告花费', '毛利', '广告销售额'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, formatter: '${value}' },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } }
    },
    series: [{
      type: 'bar',
      barWidth: 40,
      data: [
        { value: 610.14, itemStyle: { color: danger } },
        { value: 597.36, itemStyle: { color: warn } },
        { value: 1987.11, itemStyle: { color: success } }
      ],
      label: { show: true, position: 'top', formatter: '${c}', color: ink, fontSize: 12, fontWeight: 'bold' }
    }]
  });

  // --- Chart: Radar (5-dimension health) ---
  var chartRadar = echarts.init(document.getElementById('chart-radar'), null, { renderer: 'svg' });
  chartRadar.setOption({
    animation: false,
    tooltip: { appendToBody: true },
    radar: {
      indicator: [
        { name: '利润', max: 100 },
        { name: '广告', max: 100 },
        { name: '库存', max: 100 },
        { name: '退款', max: 100 },
        { name: '经营', max: 100 }
      ],
      shape: 'circle',
      splitNumber: 4,
      axisName: { color: ink, fontSize: 13, fontWeight: 'bold' },
      splitLine: { lineStyle: { color: rule } },
      splitArea: { show: true, areaStyle: { color: ['rgba(255,255,255,0)', 'rgba(0,0,0,0.02)'] } },
      axisLine: { lineStyle: { color: rule } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [30, 20, 75, 70, 45],
        name: '健康度评分',
        areaStyle: { color: 'rgba(231, 76, 60, 0.15)' },
        lineStyle: { color: danger, width: 2 },
        itemStyle: { color: danger },
        symbol: 'circle',
        symbolSize: 6
      }]
    }]
  });

  // --- Chart: Order vs Refund (bar) ---
  var chartRefund = echarts.init(document.getElementById('chart-refund'), null, { renderer: 'svg' });
  chartRefund.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    grid: { left: 50, right: 30, top: 30, bottom: 40 },
    xAxis: {
      type: 'category',
      data: ['总销量', '退货', '退款', '换货'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } }
    },
    series: [{
      type: 'bar',
      barWidth: 36,
      data: [
        { value: 456, itemStyle: { color: accent } },
        { value: 14, itemStyle: { color: warn } },
        { value: 10, itemStyle: { color: danger } },
        { value: 1, itemStyle: { color: muted } }
      ],
      label: { show: true, position: 'top', formatter: '{c}件', color: ink, fontSize: 11 }
    }]
  });

  window.addEventListener('resize', function() {
    chartCost.resize();
    chartAd.resize();
    chartRadar.resize();
    chartRefund.resize();
  });
})();
