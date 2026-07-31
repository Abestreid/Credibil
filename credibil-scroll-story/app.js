const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const mobileQuery = window.matchMedia('(max-width: 900px)');
const hasGSAP = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function showToast(message) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove('show'), 3500);
}

function initHeader() {
  const header = $('#header');
  const menuButton = $('.menu-button');
  const mobileMenu = $('#mobile-menu');
  const onScroll = () => header.classList.toggle('scrolled', window.scrollY > 30);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  menuButton.addEventListener('click', () => {
    const expanded = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!expanded));
    mobileMenu.hidden = expanded;
    document.body.classList.toggle('menu-open', !expanded);
  });

  $$('#mobile-menu a').forEach(link => link.addEventListener('click', () => {
    menuButton.setAttribute('aria-expanded', 'false');
    mobileMenu.hidden = true;
    document.body.classList.remove('menu-open');
  }));
}

function runTerminalDemo(query) {
  const terminal = $('#company-terminal');
  const status = $('#terminal-status');
  const queryText = $('#terminal-query');
  const modules = $$('.terminal-module');
  queryText.textContent = query || 'Nordica Trade S.R.L.';
  status.classList.add('active');
  status.lastChild.textContent = 'идёт проверка';
  terminal.classList.remove('scanning');
  void terminal.offsetWidth;
  terminal.classList.add('scanning');
  modules.forEach(m => { m.classList.remove('loaded'); $('em', m).textContent = '-'; });

  modules.forEach((module, index) => {
    setTimeout(() => {
      module.classList.add('loaded');
      $('em', module).textContent = index === 3 ? '2' : '✓';
      if (index === modules.length - 1) {
        status.lastChild.textContent = 'проверка завершена';
        showToast('Демонстрационная проверка завершена. Прокрутите ниже, чтобы раскрыть результат.');
      }
    }, 420 + index * 260);
  });
}

function initSearch() {
  const heroForm = $('#hero-search');
  const heroInput = $('#hero-query');
  const finalForm = $('#final-search-form');
  const finalInput = $('#final-query');

  heroForm.addEventListener('submit', event => {
    event.preventDefault();
    const query = heroInput.value.trim();
    if (!query) { showToast('Введите название компании, IDNO или ФИО.'); heroInput.focus(); return; }
    runTerminalDemo(query);
  });

  $$('.demo-chip').forEach(chip => chip.addEventListener('click', () => {
    heroInput.value = chip.dataset.query;
    runTerminalDemo(chip.dataset.query);
  }));

  finalForm.addEventListener('submit', event => {
    event.preventDefault();
    const query = finalInput.value.trim();
    if (!query) { showToast('Введите название компании или IDNO.'); finalInput.focus(); return; }
    showToast(`Запрос «${query}» принят. Это демонстрационная версия поиска.`);
  });
}

const storySteps = [
  { number: '01', caption: 'Идентификация записи' },
  { number: '02', caption: 'Владельцы и руководство' },
  { number: '03', caption: 'Корпоративные связи' },
  { number: '04', caption: 'Факторы внимания' },
  { number: '05', caption: 'Хронология изменений' },
  { number: '06', caption: 'Формирование отчёта' }
];

function setStoryStep(index) {
  index = Math.max(0, Math.min(storySteps.length - 1, index));
  $$('.story-text').forEach((el, i) => el.classList.toggle('active', i === index));
  $('#story-number').textContent = storySteps[index].number;
  $('#stage-caption').textContent = storySteps[index].caption;
}

