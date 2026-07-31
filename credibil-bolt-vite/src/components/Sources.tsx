import { Database, Landmark, BarChart3, Scale, Gavel, ShoppingCart, Award, ShieldAlert } from 'lucide-react';
import { Reveal } from './Reveal';

const SOURCES = [
  { icon: Database, name: 'Портал открытых данных', desc: 'Государственный портал открытых данных Молдовы' },
  { icon: Landmark, name: 'Налоговая служба', desc: 'Государственная налоговая служба' },
  { icon: BarChart3, name: 'Бюро статистики', desc: 'Национальное бюро статистики' },
  { icon: Scale, name: 'Судебные инстанции', desc: 'Национальный портал судебных инстанций' },
  { icon: Gavel, name: 'Судебные исполнители', desc: 'Национальный союз судебных исполнителей' },
  { icon: ShoppingCart, name: 'MTender', desc: 'Система государственных закупок' },
  { icon: Award, name: 'MOLDAC', desc: 'Центр аккредитации' },
  { icon: ShieldAlert, name: 'Санкционная интеграция', desc: 'Специализированная санкционная интеграция' },
];

export function Sources() {
  return (
    <section id="istochniki" className="relative bg-surface py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <Reveal>
          <div className="max-w-2xl mb-12">
            <span className="text-green-dark text-sm font-semibold tracking-widest uppercase">Источники данных</span>
            <h2 className="mt-4 text-3xl sm:text-4xl lg:text-5xl font-bold text-navy tracking-tight text-balance">
              Сведения из&nbsp;официальных источников
            </h2>
            <p className="mt-5 text-text-muted text-lg leading-relaxed text-pretty">
              Credibil собирает данные из государственных, официальных и специализированных источников Республики Молдова. Все сведения структурированы и представлены в едином формате.
            </p>
          </div>
        </Reveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {SOURCES.map((src, i) => {
            const Icon = src.icon;
            return (
              <Reveal key={src.name} delay={i * 60}>
                <div className="group h-full rounded-2xl border border-border bg-white p-6 hover:border-green/30 hover:shadow-lg hover:shadow-navy/5 transition-all duration-300">
                  <span className="flex items-center justify-center h-12 w-12 rounded-xl bg-navy/5 group-hover:bg-green/10 transition-colors duration-300">
                    <Icon size={24} className="text-navy group-hover:text-green-dark transition-colors duration-300" aria-hidden="true" />
                  </span>
                  <h3 className="mt-4 font-semibold text-navy">{src.name}</h3>
                  <p className="mt-1 text-sm text-text-muted leading-relaxed">{src.desc}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
