import { Info } from 'lucide-react';
import { Reveal } from './Reveal';

const LIMITS = [
  'Credibil не является государственным реестром и не заменяет юридическое заключение.',
  'Сервис не гарантирует отсутствия рисков или стопроцентной точности данных.',
  'Данные собираются из сторонних источников, и их актуальность зависит от обновления источников.',
  'Credibil помогает принять решение, но не заменяет профессиональную юридическую консультацию.',
];

export function Limitations() {
  return (
    <section className="relative bg-teal-dark py-24 sm:py-32">
      <div className="mx-auto max-w-4xl px-5 sm:px-8">
        <Reveal>
          <div className="rounded-3xl border border-white/10 bg-navy/40 p-8 sm:p-12">
            <div className="flex items-center gap-3 mb-8">
              <span className="flex items-center justify-center h-12 w-12 rounded-2xl bg-white/10">
                <Info size={24} className="text-white" aria-hidden="true" />
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-white">Важно знать</h2>
            </div>
            <ul className="space-y-4" role="list">
              {LIMITS.map((limit, i) => (
                <li key={i} className="flex items-start gap-3">
                  <span className="mt-2 h-1.5 w-1.5 rounded-full bg-green shrink-0" aria-hidden="true" />
                  <p className="text-white/60 leading-relaxed">{limit}</p>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