function initStory() {
  if (!hasGSAP || reduceMotion || mobileQuery.matches) return;
  const { gsap, ScrollTrigger } = window;
  gsap.registerPlugin(ScrollTrigger);

  const texts = $$('.story-text');
  const pathsOwners = $$('.p-owner1, .p-owner2');
  const pathsLinks = $$('.p-link1, .p-link2, .p-link3, .p-link4');
  const pathsRisks = $$('.p-risk1, .p-risk2');
  const owners = $$('[data-stage="owners"]');
  const links = $$('[data-stage="links"]');
  const risks = $$('[data-stage="risks"]');
  const timeline = $('[data-stage="history"]');
  const report = $('[data-stage="report"]');
  const core = $('.stage-core');

  gsap.set([...pathsOwners, ...pathsLinks, ...pathsRisks], { strokeDasharray: '8 8', opacity: 0 });
  gsap.set([...owners, ...links, ...risks], { opacity: 0, scale: .82 });
  gsap.set([timeline, report], { opacity: 0, scale: .9 });

  const tl = gsap.timeline({
    defaults: { ease: 'none' },
    scrollTrigger: {
      trigger: '.story-pin',
      start: 'top top',
      end: 'bottom bottom',
      scrub: .7,
      invalidateOnRefresh: true,
      onUpdate: self => {
        const step = Math.min(5, Math.floor(self.progress * 6));
        setStoryStep(step);
        gsap.set('#story-progress-bar', { scaleX: Math.max(1/6, self.progress) });
      }
    }
  });

  tl.to('.core-scan', { yPercent: 200, duration: .7 }, 0)
    .fromTo(core, { boxShadow: '0 0 0 rgba(97,210,162,0)' }, { boxShadow: '0 0 70px rgba(97,210,162,.2)', duration: .7 }, 0)
    .to(pathsOwners, { opacity: 1, duration: .35 }, .75)
    .to(owners, { opacity: 1, scale: 1, duration: .45, stagger: .08, ease: 'power2.out' }, .82)
    .to(pathsLinks, { opacity: 1, duration: .4 }, 1.55)
    .to(links, { opacity: 1, scale: 1, duration: .5, stagger: .07, ease: 'back.out(1.3)' }, 1.65)
    .to([...owners, ...links, ...pathsOwners, ...pathsLinks], { opacity: .28, duration: .3 }, 2.38)
    .to(pathsRisks, { opacity: 1, duration: .3 }, 2.45)
    .to(risks, { opacity: 1, scale: 1, duration: .45, stagger: .08, ease: 'power2.out' }, 2.5)
    .to([...risks, ...pathsRisks, core], { opacity: 0, scale: .9, duration: .35 }, 3.32)
    .to(timeline, { opacity: 1, scale: 1, duration: .5, ease: 'power2.out' }, 3.4)
    .to(timeline, { opacity: 0, scale: .92, duration: .35 }, 4.28)
    .to(report, { opacity: 1, scale: 1, duration: .5, ease: 'back.out(1.2)' }, 4.35)
    .to('.pdf-page', { x: -85, rotation: -7, duration: .5 }, 4.4)
    .to('.xlsx-page', { x: 105, rotation: 8, duration: .5 }, 4.4);

  texts.forEach((text, index) => {
    if (index === 0) return;
    gsap.set(text, { opacity: 0, y: 28 });
  });
}

const previewData = {
  registration: `
    <div class="data-row"><span>IDNO</span><b>1000000000000</b></div>
    <div class="data-row"><span>Дата регистрации</span><b>12.04.2018</b></div>
    <div class="data-row"><span>Юридический адрес</span><b>Кишинёв, демонстрационный адрес</b></div>
    <div class="data-row"><span>Форма собственности</span><b>Частная</b></div>
    <div class="data-row"><span>CAEM</span><b>4690 - неспециализированная торговля</b></div>
    <div class="preview-source">Источник и дата актуальности указываются для каждого критичного показателя.</div>`,
  owners: `
    <div class="preview-cards">
      <div class="preview-card"><small>Администратор</small><b>Ана Демо</b><p>Роль подтверждена в регистрационных данных.</p></div>
      <div class="preview-card"><small>Учредитель</small><b>Виктор Пример</b><p>Доля владения: 50%.</p></div>
      <div class="preview-card"><small>Учредитель</small><b>Ана Демо</b><p>Доля владения: 50%.</p></div>
      <div class="preview-card"><small>Связанные роли</small><b>4 организации</b><p>Активные и ликвидированные компании.</p></div>
    </div>`,
  connections: `
    <div class="preview-cards">
      <div class="preview-card"><small>Активная компания</small><b>Alba Logistic S.R.L.</b><p>Ана Демо - директор.</p></div>
      <div class="preview-card"><small>Ликвидированная компания</small><b>Vector Plus S.R.L.</b><p>Виктор Пример - учредитель.</p></div>
      <div class="preview-card"><small>Активная компания</small><b>Nord Agro S.R.L.</b><p>Виктор Пример - учредитель.</p></div>
      <div class="preview-card"><small>Ликвидированная компания</small><b>Delta Market S.R.L.</b><p>Ана Демо - администратор.</p></div>
    </div>
    <div class="preview-source">Связи отображают роль лица, статус организации и доступную долю владения.</div>`,
  events: `
    <div class="data-row"><span>Судебное событие</span><b>Требует внимания</b></div>
    <div class="data-row"><span>Публичные извещения UNEJ</span><b>1 демонстрационная запись</b></div>
    <div class="data-row"><span>Государственные закупки</span><b>Доступные записи MTender</b></div>
    <div class="data-row"><span>Аккредитация MOLDAC</span><b>Связь требует подтверждения</b></div>
    <div class="data-row"><span>Санкционная проверка</span><b>Проверка выполнена</b></div>`,
  sources: `
    <div class="data-row"><span>Регистрационные сведения</span><b>Обновлено 28.07.2026</b></div>
    <div class="data-row"><span>Налоговая информация</span><b>Проверено вручную</b></div>
    <div class="data-row"><span>Судебные сведения</span><b>instante.justice.md</b></div>
    <div class="data-row"><span>Публичные извещения</span><b>unej.md</b></div>
    <div class="data-row"><span>Аккредитации</span><b>MOLDAC</b></div>
    <div class="preview-source">Credibil структурирует доступные сведения и не заменяет юридическое заключение.</div>`
};

