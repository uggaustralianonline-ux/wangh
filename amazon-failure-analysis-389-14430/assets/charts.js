// 389-14430-VG failure analysis charts
(function () {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  function baseGrid(v) {
    return { left: 12, right: 24, top: 30, bottom: 8, containLabel: true };
  }
  function tooltipBase() {
    return { trigger: 'axis', appendToBody: true, backgroundColor: '#fff', borderColor: rule, textStyle: { color: ink } };
  }
  function axisLabel() {
    return { color: muted, fontSize: 11 };
  }

  // ===== Chart 1: Monthly gross profit =====
  var profitMonth = echarts.init(document.getElementById('chart-profit-month'), null, { renderer: 'svg' });
  var pmData = [
    { m: '2026-04', v: -360.00 }, { m: '2026-05', v: 0 }, { m: '2026-06', v: 37.13 },
    { m: '2026-07', v: -318.11 }, { m: '2026-08', v: -63.58 }
  ];
  profitMonth.setOption({
    animation: false,
    grid: baseGrid(),
    tooltip: Object.assign(tooltipBase(), {
      formatter: function (p) {
        return p[0].name + ' 毛利：<b>' + p[0].value.toFixed(2) + ' 元</b>';
      }
    }),
    xAxis: { type: 'category', data: pmData.map(function (d) { return d.m; }), axisLine: { lineStyle: { color: rule } }, axisTick: { show: false }, axisLabel: axisLabel() },
    yAxis: { type: 'value', name: '元', nameTextStyle: { color: muted }, axisLabel: axisLabel(), splitLine: { lineStyle: { color: rule, type: 'dashed' } } },
    series: [{
      type: 'bar',
      data: pmData.map(function (d) { return d.v; }),
      barWidth: '46%',
      label: {
        show: true,
        position: 'top',
        color: ink,
        fontSize: 11,
        formatter: function (p) { return p.value === 0 ? '—' : p.value.toFixed(0); }
      },
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: function (p) { return p.value >= 0 ? accent2 : accent; }
      }
    }]
  });
  window.addEventListener('resize', function () { profitMonth.resize(); });

  // ===== Chart 2: Cost structure =====
  var costChart = echarts.init(document.getElementById('chart-cost-structure'), null, { renderer: 'svg' });
  var costData = [
    { n: '销售额', v: 2216.92 }, { n: '其他调整项', v: 21.69 },
    { n: 'FBA 履约费', v: -936.39 }, { n: '广告花费', v: -791.82 },
    { n: '预估费用', v: -360.00 }, { n: '采购成本', v: -354.78 },
    { n: '头程物流', v: -153.36 }, { n: '平台佣金', v: -131.75 },
    { n: '退款', v: -92.86 }, { n: '仓储费', v: -75.78 }, { n: '促销折扣', v: -46.43 }
  ];
  costChart.setOption({
    animation: false,
    grid: baseGrid(),
    tooltip: Object.assign(tooltipBase(), {
      formatter: function (p) {
        return p[0].name + '：<b>' + p[0].value.toFixed(2) + ' 元</b>';
      }
    }),
    xAxis: { type: 'value', name: '元', nameTextStyle: { color: muted }, axisLabel: axisLabel(), splitLine: { lineStyle: { color: rule, type: 'dashed' } } },
    yAxis: {
      type: 'category',
      data: costData.map(function (d) { return d.n; }),
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false },
      axisLabel: axisLabel()
    },
    series: [{
      type: 'bar',
      data: costData.map(function (d) { return d.v; }),
      barWidth: '60%',
      label: {
        show: true,
        position: 'right',
        color: ink,
        fontSize: 10,
        formatter: function (p) { return p.value.toFixed(0); }
      },
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: function (p) {
          if (p.name === '销售额') return accent2;
          return p.value >= 0 ? accent2 : accent;
        }
      }
    }]
  });
  window.addEventListener('resize', function () { costChart.resize(); });

  // ===== Chart 3: Campaign spend vs sales =====
  var campChart = echarts.init(document.getElementById('chart-campaign'), null, { renderer: 'svg' });
  var camps = ['SP-AUTO 自动', 'SP-KW 关键词', 'SP-KW-P 短语', 'SP-ASIN 定向'];
  campChart.setOption({
    animation: false,
    grid: baseGrid(),
    tooltip: Object.assign(tooltipBase(), { trigger: 'axis' }),
    legend: { data: ['广告花费', '广告销售'], textStyle: { color: muted }, top: 0 },
    xAxis: { type: 'category', data: camps, axisLine: { lineStyle: { color: rule } }, axisTick: { show: false }, axisLabel: axisLabel() },
    yAxis: { type: 'value', name: 'EUR', nameTextStyle: { color: muted }, axisLabel: axisLabel(), splitLine: { lineStyle: { color: rule, type: 'dashed' } } },
    series: [
      {
        name: '广告花费',
        type: 'bar',
        data: [47.59, 37.24, 9.72, 7.40],
        barWidth: '24%',
        itemStyle: { color: accent, borderRadius: [3, 3, 0, 0] },
        label: { show: true, position: 'top', color: ink, fontSize: 10 }
      },
      {
        name: '广告销售',
        type: 'bar',
        data: [158.45, 70.42, 20.12, 0.00],
        barWidth: '24%',
        itemStyle: { color: accent2, borderRadius: [3, 3, 0, 0] },
        label: { show: true, position: 'top', color: ink, fontSize: 10, formatter: function (p) { return p.value === 0 ? '0' : p.value; } }
      }
    ]
  });
  window.addEventListener('resize', function () { campChart.resize(); });

  // ===== Chart 4: Keyword search volume =====
  var kwChart = echarts.init(document.getElementById('chart-keywords'), null, { renderer: 'svg' });
  var kwData = [
    { n: 'einschulung junge（入学-男孩）', v: 114757 },
    { n: 'schultüte füllung（入学彩袋填充）', v: 111639 },
    { n: 'geschenke zur einschulung（入学礼物）', v: 47743 },
    { n: 'socken（袜子）', v: 45883 },
    { n: 'einschulung geschenke（入学礼物）', v: 5772 },
    { n: 'abitur geschenke / abi socken（本产品主题，无数据）', v: 0 }
  ];
  kwChart.setOption({
    animation: false,
    grid: Object.assign(baseGrid(), { top: 20 }),
    tooltip: Object.assign(tooltipBase(), {
      formatter: function (p) {
        return p[0].name + '：<b>' + (p[0].value === 0 ? '非趋势词，无搜索量' : p[0].value.toLocaleString() + ' 次/月') + '</b>';
      }
    }),
    xAxis: { type: 'value', name: '月搜索量', nameTextStyle: { color: muted }, axisLabel: axisLabel(), splitLine: { lineStyle: { color: rule, type: 'dashed' } } },
    yAxis: {
      type: 'category',
      data: kwData.map(function (d) { return d.n; }),
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false },
      axisLabel: { color: muted, fontSize: 10 }
    },
    series: [{
      type: 'bar',
      data: kwData.map(function (d) { return d.v; }),
      barWidth: '52%',
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: function (p) { return p.dataIndex === kwData.length - 1 ? accent : accent2; }
      },
      label: {
        show: true,
        position: 'right',
        color: ink,
        fontSize: 10,
        formatter: function (p) { return p.value === 0 ? '0（无数据）' : p.value.toLocaleString(); }
      }
    }]
  });
  window.addEventListener('resize', function () { kwChart.resize(); });
})();
