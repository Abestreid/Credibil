import { useEffect, useRef, useState } from 'react';
import { Building2, Users, Network, CalendarClock, ShieldAlert, FileText, Radar } from 'lucide-react';

const STEPS = [
  { icon: Building2, label: 'Компания', desc: 'Название, IDNO, статус, дата регистрации, правовая форма, адрес, CAEM' },
  { icon: Users, label: 'Владельцы', desc: 'Учредители и доли, администраторы и руководство' },
  { icon: Network, label: 'Связи', desc: 'Другие компании связанных лиц, роли в организациях, активные и ликвидированные' },
  { icon: CalendarClock, label: 'События', desc: 'Судебные дела, публичные извещения UNEJ, хронология изменений' },
  { icon: ShieldAlert, label: 'Риски', desc: 'Налоговая задолженность, санкционный раздел, факторы риска' },
  { icon: FileText, label: 'Отчёт', desc: 'Экспорт в PDF или Excel для принятия решения' },
  { icon: Radar, label: 'Мониторинг', desc: 'Добавьте компанию и отслеживайте последующие изменения' },
];

export function StoryChain() {
  const sectionRef = useRef<HTMLDivElement | null>(null);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      const node = sectionRef.current;
      if (!node) return;
      const rect = node.getBoundingClientRect();
      const viewH = window.innerHeight;
      const total = rect.height - viewH;
      const scrolled = Math.max(0, -rect.top);
      const progress = Math.min(1, Math.max(0, scrolled / total));
      const step = Math.min(STEPS.length - 1, Math.floor(progress * STEPS.length));
      setActiveStep(step);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <section ref={sectionRef} className="relative bg-navy-dark py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-5 sm:px-8">
        <div className="max-w-2xl mb-16">
          <span className="text-green text-sm font-semibold tracking-widest uppercase">Главная идея</span>
          <h2 className="mt-4 text-3xl sm:text-4xl lg:text-5xl font-bold text-white tracking-tight text-balance">
            Цепочка, которая ведёт к&nbsp;решению
          </h2>
          <p className="mt-5 text-white/50 text-lg leading-relaxed text-pretty">
            Credibil раскрывает путь от названия компании до контроля изменений. Каждый шаг — это новый слой данных, который делает картину всё более полной.
          </p>
        </div>

        {/* Desktop: horizontal chain with sticky highlight */}
        <div className="hidden lg:block relative">
          {/* Progress line */}
          <div className="absolute top-12 left-0 right-0 h-px bg-white/10">
            <div
              className="h-px bg-green transition-all duration-500 ease-out"
              style={{ width: `${(activeStep / (STEPS.length - 1)) * 100}%` }}
            />
          </div>

          <div className="grid grid-cols-7 gap-2">
            {STEPS.map((step, i) => {
              const Icon = step.icon;
              const isActive = i <= activeStep;
              const isCurrent = i === activeStep;
              return (
                <div key={step.label} className="flex flex-col items-center text-center">
                  <div
                    className={`relative z-10 flex items-center justify-center h-24 w-24 rounded-2xl border transition-all duration-500 ${
                      isCurrent
                        ? 'bg-green border-green scale-110 shadow-lg shadow-green/30'
                        : isActive
                        ? 'bg-navy border-green/40'
                        : 'bg-navy border-white/10'
                    }`}
                  >
                    <Icon
                      size={28}
                      className={`transition-colors duration-500 ${isCurrent ? 'text-white' : isActive ? 'text-green' : 'text-white/30'}`}
                      aria-hidden="true"
                    />
                    {isCurrent && (
                      <span className="absolute inset-0 rounded-2xl border-2 border-green/40 animate-ping" aria-hidden="true" />
                    )}
                  </div>
                  <span
                    className={`mt-4 text-sm font-semibold transition-colors duration-300 ${
                      isCurrent ? 'text-white' : isActive ? 'text-white/60' : 'text-white/30'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Active step description */}
          <div className="mt-10 min-h-[80px] flex items-start justify-center">
            <p key={activeStep} className="text-white/50 text-base max-w-lg text-center animate-fade-in text-pretty">
              {STEPS[activeStep].desc}
            </p>
          </div>
        </div>

        {/* Mobile: vertical timeline */}
        <div className="lg:hidden space-y-6">
          {STEPS.map((step, i) => {
            const Icon = step.icon;
            return (
              <div key={step.label} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="flex items-center justify-center h-14 w-14 rounded-xl bg-navy border border-green/40 shrink-0">
                    <Icon size={24} className="text-green" aria-hidden="true" />
                  </div>
                  {i < STEPS.length - 1 && <div className="w-px flex-1 bg-white/10 mt-2" />}
                </div>
                <div className="pt-1 pb-6">
                  <h3 className="text-white font-semibold">{step.label}</h3>
                  <p className="mt-1 text-white/50 text-sm leading-relaxed">{step.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