function initChecks() {
  const content = $('#preview-content');
  content.innerHTML = previewData.registration;
  $$('.check-tab').forEach(tab => tab.addEventListener('click', () => {
    $$('.check-tab').forEach(item => { item.classList.remove('active'); item.setAttribute('aria-selected','false'); });
    tab.classList.add('active');
    tab.setAttribute('aria-selected','true');
    if (hasGSAP && !reduceMotion) {
      window.gsap.to(content, { opacity: 0, y: 8, duration: .16, onComplete: () => {
        content.innerHTML = previewData[tab.dataset.check];
        window.gsap.fromTo(content, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .28 });
      }});
    } else content.innerHTML = previewData[tab.dataset.check];
  }));
}

const moldovaPolygon = [
  [26.619337,48.220726],[26.857824,48.368211],[27.522537,48.467119],[28.259547,48.155562],[28.670891,48.118149],[29.122698,47.849095],[29.050868,47.510227],[29.415135,47.346645],[29.559674,46.928583],[29.908852,46.674361],[29.83821,46.525326],[30.024659,46.423937],[29.759972,46.349988],[29.170654,46.379262],[29.072107,46.517678],[28.862972,46.437889],[28.933717,46.25883],[28.659987,45.939987],[28.485269,45.596907],[28.233554,45.488283],[28.054443,45.944586],[28.160018,46.371563],[28.12803,46.810476],[27.551166,47.405117],[27.233873,47.826771],[26.924176,48.123264]
];

