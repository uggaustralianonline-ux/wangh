(function () {
  var D = window.REPORT_DATA || {};
  var C = window.REPORT_CHARTS || {};
  var S = D.summary || {};
  var R = S.rate || 6.69;

  function n0(v) { return (v || 0).toLocaleString('en-US', { maximumFractionDigits: 0 }); }
  function n2(v) { return (v || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function n4(v) { return (v || 0).toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 }); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* ---------- charts ---------- */
  if (window.echarts) {
    var axis = { axisLine: { lineStyle: { color: '#DDE1E8' } }, axisLabel: { color: '#6B7684', fontSize: 11 }, splitLine: { lineStyle: { color: 'rgba(27,36,48,.08)' } } };
    var tip = { backgroundColor: '#FFFFFF', borderColor: '#DDE1E8', textStyle: { color: '#1B2430', fontSize: 12 } };
    var insts = [];
    function mount(id, opt) {
      var el = document.getElementById(id);
      if (!el) return;
      var ch = echarts.init(el);
      ch.setOption(opt);
      insts.push(ch);
    }

    // 1. keeper ranking (horizontal, top first)
    var kp = (C.keepers || []).slice().sort(function (a, b) { return a[1] - b[1]; });
    mount('c1', {
      grid: { left: 8, right: 90, top: 16, bottom: 8, containLabel: true },
      tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function (p) { return p[0].name + '<br/>销售额：$' + n2(p[0].value); } }, tip),
      xAxis: Object.assign({ type: 'value', axisLabel: { color: '#6B7684', fontSize: 11, formatter: function (v) { return '$' + (v / 1000) + 'k'; } } }, { splitLine: axis.splitLine }),
      yAxis: Object.assign({ type: 'category', data: kp.map(function (x) { return x[0]; }) }, { axisLabel: { color: '#3A4653', fontSize: 12 } }, { axisLine: axis.axisLine }),
      series: [{
        type: 'bar', data: kp.map(function (x) { return x[1]; }), barWidth: '62%',
        itemStyle: { color: '#0969DA', borderRadius: [0, 3, 3, 0] },
        label: { show: true, position: 'right', color: '#3A4653', fontSize: 11, formatter: function (p) { return '$' + n0(p.value); } }
      }]
    });

    // 2. scatter qty x unit price x amount
    var sc = (C.scatter || []).map(function (x) { return { value: [x[0], x[1], x[2]], name: x[3] }; });
    var maxUsd = Math.max.apply(null, sc.map(function (x) { return x.value[2]; }));
    mount('c2', {
      grid: { left: 8, right: 24, top: 24, bottom: 8, containLabel: true },
      tooltip: Object.assign({
        formatter: function (p) {
          return '<b>' + esc(p.data.name) + '</b><br/>预估销量：' + n0(p.value[0]) + ' 件<br/>客单价：$' + n2(p.value[1]) + '<br/>销售额：$' + n2(p.value[2]);
        }
      }, tip),
      xAxis: Object.assign({ type: 'value', name: '预估销量(件)', nameLocation: 'middle', nameGap: 30, nameTextStyle: { color: '#6B7684', fontSize: 11 }, axisLabel: { color: '#6B7684', fontSize: 11, formatter: function (v) { return v / 1000 + 'k'; } } }, { splitLine: axis.splitLine }),
      yAxis: Object.assign({ type: 'value', name: '客单价($)', nameTextStyle: { color: '#6B7684', fontSize: 11 }, scale: true, axisLabel: { color: '#6B7684', fontSize: 11, formatter: '${value}' } }, { splitLine: axis.splitLine }),
      series: [{
        type: 'scatter',
        data: sc,
        symbolSize: function (v) { return 12 + 30 * Math.sqrt(v[2] / maxUsd); },
        itemStyle: { color: 'rgba(9,105,218,.55)', borderColor: '#0969DA', borderWidth: 1 },
        label: { show: true, position: 'top', fontSize: 11, color: '#3A4653', formatter: function (p) { return p.data.name; } },
        labelLayout: { hideOverlap: true }
      }]
    });

    // 3. top15 shops
    var sp = (C.shops || []).slice().sort(function (a, b) { return a[1] - b[1]; });
    mount('c3', {
      grid: { left: 8, right: 90, top: 16, bottom: 8, containLabel: true },
      tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function (p) { return p[0].name + '<br/>销售额：$' + n2(p[0].value); } }, tip),
      xAxis: Object.assign({ type: 'value', axisLabel: { color: '#6B7684', fontSize: 11, formatter: function (v) { return '$' + (v / 1000) + 'k'; } } }, { splitLine: axis.splitLine }),
      yAxis: Object.assign({ type: 'category', data: sp.map(function (x) { return x[0]; }) }, { axisLabel: { color: '#3A4653', fontSize: 12 } }, { axisLine: axis.axisLine }),
      series: [{
        type: 'bar', data: sp.map(function (x) { return x[1]; }), barWidth: '58%',
        itemStyle: { color: '#8250DF', borderRadius: [0, 3, 3, 0] },
        label: { show: true, position: 'right', color: '#3A4653', fontSize: 11, formatter: function (p) { return '$' + n0(p.value); } }
      }]
    });

    // 4. site share
    var st = (C.sites || []).filter(function (x) { return x[1] > 0; });
    var pal = ['#0969DA', '#8250DF', '#06B6D4', '#BF3989', '#FAAD14', '#52C41A', '#FF7A45', '#6B7684'];
    mount('c4', {
      tooltip: Object.assign({ formatter: function (p) { return p.name + '<br/>$' + n2(p.value) + '（' + p.percent + '%）'; } }, tip),
      legend: { bottom: 0, textStyle: { color: '#3A4653', fontSize: 11 }, itemWidth: 10, itemHeight: 10 },
      series: [{
        type: 'pie', radius: ['42%', '68%'], center: ['50%', '44%'],
        data: st.map(function (x) { return { name: x[0], value: x[1] }; }),
        itemStyle: { borderColor: '#fff', borderWidth: 2 },
        label: { formatter: '{b} {d}%', color: '#3A4653', fontSize: 11 },
        color: pal
      }]
    });

    window.addEventListener('resize', function () { insts.forEach(function (c) { c.resize(); }); });
  }

  /* ---------- detail explorer ---------- */
  var groups = document.getElementById('groups');
  if (!groups || !D.detail) return;

  var byKeeper = {};
  (D.detail || []).forEach(function (r) {
    if (!byKeeper[r.k]) byKeeper[r.k] = [];
    byKeeper[r.k].push(r);
  });
  var order = (D.keepers || []).map(function (x) { return x.name; }).filter(function (n) { return byKeeper[n]; });
  var meta = {};
  (D.keepers || []).forEach(function (x) { meta[x.name] = x; });

  var HEAD = '<table><thead><tr><th>MSKU</th><th>店铺</th><th>ASIN</th><th>产品编号</th><th>产品名称</th><th>开发人</th><th class="num">售价(本币)</th><th class="num">预估销量</th><th class="num">销售额($)</th><th class="num">客单价($)</th></tr></thead><tbody>';
  var rendered = {};

  function rowsHtml(name, filter) {
    var rows = byKeeper[name];
    var out = [];
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      if (filter && filter.length) {
        var hay = (r.m + ' ' + r.s + ' ' + r.a + ' ' + r.p + ' ' + r.n + ' ' + r.d + ' ' + name).toLowerCase();
        var ok = filter.every(function (t) { return hay.indexOf(t) >= 0; });
        if (!ok) continue;
      }
      out.push('<tr><td>' + esc(r.m) + '</td><td>' + esc(r.s) + '</td><td>' + esc(r.a) + '</td><td>' + esc(r.p) + '</td><td class="pn">' + esc(r.n) + '</td><td>' + esc(r.d) + '</td><td class="num">' + n4(r.pr) + '</td><td class="num">' + n0(r.q) + '</td><td class="num">' + n2(r.c / R) + '</td><td class="num">' + (r.q ? n2(r.c / r.q / R) : '—') + '</td></tr>');
    }
    return out.join('');
  }

  var html = order.map(function (name) {
    var m = meta[name] || {};
    return '<details class="kg" data-k="' + esc(name) + '">' +
      '<summary><span>' + esc(name) + '</span><span class="m">' + n0(m.qty) + ' 件 · $' + n2(m.usd) + ' · ' + n0(byKeeper[name].length) + ' 条 MSKU</span></summary>' +
      '<div class="body"></div></details>';
  }).join('');
  groups.innerHTML = html;

  var boxes = Array.prototype.slice.call(groups.querySelectorAll('details.kg'));
  function fill(box) {
    var name = box.getAttribute('data-k');
    var f = box.__filter || [];
    if (box.__rendered === (f.join('|'))) return;
    box.querySelector('.body').innerHTML = HEAD + rowsHtml(name, f) + '</tbody></table>';
    box.__rendered = f.join('|');
  }

  boxes.forEach(function (box) {
    box.addEventListener('toggle', function () { if (box.open) fill(box); });
  });

  var input = document.getElementById('q');
  var stat = document.getElementById('stat');
  function apply() {
    var q = (input.value || '').trim().toLowerCase();
    var terms = q ? q.split(/\s+/).filter(Boolean) : [];
    var total = 0;
    boxes.forEach(function (box) {
      var name = box.getAttribute('data-k');
      var cnt = 0;
      if (terms.length) {
        var rows = byKeeper[name];
        for (var i = 0; i < rows.length; i++) {
          var r = rows[i];
          var hay = (r.m + ' ' + r.s + ' ' + r.a + ' ' + r.p + ' ' + r.n + ' ' + r.d + ' ' + name).toLowerCase();
          if (terms.every(function (t) { return hay.indexOf(t) >= 0; })) cnt++;
        }
      } else {
        cnt = byKeeper[name].length;
      }
      total += cnt;
      box.style.display = cnt ? '' : 'none';
      box.__filter = terms;
      box.__rendered = null;
      if (terms.length && cnt) { box.open = true; fill(box); }
      else if (terms.length) { box.open = false; }
    });
    if (stat) stat.textContent = terms.length
      ? '命中 ' + n0(total) + ' 条 / 共 ' + n0(S.rows) + ' 条'
      : '共 ' + n0(S.rows) + ' 条，按推广人分组';
  }
  if (input) input.addEventListener('input', apply);
  var eb = document.getElementById('expand');
  var cb = document.getElementById('collapse');
  if (eb) eb.addEventListener('click', function () { boxes.forEach(function (b) { if (b.style.display !== 'none') { b.open = true; fill(b); } }); });
  if (cb) cb.addEventListener('click', function () { boxes.forEach(function (b) { b.open = false; }); });
  apply();
})();