/* 图表配色：Business Blue 预设；ECharts 需具体色值，与 :root 保持一致 */
const CHART = {
  series1: '#0969DA',
  series2: '#8250DF',
  series3: '#06B6D4',
  seriesOther: '#DDE1E8',
  positive: '#52C41A',
  grid: 'rgba(27, 36, 48, 0.12)',
  axis: '#6B7684',
  label: '#6B7684',
  tooltipBg: '#FFFFFF'
};

const TOOLTIP_BASE = {
  appendToBody: true,
  backgroundColor: CHART.tooltipBg,
  borderColor: CHART.grid,
  textStyle: { color: '#1B2430', fontSize: 12 }
};

const fmtUSD = (v) => '$' + Number(v).toLocaleString('en-US');
const fmtK = (v) => '$' + Math.round(v / 1000) + 'k';
const barTooltip = {
  trigger: 'axis',
  axisPointer: { type: 'shadow' },
  formatter: (ps) => ps[0].name + '<br/><strong style="color:#0969DA">' + fmtUSD(ps[0].value) + '</strong>'
};

/* 图 1 · Q4 两部门预估销售额占比 */
const SHARE_DATA = [
  { value: 26371122, name: '事业一部运营部门' },
  { value: 1052316, name: '事业三部' }
];

const shareEl = document.getElementById('chartShare');
if (shareEl) {
  const chartShare = echarts.init(shareEl, null, { renderer: 'svg' });
  chartShare.setOption({
    animation: false,
    tooltip: Object.assign({}, TOOLTIP_BASE, {
      trigger: 'item',
      formatter: (p) => p.name + '<br/><strong style="color:#0969DA">' + fmtUSD(p.value) + '</strong>（' + p.percent + '%）'
    }),
    legend: {
      bottom: 0,
      icon: 'roundRect',
      itemWidth: 12,
      itemHeight: 12,
      textStyle: { color: CHART.label, fontSize: 12 }
    },
    series: [{
      type: 'pie',
      radius: ['46%', '70%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      itemStyle: { borderColor: '#FFFFFF', borderWidth: 2 },
      label: {
        show: true,
        formatter: (p) => p.name + '\n' + fmtUSD(p.value) + '（' + p.percent + '%）',
        color: CHART.label,
        fontSize: 11,
        lineHeight: 16
      },
      labelLine: { length: 12, length2: 12 },
      data: [
        { value: SHARE_DATA[0].value, name: SHARE_DATA[0].name, itemStyle: { color: CHART.series1 } },
        { value: SHARE_DATA[1].value, name: SHARE_DATA[1].name, itemStyle: { color: CHART.series2 } }
      ]
    }]
  });
  window.addEventListener('resize', () => chartShare.resize());
}

/* 图 2 / 图 3 · 两部门月度预估趋势 */
const MONTHS = ['10月', '11月', '12月'];
const UNIT1_MONTHLY = [8454738, 8985241, 8931143];
const UNIT3_MONTHLY = [187172, 282706, 582438];

function renderMonthly(elId, values, color) {
  const el = document.getElementById(elId);
  if (!el) return;
  const chart = echarts.init(el, null, { renderer: 'svg' });
  chart.setOption({
    animation: false,
    grid: { left: 12, right: 16, top: 28, bottom: 8, containLabel: true },
    tooltip: Object.assign({}, TOOLTIP_BASE, barTooltip),
    xAxis: {
      type: 'category',
      data: MONTHS,
      axisLabel: { color: CHART.label, fontSize: 12 },
      axisLine: { lineStyle: { color: CHART.grid } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: CHART.axis, fontSize: 11, formatter: fmtK },
      splitLine: { lineStyle: { color: CHART.grid } }
    },
    series: [{
      type: 'bar',
      data: values.map((v, i) => ({ value: v, name: MONTHS[i] })),
      itemStyle: { color: color, borderRadius: [4, 4, 0, 0] },
      barMaxWidth: 64,
      label: {
        show: true,
        position: 'top',
        color: CHART.label,
        fontSize: 11,
        formatter: (p) => fmtUSD(p.value)
      }
    }]
  });
  window.addEventListener('resize', () => chart.resize());
}

renderMonthly('chartMonthly1', UNIT1_MONTHLY, CHART.series1);
renderMonthly('chartMonthly3', UNIT3_MONTHLY, CHART.series2);

/* 图 4 · 事业一部运营部门 21 名推广人 Q4 累计 */
const KEEPER1_DATA = [
  ['范昌娟', 3260246], ['张淑珍', 2606870], ['丁道理', 2541302], ['范雅晴', 2173959],
  ['吴跃', 2043080], ['陈云艳', 1755032], ['袁雯丽', 1517575], ['AI推广', 1275529],
  ['张颖', 1261719], ['丁惠敏', 1207294], ['秦书月', 1029309], ['胡宏金', 927101],
  ['刘雨晴', 909037], ['李超', 831933], ['吴瑶', 749252], ['徐叶', 748694],
  ['程智刚', 636625], ['于战战', 387077], ['郑思璇', 266072], ['韦燕敏', 183850],
  ['韩咏琪', 59566]
];

/* 图 5 · 事业三部 5 名推广人 Q4 累计 */
const KEEPER3_DATA = [
  ['倪锐', 644094], ['孙莹', 178953], ['鲍远娇', 148295], ['董思敏', 48409],
  ['周礼旺', 32565]
];

function renderKeepers(elId, data, barWidth, fontSize) {
  const el = document.getElementById(elId);
  if (!el) return;
  const chart = echarts.init(el, null, { renderer: 'svg' });
  chart.setOption({
    animation: false,
    grid: { left: 12, right: 56, top: 12, bottom: 8, containLabel: true },
    tooltip: Object.assign({}, TOOLTIP_BASE, {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (ps) => ps[0].name + '<br/><strong style="color:#0969DA">' + fmtUSD(ps[0].value) + '</strong>'
    }),
    xAxis: {
      type: 'value',
      axisLabel: { color: CHART.axis, fontSize: 11, formatter: fmtK },
      splitLine: { lineStyle: { color: CHART.grid }, show: true }
    },
    yAxis: {
      type: 'category',
      inverse: true,
      data: data.map((d) => d[0]),
      axisLabel: { color: CHART.label, fontSize: fontSize },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: data.map((d) => ({ value: d[1], name: d[0] })),
      itemStyle: { color: CHART.series1, borderRadius: [0, 4, 4, 0] },
      barMaxWidth: barWidth,
      label: {
        show: true,
        position: 'right',
        color: CHART.label,
        fontSize: 10,
        formatter: (p) => fmtUSD(p.value)
      }
    }]
  });
  window.addEventListener('resize', () => chart.resize());
}

renderKeepers('chartKeeper1', KEEPER1_DATA, 18, 11);
renderKeepers('chartKeeper3', KEEPER3_DATA, 26, 12);