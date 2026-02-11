// ═══════════════════════════════════════════════
//  iRevolution — Shared JS Utilities
// ═══════════════════════════════════════════════

const COLORS = {
  blue:   '#4f8eff', violet:'#8b5cf6', pink:'#ec4899',
  cyan:   '#06b6d4', green: '#10b981', amber:'#f59e0b',
  red:    '#ef4444', muted: '#7878a0'
};

const GRADIENTS = {
  blue:   ['#4f8eff','#8b5cf6'],
  pink:   ['#ec4899','#8b5cf6'],
  cyan:   ['#06b6d4','#4f8eff'],
  green:  ['#10b981','#06b6d4'],
  amber:  ['#f59e0b','#ef4444'],
};

Chart.defaults.color = '#7878a0';
Chart.defaults.font.family = "'DM Sans', sans-serif";
Chart.defaults.font.size = 12;

// Create canvas gradient helper
function makeGrad(ctx, colors, vertical=true) {
  const g = vertical
    ? ctx.createLinearGradient(0, 0, 0, ctx.canvas.height)
    : ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
  g.addColorStop(0, colors[0]);
  g.addColorStop(1, colors[1]);
  return g;
}

// Area fill gradient (top opacity)
function areaGrad(ctx, color) {
  const g = ctx.createLinearGradient(0,0,0,ctx.canvas.height);
  g.addColorStop(0, color+'55');
  g.addColorStop(1, color+'00');
  return g;
}

// Default chart options
const defOpts = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration:800, easing:'easeOutQuart' },
  plugins: {
    legend: { display:false },
    tooltip: {
      backgroundColor:'#1a1a2e',
      borderColor:'rgba(255,255,255,0.08)',
      borderWidth:1,
      padding:12,
      titleFont:{ family:"'Syne',sans-serif", size:13, weight:'700' },
      bodyFont:{ family:"'DM Sans',sans-serif", size:12 },
      callbacks: {}
    }
  }
};

function lineOpts(yLabel='', xLabel='') {
  return {
    ...defOpts,
    scales: {
      x: { grid:{ color:'rgba(255,255,255,0.04)' },
           ticks:{ color:'#7878a0' }, border:{ display:false } },
      y: { grid:{ color:'rgba(255,255,255,0.04)' },
           ticks:{ color:'#7878a0' }, border:{ display:false },
           title:{ display:!!yLabel, text:yLabel, color:'#7878a0' } }
    }
  };
}

function barOpts(horizontal=false) {
  return {
    ...defOpts,
    indexAxis: horizontal ? 'y' : 'x',
    scales: {
      x: { grid:{ color:horizontal?'rgba(255,255,255,0.04)':'transparent' },
           ticks:{ color:'#7878a0' }, border:{ display:false } },
      y: { grid:{ color:horizontal?'transparent':'rgba(255,255,255,0.04)' },
           ticks:{ color:'#7878a0' }, border:{ display:false } }
    }
  };
}

function donutOpts() {
  return {
    ...defOpts,
    cutout:'70%',
    plugins:{
      ...defOpts.plugins,
      legend:{ display:false }
    }
  };
}

// Fetch wrapper
async function api(endpoint) {
  const r = await fetch(endpoint);
  return r.json();
}

// Format helpers
function fmtB(n)  { return '$' + n.toFixed(1) + 'B'; }
function fmtM(n)  { return n.toFixed(1) + 'M'; }
function fmtK(n)  { return n >= 1000 ? (n/1000).toFixed(0)+'K' : n; }
function fmtPct(n){ return n.toFixed(1)+'%'; }
function fmtNum(n){ return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g,','); }

// Animate counters
function animateValue(el, end, prefix='', suffix='', duration=1200) {
  if (!el) return;
  const start = 0, step = 16;
  const increment = end / (duration / step);
  let current = 0;
  const timer = setInterval(() => {
    current += increment;
    if (current >= end) { current = end; clearInterval(timer); }
    el.textContent = prefix + (Number.isInteger(end) ? Math.round(current) : current.toFixed(1)) + suffix;
  }, step);
}

// Fade-in on scroll
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
}, { threshold: 0.08 });

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.fade').forEach(el => observer.observe(el));

  // Active nav link
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (path === '/' && href === '/') ||
        (path !== '/' && href !== '/' && path.startsWith(href))) {
      a.classList.add('active');
    }
  });

  // Live clock
  const clk = document.getElementById('live-clock');
  if (clk) {
    const tick = () => { clk.textContent = new Date().toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit',second:'2-digit'}); };
    tick(); setInterval(tick, 1000);
  }
});
