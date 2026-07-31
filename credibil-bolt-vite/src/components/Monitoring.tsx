import { Radar, Eye, Bell, ArrowRight } from 'lucide-react';
import { Reveal } from './Reveal';

const CHANGES = [
  { date: '15.01.2024', event: 'Изменение состава администраторов', type: 'structure' },
  { date: '02.10.2023', event: 'Изменение юридического адреса', type: 'address' },
  { date: '18.06.2023', event: 'Увеличение уставного капитала', type: 'capital' },
  { date: '04.03.2023', event: 'Новое судебное дело', type: 'litigation' },
];

export function Monitoring() {
  return (
    <section id="monitoring" className="relative bg-navy py-24 sm:py-32 overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-40" aria-hidden="true" />
      <div
        className="absolute top-0 left-0 right-0 h-px"
        aria-hidden="true"
        style={{ background: 'linear-gradient(to right, transparent, rgba(42, 156, 111, 0.4), transparent)' }}
      />

      <div className="relative mx-auto max-w-6xl px-5 sm:px-8">
        <Reveal>
          <div className="max-w-2xl mb-16">
            <span className="text-green text-sm font-semibold tracking-widest uppercase">Мониторинг</span>
            <h2 className="mt-4 text-3xl sm:text-4xl lg:text-5xl font-bold text-white tracking-tight text-balance">
              Разовая проверка показывает сейчас. Мониторинг контролирует дальше.
            </h2>
            <p className="mt-5 text-white/50 text-lg leading-relaxed text-pretty">
              Добавьте компанию в мониторинг и отслеживайте последующие изменения. Вы узнаёете о новых событиях, изменениях в составе владельцев, судебных делах и других факторах риска.
            </p>
          </div>
        </Reveal>

        {/* Contrast cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-16">
          {/* One-time check */}
          <Reveal>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-8 h-full">
              <div className="flex items-center gap-3 mb-6">
                <span className="flex items-center justify-center h-12 w-12 rounded-2xl bg-white/10">
                  <Eye size={24} className="text-white/70" aria-hidden="true" />
                </span>
                <h3 className="text-xl font-bold text-white">Разовая проверка</h3>
              </div>
              <p className="text-white/50 leading-relaxed">
                Показывает состояние компании в момент запроса. Вы видите текущие сведения, владельцев, связи и события — но картина статична.
              </p>
              <div className="mt-6 pt-6 border-t border-white/10">
                <p className="text-white/30 text-sm">Снимок данных на момент проверки</p>
              </div>
            </div>
          </Reveal>

          {/* Monitoring */}
          <Reveal delay={100}>
            <div className="relative rounded-3xl border border-green/30 bg-green/5 p-8 h-full overflow-hidden">
              <div
                className="absolute -top-12 -right-12 h-32 w-32 rounded-full bg-green/10 blur-2xl"
                aria-hidden="true"
              />
              <div className="relative">
                <div className="flex items-center gap-3 mb-6">
                  <span className="flex items-center justify-center h-12 w-12 rounded-2xl bg-green">
                    <Radar size={24} className="text-white" aria-hidden="true" />
                  </span>
                  <h3 className="text-xl font-bold text-white">Мониторинг</h3>
                </div>
                <p className="text-white/60 leading-relaxed">
                  Непрерывный контроль изменений. Вы получаете уведомления, когда у компании меняются владельцы, появляются новые судебные дела, налоговая задолженность или санкционные совпадения.
                </p>
                <div className="mt-6 pt-6 border-t border-green/20">
                  <div className="flex items-center gap-2 text-green text-sm font-medium">
                    <Bell size={16} aria-hidden="true" />
                    Уведомления об изменениях
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </div>

        {/* Change timeline */}
        <Reveal delay={200}>
          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 sm:p-8">
            <h3 className="text-white font-semibold mb-6 flex items-center gap-2">
              <Bell size={18} className="text-green" aria-hidden="true" />
              Что отслеживает мониторинг
            </h3>
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-0 right-0 top-4 h-px bg-white/10 hidden sm:block" aria-hidden="true" />
              <div className="grid sm:grid-cols-4 gap-6">
                {CHANGES.map((c, i) => (
                  <div key={i} className="relative">
                    <div className="flex sm:flex-col items-center sm:items-start gap-3 sm:gap-0">
                      <span className="relative z-10 flex items-center justify-center h-8 w-8 rounded-full bg-navy border-2 border-green shrink-0">
                        <span className="h-2 w-2 rounded-full bg-green" />
                      </span>
                      <div className="sm:mt-4">
                        <p className="text-white/40 text-xs tabular-nums">{c.date}</p>
                        <p className="text-white text-sm font-medium mt-1">{c.event}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Reveal>

        <Reveal delay={300}>
          <div className="mt-12 text-center">
            <a
              href="#demo"
              className="inline-flex items-center gap-2 rounded-full bg-green px-7 py-3.5 text-base font-semibold text-white hover:bg-green-dark transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green focus-visible:ring-offset-2 focus-visible:ring-offset-navy"
            >
              Добавить компанию в мониторинг
              <ArrowRight size={18} aria-hidden="true" />
            </a>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
