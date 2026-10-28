// 550-14239-VG failure analysis charts
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
    { m: '1月', v: 0 }, { m: '2月', v: 0 }, { m: '3月', v: -367.88 }, { m: '4月', v: 0 },
    { m: '5月', v: -3.76 }, { m: '6月', v: -1060.05 }, { m: '7月', v: -36.82 }, { m: '8月', v: 56.92 }
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
    { n: '销售额', v: 1847.36 }, { n: '库存补偿等', v: 60.09 },
    { n: '广告花费', v: -1613.97 }, { n: 'FBA 履约费', v: -822.71 },
    { n: '预估费用', v: -393.71 }, { n: '采购成本', v: -170.50 },
    { n: '平台佣金', v: -129.71 }, { n: '头程物流', v: -67.10 },
    { n: '退款', v: -61.55 }, { n: '促销折扣', v: -46.90 }, { n: '仓储费', v: -15.13 }
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
  var camps = ['SP-AUTO 自动', 'SP-KW 关键词', 'SP-ASIN 定向'];
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
        data: [117.88, 64.60, 23.58],
        barWidth: '26%',
        itemStyle: { color: accent, borderRadius: [3, 3, 0, 0] },
        label: { show: true, position: 'top', color: ink, fontSize: 10 }
      },
      {
        name: '广告销售',
        type: 'bar',
        data: [129.92, 46.09, 4.19],
        barWidth: '26%',
        itemStyle: { color: accent2, borderRadius: [3, 3, 0, 0] },
        label: { show: true, position: 'top', color: ink, fontSize: 10 }
      }
    ]
  });
  window.addEventListener('resize', function () { campChart.resize(); });

  // ===== Chart 4: Top 5 products =====
  var topChart = echarts.init(document.getElementById('chart-top-products'), null, { renderer: 'svg' });
  var topData = [
    { n: 'YUNYAKARSA Schulkind 入学袜', v: 4052 },
    { n: 'Dedoles 趣味袜', v: 3390 },
    { n: 'TODO 趣味袜', v: 2870 },
    { n: 'Orifinter 入学袜', v: 2521 },
    { n: 'Orifinter 刺绣入学袜', v: 2041 }
  ];
  topChart.setOption({
    animation: false,
    grid: baseGrid(),
    tooltip: Object.assign(tooltipBase(), {
      formatter: function (p) { return p[0].name + '：<b>' + p[0].value + ' 件/月</b>'; }
    }),
    xAxis: { type: 'value', name: '件/月', nameTextStyle: { color: muted }, axisLabel: axisLabel(), splitLine: { lineStyle: { color: rule, type: 'dashed' } } },
    yAxis: {
      type: 'category',
      data: topData.map(function (d) { return d.n; }),
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false },
      axisLabel: { color: muted, fontSize: 10 }
    },
    series: [{
      type: 'bar',
      data: topData.map(function (d) { return d.v; }),
      barWidth: '55%',
      itemStyle: { color: accent2, borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: 'right', color: ink, fontSize: 10 }
    }]
  });
  window.addEventListener('resize', function () { topChart.resize(); });

  // ===== Chart 5: Keyword search volume =====
  var kwChart = echarts.init(document.getElementById('chart-keywords'), null, { renderer: 'svg' });
  var kwData = [
    { n: 'einschulung junge（入学-男孩）', v: 114757 },
    { n: 'schultüte füllung（入学彩袋填充）', v: 111639 },
    { n: 'socken（袜子）', v: 45883 },
    { n: 'einschulung mädchen geschenk（入学礼物）', v: 35218 },
    { n: 'fußball socken（足球袜）', v: 21569 }
  ];
  kwChart.setOption({
    animation: false,
    grid: Object.assign(baseGrid(), { top: 20 }),
    tooltip: Object.assign(tooltipBase(), {
      formatter: function (p) { return p[0].name + '：<b>' + p[0].value.toLocaleString() + ' 次/月</b>'; }
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
        color: function (p) { return p.dataIndex === 2 ? accent : accent2; }
      },
      label: { show: true, position: 'right', color: ink, fontSize: 10, formatter: function (p) { return p.value.toLocaleString(); } }
    }]
  });
  window.addEventListener('resize', function () { kwChart.resize(); });
})();