function pointInPolygon(point, polygon) {
  const [x,y] = point; let inside = false;
  for (let i=0,j=polygon.length-1;i<polygon.length;j=i++) {
    const [xi,yi] = polygon[i], [xj,yj] = polygon[j];
    const intersect = ((yi>y)!==(yj>y)) && (x < (xj-xi)*(y-yi)/(yj-yi)+xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

function initMoldovaMap() {
  const group = $('.map-dots');
  if (!group) return;
  const ns = 'http://www.w3.org/2000/svg';
  const minX = 26.55, maxX = 30.08, minY = 45.42, maxY = 48.52;
  const dots = [];
  for (let y=minY; y<=maxY; y+=.095) {
    for (let x=minX; x<=maxX; x+=.095) {
      if (pointInPolygon([x,y], moldovaPolygon)) {
        const circle = document.createElementNS(ns,'circle');
        const px = 55 + ((x-minX)/(maxX-minX))*365;
        const py = 520 - ((y-minY)/(maxY-minY))*455;
        circle.setAttribute('cx',px.toFixed(1)); circle.setAttribute('cy',py.toFixed(1)); circle.setAttribute('r','2.5');
        group.appendChild(circle); dots.push(circle);
      }
    }
  }
  if (hasGSAP && !reduceMotion) {
    window.gsap.set(dots,{opacity:0,scale:0,transformOrigin:'center'});
    window.gsap.to(dots,{opacity:.9,scale:1,duration:.7,stagger:{each:.002,from:'random'},ease:'power2.out',scrollTrigger:{trigger:'.moldova-section',start:'top 65%'}});
    window.gsap.from('.map-shield',{scale:.5,opacity:0,duration:.8,ease:'back.out(1.5)',transformOrigin:'center',scrollTrigger:{trigger:'.moldova-section',start:'top 55%'}});
    window.gsap.from('.source-beams path',{strokeDashoffset:80,opacity:0,duration:1,stagger:.12,scrollTrigger:{trigger:'.moldova-section',start:'top 45%'}});
  } else dots.forEach(dot => dot.style.opacity = '.9');
}

const audienceData = {
  procurement: {index:'01',title:'Проверка нового поставщика до договора',text:'Убедитесь, что компания активна, изучите владельцев, связи и события, затем сохраните результат проверки.',factors:['Юридический статус','Связанные организации','Судебные и исполнительные события','Мониторинг после начала работы'],cta:'Проверить поставщика'},
  finance: {index:'02',title:'Проверка клиента перед отсрочкой платежа',text:'Сопоставьте статус, финансовые сведения, задолженности и события до согласования коммерческих условий.',factors:['Налоговая информация','Доступные финансовые отчёты','Исполнительные сведения','Фиксация результата в PDF'],cta:'Проверить клиента'},
  legal: {index:'03',title:'Фиксация структуры владения и факторов внимания',text:'Изучите учредителей, руководство, корпоративные связи, судебные сведения и статус санкционной проверки.',factors:['Учредители и доли','Корпоративные роли','Судебные дела','Источники и дата актуальности'],cta:'Начать юридическую проверку'},
  leaders: {index:'04',title:'Быстрая картина перед деловым решением',text:'Получите сводный статус, ключевые связи, важные события и историю изменений без ручного обхода реестров.',factors:['Сводный профиль компании','Критичные связи','Факторы внимания','Постоянный мониторинг'],cta:'Проверить контрагента'}
};

function renderAudience(role) {
  const data = audienceData[role];
  const panel = $('#audience-panel');
  panel.innerHTML = `<div><span class="panel-index">${data.index}</span><h3>${data.title}</h3><p>${data.text}</p></div><ol>${data.factors.map(f=>`<li>${f}</li>`).join('')}</ol><a class="text-link" href="#final-search">${data.cta} <span>↗</span></a>`;
}

function initAudience() {
  $$('.audience-tab').forEach(tab => tab.addEventListener('click', () => {
    $$('.audience-tab').forEach(item => {item.classList.remove('active');item.setAttribute('aria-selected','false');});
    tab.classList.add('active'); tab.setAttribute('aria-selected','true');
    const panel = $('#audience-panel');
    if (hasGSAP && !reduceMotion) {
      window.gsap.to(panel,{opacity:0,y:8,duration:.16,onComplete:()=>{renderAudience(tab.dataset.role);window.gsap.fromTo(panel,{opacity:0,y:12},{opacity:1,y:0,duration:.3});}});
    } else renderAudience(tab.dataset.role);
  }));
}

function initMonitoring() {
  const toggle = $('#monitor-toggle');
  toggle.addEventListener('click', () => {
    const active = toggle.getAttribute('aria-checked') === 'true';
    toggle.setAttribute('aria-checked', String(!active));
    $('b',toggle).textContent = active ? 'Мониторинг выключен' : 'Мониторинг включён';
    showToast(active ? 'Демонстрационный мониторинг выключен.' : 'Демонстрационный мониторинг включён.');
  });
  if (hasGSAP && !reduceMotion) {
    window.gsap.from('.event-card',{x:80,opacity:0,duration:.6,stagger:.16,ease:'power2.out',scrollTrigger:{trigger:'.events-window',start:'top 72%'}});
  }
}

function initLottie() {
  if (!window.lottie || reduceMotion) return;
  const animationData = {
    v:'5.7.4',fr:60,ip:0,op:150,w:220,h:220,nm:'Отчёт',ddd:0,assets:[],layers:[
      {ddd:0,ind:1,ty:4,nm:'Кольцо',sr:1,ks:{o:{a:1,k:[{t:0,s:[0]},{t:22,s:[70]},{t:120,s:[70]},{t:145,s:[0]}]},r:{a:1,k:[{t:0,s:[0]},{t:145,s:[360]}]},p:{a:0,k:[110,110,0]},a:{a:0,k:[0,0,0]},s:{a:1,k:[{t:0,s:[60,60,100]},{t:30,s:[100,100,100]},{t:130,s:[100,100,100]},{t:145,s:[70,70,100]}]}},ao:0,shapes:[{ty:'el',p:{a:0,k:[0,0]},s:{a:0,k:[150,150]},nm:'Эллипс'},{ty:'st',c:{a:0,k:[.38,.82,.64,1]},o:{a:0,k:100},w:{a:0,k:3},lc:2,lj:2},{ty:'tm',s:{a:0,k:5},e:{a:1,k:[{t:0,s:[5]},{t:50,s:[75]},{t:110,s:[100]}]},o:{a:0,k:0},m:1}],ip:0,op:150,st:0,bm:0},
      {ddd:0,ind:2,ty:4,nm:'Галочка',sr:1,ks:{o:{a:1,k:[{t:0,s:[0]},{t:72,s:[0]},{t:82,s:[100]},{t:130,s:[100]},{t:145,s:[0]}]},r:{a:0,k:0},p:{a:0,k:[110,110,0]},a:{a:0,k:[0,0,0]},s:{a:0,k:[100,100,100]}},ao:0,shapes:[{ty:'sh',ks:{a:0,k:{i:[[0,0],[0,0],[0,0]],o:[[0,0],[0,0],[0,0]],v:[[-34,2],[-8,28],[38,-31]],c:false}},nm:'Путь'},{ty:'st',c:{a:0,k:[.38,.82,.64,1]},o:{a:0,k:100},w:{a:0,k:9},lc:2,lj:2},{ty:'tm',s:{a:0,k:0},e:{a:1,k:[{t:72,s:[0]},{t:105,s:[100]}]},o:{a:0,k:0},m:1}],ip:0,op:150,st:0,bm:0}
    ],markers:[]
  };
  window.lottie.loadAnimation({container:$('#report-lottie'),renderer:'svg',loop:true,autoplay:true,animationData});
}

async function initThreeCanvas(canvasId, seed = 1) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || reduceMotion) return;
  try {
    const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.185.1/build/three.module.min.js');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55,1,.1,100);
    camera.position.z = 6;
    const renderer = new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'low-power'});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.5));
    const geometry = new THREE.BufferGeometry();
    const count = 150;
    const positions = new Float32Array(count*3);
    let value = seed;
    const random = () => (value = (value*9301+49297)%233280)/233280;
    for (let i=0;i<count;i++) {
      positions[i*3]=(random()-.5)*9;
      positions[i*3+1]=(random()-.5)*6;
      positions[i*3+2]=(random()-.5)*5;
    }
    geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
    const material = new THREE.PointsMaterial({color:0x2a9c6f,size:.045,transparent:true,opacity:.65});
    const points = new THREE.Points(geometry,material); scene.add(points);
    const lineMaterial = new THREE.LineBasicMaterial({color:0x2a9c6f,transparent:true,opacity:.08});
    const linePositions=[];
    for(let i=0;i<38;i++){const a=Math.floor(random()*count),b=Math.floor(random()*count);linePositions.push(positions[a*3],positions[a*3+1],positions[a*3+2],positions[b*3],positions[b*3+1],positions[b*3+2]);}
    const lineGeo=new THREE.BufferGeometry();lineGeo.setAttribute('position',new THREE.Float32BufferAttribute(linePositions,3));
    const lines=new THREE.LineSegments(lineGeo,lineMaterial);scene.add(lines);
    let visible=true,raf=0;
    const resize=()=>{const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return;renderer.setSize(rect.width,rect.height,false);camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();};
    const render=()=>{if(!visible)return;points.rotation.y+=.0008;points.rotation.x+=.00025;lines.rotation.copy(points.rotation);renderer.render(scene,camera);raf=requestAnimationFrame(render);};
    const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible&&!raf)render();if(!visible&&raf){cancelAnimationFrame(raf);raf=0;}},{threshold:.01});
    observer.observe(canvas); resize(); window.addEventListener('resize',resize,{passive:true});
  } catch (error) {
    canvas.style.display='none';
  }
}

function initGeneralAnimations() {
  if (!hasGSAP || reduceMotion) return;
  const { gsap } = window;
  gsap.from('.hero-copy > *',{y:28,opacity:0,duration:.75,stagger:.08,ease:'power3.out',delay:.15});
  gsap.from('.company-terminal',{scale:.92,opacity:0,y:30,duration:1,ease:'power3.out',delay:.35});
  gsap.from('.section-heading > *',{y:28,opacity:0,duration:.6,stagger:.12,scrollTrigger:{trigger:'.section-heading',start:'top 80%'}});
  gsap.from('.document',{y:50,opacity:0,duration:.8,stagger:.15,ease:'power3.out',scrollTrigger:{trigger:'.report-artifacts',start:'top 75%'}});
}

function init() {
  initHeader();
  initSearch();
  initStory();
  initChecks();
  initMoldovaMap();
  initMonitoring();
  initAudience();
  initLottie();
  initGeneralAnimations();
  initThreeCanvas('hero-canvas',13);
  initThreeCanvas('final-canvas',37);
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',init); else init();
