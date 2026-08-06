(() => {
  const menuButton = document.querySelector('#menuButton');
  const mobileMenu = document.querySelector('#mobileMenu');
  const modal = document.querySelector('#authModal');
  const modalClose = document.querySelector('#modalClose');
  const modalTitle = document.querySelector('#modalTitle');
  const modalLead = modal?.querySelector('p:not(.eyebrow)');
  const copyButton = document.querySelector('#copyIdno');
  const toast = document.querySelector('#toast');
  const sectionLinks = [...document.querySelectorAll('.section-nav a[href^="#"]')];
  const sections = sectionLinks.map((link) => document.querySelector(link.getAttribute('href'))).filter(Boolean);
  let toastTimer;

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove('show'), 2200);
  };

  const closeMenu = () => {
    mobileMenu?.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
  };

  menuButton?.addEventListener('click', () => {
    const open = mobileMenu.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(open));
  });
  mobileMenu?.querySelectorAll('a, button').forEach((item) => item.addEventListener('click', closeMenu));

  const modalCopy = {
    report: {
      title: 'Откройте полный отчёт Credibil',
      lead: 'После регистрации вы вернётесь к FERRUM NORDICA S.R.L., IDNO 1004600034130, и получите доступ к подробным сведениям и экспорту.'
    },
    monitoring: {
      title: 'Добавьте компанию в мониторинг',
      lead: 'Создайте аккаунт, чтобы сохранить FERRUM NORDICA S.R.L. и получать уведомления о доступных изменениях компании.'
    },
    login: {
      title: 'Войдите и продолжите проверку',
      lead: 'После входа Credibil вернёт вас к карточке FERRUM NORDICA S.R.L., IDNO 1004600034130.'
    },
    signup: {
      title: 'Создайте аккаунт Credibil',
      lead: 'Регистрация открывает полный отчёт, связи, историю, экспорт и мониторинг выбранной компании.'
    }
  };

  const openModal = (intent = 'report') => {
    const copy = modalCopy[intent] || modalCopy.report;
    if (modalTitle) modalTitle.textContent = copy.title;
    if (modalLead) modalLead.textContent = copy.lead;
    modal?.classList.add('open');
    document.body.style.overflow = 'hidden';
    window.setTimeout(() => modal?.querySelector('input')?.focus(), 30);
  };

  const closeModal = () => {
    modal?.classList.remove('open');
    document.body.style.overflow = '';
  };

  document.querySelectorAll('[data-modal-open]').forEach((button) => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      openModal(button.dataset.intent || 'report');
    });
  });
  modalClose?.addEventListener('click', closeModal);
  modal?.addEventListener('click', (event) => { if (event.target === modal) closeModal(); });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeModal(); });

  copyButton?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText('1004600034130');
    } catch {
      const input = document.createElement('textarea');
      input.value = '1004600034130';
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      input.remove();
    }
    showToast('IDNO скопирован');
  });

  document.querySelectorAll('[data-prototype-form]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const email = form.querySelector('input[type="email"]');
      if (!email?.checkValidity()) {
        email?.reportValidity();
        return;
      }
      closeModal();
      showToast('Прототип: здесь начинается регистрация с сохранением IDNO');
    });
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      sectionLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${visible.target.id}`));
    }, { rootMargin: '-20% 0px -66% 0px', threshold: [0, .2, .5] });
    sections.forEach((section) => observer.observe(section));
  }
})();

