// Date display
const el = document.getElementById('currentDate');
if (el) {
  const now = new Date();
  el.textContent = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
}

// Desktop sidebar collapse
const sidebar = document.getElementById('sidebar');
const mainWrapper = document.getElementById('mainWrapper');
const sidebarToggle = document.getElementById('sidebarToggle');

if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => {
    if (window.innerWidth > 768) {
      sidebar.classList.toggle('collapsed');
    } else {
      sidebar.classList.toggle('mobile-open');
    }
  });
}

// Mobile topbar toggle
const topbarToggle = document.getElementById('topbarToggle');
if (topbarToggle && sidebar) {
  topbarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('mobile-open');
  });
}

// Close sidebar on mobile overlay click
document.addEventListener('click', (e) => {
  if (window.innerWidth <= 768 && sidebar && !sidebar.contains(e.target) && e.target !== topbarToggle) {
    sidebar.classList.remove('mobile-open');
  }
});

// Auto dismiss alerts
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(a => {
    a.style.transition = 'opacity 0.5s';
    a.style.opacity = '0';
    setTimeout(() => a.remove(), 500);
  });
}, 4000);

// Animate bar chart
function animateBars() {
  const bars = document.querySelectorAll('.bar-fill[data-height]');
  bars.forEach(bar => {
    bar.style.height = bar.getAttribute('data-height') + '%';
  });
}
window.addEventListener('load', animateBars);

// Animate stat numbers
function animateNumbers() {
  document.querySelectorAll('.stat-value[data-value]').forEach(el => {
    const target = parseFloat(el.getAttribute('data-value'));
    const isFloat = el.getAttribute('data-float') === 'true';
    const prefix = el.getAttribute('data-prefix') || '';
    let start = 0;
    const duration = 900;
    const step = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = target * ease;
      el.textContent = prefix + (isFloat ? current.toFixed(2) : Math.floor(current).toLocaleString());
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });
}
window.addEventListener('load', animateNumbers);
