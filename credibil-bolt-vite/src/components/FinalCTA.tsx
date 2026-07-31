import { ArrowRight } from 'lucide-react';
import { Reveal } from './Reveal';

export function FinalCTA() {
  return (
    <section id="demo" className="relative bg-navy-dark py-24 sm:py-32 overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-40" aria-hidden="true" />
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
        style={{
          background: 'radial-gradient(ellipse 60% 50% at 50% 50%, rgba(42, 156, 111, 0.15), transparent 70%)',
        }}
      />

      <div className="relative mx-auto max-w-4xl px-5 sm:px-8 text-center">
        <Reveal>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white tracking-tight text-balance">
            Проверьте компанию, контрагента или&nbsp;связанное лицо
          </h2>
          <p className="mt-5 text-white/50 text-lg leading-relaxed max-w-2xl mx-auto text-pretty">
            Credibil превращает разрозненные сведения в понятную картину — от названия компании до контроля изменений.
          </p>
        </Reveal>

        <Reveal delay={100}>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="#poisk"
              className="inline-flex items-center gap-2 rounded-full bg-green px-7 py-3.5 text-base font-semibold text-white hover:bg-green-dark transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green focus-visible:ring-offset-2 focus-visible:ring-offset-navy-dark"
            >
              Начать поиск
              <ArrowRight size={18} aria-hidden="true" />
            </a>
            <a
              href="#istochniki"
              className="inline-flex items-center gap-2 rounded-full border border-white/20 px-7 py-3.5 text-base font-semibold text-white hover:bg-white/5 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green focus-visible:ring-offset-2 focus-visible:ring-offset-navy-dark"
            >
              Узнать об источниках
            </a>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
