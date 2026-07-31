import { FileText, FileSpreadsheet, Download } from 'lucide-react';
import { Reveal } from './Reveal';

export function Reports() {
  return (
    <section id="otchyoty" className="relative bg-surface-warm py-24 sm:py-32">
      <div className="mx-auto max-w-5xl px-5 sm:px-8">
        <Reveal>
          <div className="max-w-2xl mb-12">
            <span className="text-green-dark text-sm font-semibold tracking-widest uppercase">Отчёты</span>
            <h2 className="mt-4 text-3xl sm:text-4xl lg:text-5xl font-bold text-navy tracking-tight text-balance">
              Экспорт для&nbsp;принятия решения
            </h2>
            <p className="mt-5 text-text-muted text-lg leading-relaxed text-pretty">
              Сформируйте отчёт по компании и сохраните его для коллег, юристов или комплаенс-отдела. Доступен экспорт в двух форматах.
            </p>
          </div>
        </Reveal>

        <div className="grid sm:grid-cols-2 gap-6">
          {/* PDF */}
          <Reveal>
            <div className="group relative rounded-3xl border border-border bg-white p-8 overflow-hidden hover:border-green/30 transition-colors duration-300">
              <div className="flex items-center gap-4 mb-6">
                <span className="flex items-center justify-center h-14 w-14 rounded-2xl bg-navy">
                  <FileText size={28} className="text-white" aria-hidden="true" />
                </span>
                <div>
                  <h3 className="text-xl font-bold text-navy">PDF</h3>
                  <p className="text-sm text-text-muted">Структурированный документ</p>
                </div>
              </div>
              <ul className="space-y-2.5 text-sm text-text-muted">
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green" /> Основные сведения о компании</li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green" /> Владельцы и руководство</li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green" /> Связи и события</li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green" /> Факторы риска</li>
              </ul>
              <div className="mt-8 inline-flex items-center gap-2 text-navy font-semibold text-sm group-hover:text-green-dark transition-colors">
                <Download size={16} aria-hidden="true" />
                Экспортировать PDF
              </div>
            </div>
          </Reveal>

          {/* Excel */}
          <Reveal delay={100}>
            <div className="group relative rounded-3xl border border-border bg-white p-8 overflow-hidden hover:border-green/30 transition-colors duration-300">
              <div className="flex items-center gap-4 mb-6">
                <span className="flex items-center justify-center h-14 w-14 rounded-2xl bg-green-dark">
                  <FileSpreadsheet size={28} className="text-white" aria-hidden="true" />
                </span>
                <div>
                  <h3 className="text-xl font-bold text-navy">Excel</h3>
                  <p className="text-sm text-text-muted">Табличный формат</p>
                </div>
              </div>
              <ul className="space-y-2.5 text-sm text-text-muted">
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green" /> Структурированные данные</li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green" /> Финансовые показатели</li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green" /> Списки связанных лиц</li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green" /> Хронология изменений</li>
              </ul>
              <div className="mt-8 inline-flex items-center gap-2 text-navy font-semibold text-sm group-hover:text-green-dark transition-colors">
                <Download size={16} aria-hidden="true" />
                Экспортировать Excel
              </div>
            </div>
          </Reveal>
        </div>

        <Reveal delay={200}>
          <p className="mt-6 text-xs text-text-muted/60 text-center">
            Точный состав готового отчёта определяется сервисом. Подтверждена возможность экспорта в обоих форматах.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
