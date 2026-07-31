(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const header = document.querySelector('[data-header]');
  const menuToggle = document.querySelector('.menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');

  const setHeader = () => header.classList.toggle('is-scrolled', window.scrollY > 20);
  setHeader();
  window.addEventListener('scroll', setHeader, { passive: true });

  menuToggle?.addEventListener('click', () => {
    const open = menuToggle.getAttribute('aria-expanded') === 'true';
    menuToggle.setAttribute('aria-expanded', String(!open));
    mobileMenu.hidden = open;
    document.body.classList.toggle('menu-open', !open);
  });
  mobileMenu?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    menuToggle.setAttribute('aria-expanded', 'false');
    mobileMenu.hidden = true;
    document.body.classList.remove('menu-open');
  }));

  const input = document.getElementById('company-search');
  const form = document.querySelector('.hero-search');
  const suggestions = document.querySelector('.search-suggestions');
  const toast = document.querySelector('.toast');

  input?.addEventListener('input', () => {
    suggestions.hidden = input.value.trim().length < 2;
  });
  input?.addEventListener('focus', () => {
    if (input.value.trim().length >= 2) suggestions.hidden = false;
  });
  document.addEventListener('click', (event) => {
    if (!form?.contains(event.target)) suggestions.hidden = true;
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') suggestions.hidden = true;
  });
  suggestions?.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', () => {
      input.value = button.dataset.query;
      suggestions.hidden = true;
      input.focus();
    });
  });
  form?.addEventListener('submit', (event) => {
    event.preventDefault();
    const query = input.value.trim();
    if (!query) {
      input.focus();
      form.animate([{ transform: 'translateX(0)' }, { transform: 'translateX(-7px)' }, { transform: 'translateX(7px)' }, { transform: 'translateX(0)' }], { duration: 280 });
      return;
    }
    try { sessionStorage.setItem('credibil_query', query); } catch (_) {}
    toast.hidden = false;
    toast.animate([{ opacity: 0, transform: 'translateY(16px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 320, easing: 'cubic-bezier(.2,.7,.2,1)' });
    setTimeout(() => { toast.hidden = true; }, 5600);
  });

  const tabs = [...document.querySelectorAll('.product-tab')];
  const images = [...document.querySelectorAll('.screen-image')];
  const caption = document.querySelector('.screen-caption');
  const captions = {
    search: ['Поиск компаний и лиц', 'Autocomplete разделяет юридические и физические лица.'],
    company: ['Карточка компании', 'Статус, реквизиты, учредители, администратор и доступные действия.'],
    monitoring: ['Мониторинг изменений', 'Список отслеживаемых компаний и отдельная область уведомлений.']
  };
  tabs.forEach(tab => tab.addEventListener('click', () => {
    const key = tab.dataset.screen;
    tabs.forEach(item => {
      const active = item === tab;
      item.classList.toggle('active', active);
      item.setAttribute('aria-selected', String(active));
    });
    images.forEach(image => image.classList.toggle('active', image.dataset.image === key));
    caption.innerHTML = `<strong>${captions[key][0]}</strong><span>${captions[key][1]}</span>`;
  }));

  if (!reduced && window.gsap && window.ScrollTrigger) {
    gsap.registerPlugin(ScrollTrigger);

    if (window.Lenis) {
      const lenis = new Lenis({ anchors: true, duration: 1.05, smoothWheel: true, wheelMultiplier: .9 });
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(time => lenis.raf(time * 1000));
      gsap.ticker.lagSmoothing(0);
    }

    document.querySelectorAll('[data-split]').forEach(el => {
      const html = el.innerHTML;
      const lines = html.split('<br>');
      el.innerHTML = lines.map(line => `<span class="line"><span class="line-inner">${line}</span></span>`).join('');
      gsap.from(el.querySelectorAll('.line-inner'), {
        yPercent: 110,
        duration: 1.05,
        stagger: .09,
        ease: 'power4.out',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true }
      });
    });

    gsap.utils.toArray('.reveal').forEach((el, index) => {
      if (el.closest('.hero-copy')) return;
      gsap.from(el, {
        y: 42,
        opacity: 0,
        duration: .9,
        ease: 'power3.out',
        delay: Math.min((index % 4) * .03, .12),
        scrollTrigger: { trigger: el, start: 'top 88%', once: true }
      });
    });

    gsap.timeline({ defaults: { ease: 'power4.out' } })
      .from('.hero .eyebrow', { y: 20, opacity: 0, duration: .7 }, .15)
      .from('.hero-title .line-inner', { yPercent: 110, duration: 1, stagger: .1 }, .23)
      .from('.hero-lead', { y: 25, opacity: 0, duration: .75 }, .55)
      .from('.hero-search', { y: 25, opacity: 0, duration: .75 }, .65)
      .from('.hero-meta', { y: 20, opacity: 0, duration: .65 }, .76)
      .from('.hero-mark', { scale: .72, rotate: -8, opacity: 0, duration: 1.15 }, .35)
      .from('.floating-card', { y: 55, opacity: 0, scale: .92, stagger: .12, duration: .9 }, .55);

    gsap.to('.hero-mark', { y: -14, duration: 3.4, repeat: -1, yoyo: true, ease: 'sine.inOut' });
    gsap.to('.orbit-one', { rotate: 360, duration: 34, repeat: -1, ease: 'none' });
    gsap.to('.orbit-two', { rotate: -360, duration: 28, repeat: -1, ease: 'none' });

    const zone = document.querySelector('[data-parallax-zone]');
    if (zone && window.matchMedia('(pointer:fine)').matches) {
      zone.addEventListener('pointermove', e => {
        const r = zone.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5;
        const y = (e.clientY - r.top) / r.height - .5;
        zone.querySelectorAll('[data-depth]').forEach(card => {
          const depth = Number(card.dataset.depth || .5);
          gsap.to(card, { x: x * 28 * depth, y: y * 24 * depth, duration: .6, ease: 'power2.out' });
        });
      });
      zone.addEventListener('pointerleave', () => {
        zone.querySelectorAll('[data-depth]').forEach(card => gsap.to(card, { x: 0, y: 0, duration: .8, ease: 'power3.out' }));
      });
    }

    gsap.fromTo('.timeline-line span', { height: '0%' }, {
      height: '100%', ease: 'none', scrollTrigger: { trigger: '.timeline', start: 'top 75%', end: 'bottom 55%', scrub: true }
    });

    gsap.to('.sheet-back', { y: -18, x: -12, rotate: -13, scrollTrigger: { trigger: '.report-stack', start: 'top 80%', end: 'bottom 45%', scrub: 1 } });
    gsap.to('.sheet-middle', { y: 18, x: 18, rotate: 10, scrollTrigger: { trigger: '.report-stack', start: 'top 80%', end: 'bottom 45%', scrub: 1 } });
    gsap.to('.final-word', { xPercent: -12, ease: 'none', scrollTrigger: { trigger: '.final-cta', start: 'top bottom', end: 'bottom bottom', scrub: 1 } });

    document.querySelectorAll('.network-lines path').forEach((path, i) => {
      const length = path.getTotalLength();
      gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
      gsap.to(path, { strokeDashoffset: 0, duration: 1.4, delay: i * .08, ease: 'power2.out', scrollTrigger: { trigger: '.network-card', start: 'top 72%', once: true } });
    });
  }

  if (window.matchMedia('(pointer:fine)').matches && !reduced) {
    const dot = document.querySelector('.cursor-dot');
    const ring = document.querySelector('.cursor-ring');
    let mx = -100, my = -100, rx = -100, ry = -100;
    window.addEventListener('pointermove', e => { mx = e.clientX; my = e.clientY; dot.style.transform = `translate(${mx}px,${my}px) translate(-50%,-50%)`; });
    const render = () => {
      rx += (mx - rx) * .16; ry += (my - ry) * .16;
      ring.style.transform = `translate(${rx}px,${ry}px) translate(-50%,-50%)`;
      requestAnimationFrame(render);
    };
    render();
    document.querySelectorAll('a,button,input,.network-node,.risk-tile').forEach(el => {
      el.addEventListener('mouseenter', () => ring.classList.add('is-hover'));
      el.addEventListener('mouseleave', () => ring.classList.remove('is-hover'));
    });
  }
})();
