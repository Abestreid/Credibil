import { useState } from 'react';
import {
  Building2, Check, AlertTriangle, Calendar, MapPin, FileBarChart,
  Users, User, Network, Gavel, FileWarning, ShoppingBag, Award,
  Ban, History, DollarSign, TrendingUp, ChevronDown,
} from 'lucide-react';
import { Reveal } from './Reveal';

type Section = {
  id: string;
  icon: typeof Building2;
  label: string;
  status?: 'ok' | 'warn' | 'danger' | 'neutral';
  content: React.ReactNode;
};

const COMPANY = {
  name: 'MoldovaAgroindbank SA',
  idno: '1002600030037',
  status: 'Активна',
  registered: '22.10.1991',
  form: 'Акционерное общество',
  address: 'г. Кишинёв, ул. Армянская 38',
  caem: 'K6419 — Деятельность по денежному посредничеству',
  taxDebt: '0 MDL',
  founders: [
    { name: 'Иван Иванов', share: '34.5%', role: 'Учредитель' },
    { name: 'Анна Кишкан', share: '21.0%', role: 'Учредитель' },
    { name: 'Прочие акционеры', share: '44.5%', role: 'Акционеры' },
  ],
  admins: [
    { name: 'Сергей Райля', role: 'Председатель правления' },
    { name: 'Мария Лупу', role: 'Член правления' },
  ],
  related: [
    { name: 'Agroind Capital SRL', relation: 'Связанная компания', status: 'Активна' },
    { name: 'MAIB Leasing SRL', relation: 'Дочерняя компания', status: 'Активна' },
    { name: 'Moldova Finance SA', relation: 'Связанная компания', status: 'Ликвидирована' },
  ],
  finance: [
    { year: '2023', revenue: '1 245 млн MDL', profit: '+18.4 млн MDL' },
    { year: '2022', revenue: '1 102 млн MDL', profit: '+12.1 млн MDL' },
    { year: '2021', revenue: '980 млн MDL', profit: '+8.7 млн MDL' },
  ],
  litigation: [
    { caseNo: '2019-0114/3', type: 'Гражданское', date: '14.03.2023' },
    { caseNo: '2021-0089/1', type: 'Административное', date: '22.11.2022' },
  ],
  unej: [
    { notice: 'Извещение о возбуждении исполнительного производства', date: '05.02.2024' },
  ],
  procurement: [
    { tender: 'Закупка IT-оборудования для филиалов', source: 'MTender', date: '18.01.2024' },
    { tender: 'Аренда помещений под отделение', source: 'MTender', date: '09.11.2023' },
  ],
  moldac: [
    { cert: 'Аккредитация лаборатории анализа рисков', status: 'Действует' },
  ],
  sanctions: 'Санкционные списки: совпадений не найдено',
  history: [
    { date: '15.01.2024', event: 'Изменение состава администраторов' },
    { date: '02.10.2023', event: 'Изменение юридического адреса' },
    { date: '18.06.2023', event: 'Увеличение уставного капитала' },
  ],
};

export function CompanyCard() {
  const [openSection, setOpenSection] = useState<string | null>('overview');

  const sections: Section[] = [
    {
      id: 'overview',
      icon: Building2,
      label: 'Основные сведения',
      status: 'ok',
      content: (
        <div className="grid sm:grid-cols-2 gap-x-8 gap-y-4">
          <Field label="Юридический статус" value={COMPANY.status} highlight="ok" />
          <Field label="Дата регистрации" value={COMPANY.registered} />
          <Field label="Правовая форма" value={COMPANY.form} />
          <Field label="IDNO" value={COMPANY.idno} mono />
          <Field label="Адрес" value={COMPANY.address} />
          <Field label="CAEM" value={COMPANY.caem} />
        </div>
      ),
    },
    {
      id: 'tax',
      icon: DollarSign,
      label: 'Налоговая задолженность',
      status: 'ok',
      content: (
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center justify-center h-10 w-10 rounded-full bg-green/10">
            <Check size={20} className="text-green-dark" aria-hidden="true" />
          </span>
          <div>
            <p className="text-navy font-semibold tabular-nums">{COMPANY.taxDebt}</p>
            <p className="text-sm text-text-muted">Задолженность перед налоговой службой не обнаружена</p>
          </div>
        </div>
      ),
    },
    {
      id: 'founders',
      icon: Users,
      label: 'Учредители и доли',
      content: (
        <ul className="space-y-3" role="list">
          {COMPANY.founders.map((f) => (
            <li key={f.name} className="flex items-center justify-between gap-4 py-2 border-b border-border last:border-0">
              <div className="flex items-center gap-3 min-w-0">
                <span className="flex items-center justify-center h-9 w-9 rounded-lg bg-navy/5 shrink-0">
                  <User size={18} className="text-navy" aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="font-medium text-navy truncate">{f.name}</p>
                  <p className="text-xs text-text-muted">{f.role}</p>
                </div>
              </div>
              <span className="font-semibold text-green-dark tabular-nums shrink-0">{f.share}</span>
            </li>
          ))}
        </ul>
      ),
    },
    {
      id: 'admins',
      icon: User,
      label: 'Администраторы и руководство',
      content: (
        <ul className="space-y-3" role="list">
          {COMPANY.admins.map((a) => (
            <li key={a.name} className="flex items-center gap-3 py-2 border-b border-border last:border-0">
              <span className="flex items-center justify-center h-9 w-9 rounded-lg bg-navy/5 shrink-0">
                <User size={18} className="text-navy" aria-hidden="true" />
              </span>
              <div>
                <p className="font-medium text-navy">{a.name}</p>
                <p className="text-xs text-text-muted">{a.role}</p>
              </div>
            </li>
          ))}
        </ul>
      ),
    },
    {
      id: 'related',
      icon: Network,
      label: 'Связанные компании и лица',
      content: (
        <ul className="space-y-3" role="list">
          {COMPANY.related.map((r) => (
            <li key={r.name} className="flex items-center justify-between gap-4 py-2 border-b border-border last:border-0">
              <div className="flex items-center gap-3 min-w-0">
                <span className="flex items-center justify-center h-9 w-9 rounded-lg bg-navy/5 shrink-0">
                  <Building2 size={18} className="text-navy" aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="font-medium text-navy truncate">{r.name}</p>
                  <p className="text-xs text-text-muted">{r.relation}</p>
                </div>
              </div>
              <span
                className={`text-xs font-medium px-2.5 py-1 rounded-full shrink-0 ${
                  r.status === 'Активна'
                    ? 'bg-green/10 text-green-dark'
                    : 'bg-red-500/10 text-red-600'
                }`}
              >
                {r.status}
              </span>
            </li>
          ))}
        </ul>
      ),
    },
    {
      id: 'finance',
      icon: TrendingUp,
      label: 'Финансовые сведения',
      content: (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-text-muted border-b border-border">
              <th className="font-medium pb-2">Год</th>
              <th className="font-medium pb-2">Выручка</th>
              <th className="font-medium pb-2">Прибыль</th>
            </tr>
          </thead>
          <tbody>
            {COMPANY.finance.map((f) => (
              <tr key={f.year} className="border-b border-border last:border-0">
                <td className="py-2.5 text-navy font-medium tabular-nums">{f.year}</td>
                <td className="py-2.5 text-navy tabular-nums">{f.revenue}</td>
                <td className="py-2.5 text-green-dark font-medium tabular-nums">{f.profit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ),
    },
    {
      id: 'litigation',
      icon: Gavel,
      label: 'Судебные события',
      status: 'warn',
      content: (
        <ul className="space-y-3" role="list">
          {COMPANY.litigation.map((l) => (
            <li key={l.caseNo} className="flex items-center justify-between gap-4 py-2 border-b border-border last:border-0">
              <div className="flex items-center gap-3 min-w-0">
                <span className="flex items-center justify-center h-9 w-9 rounded-lg bg-amber-500/10 shrink-0">
                  <Gavel size={18} className="text-amber-600" aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="font-medium text-navy truncate">Дело № {l.caseNo}</p>
                  <p className="text-xs text-text-muted">{l.type}</p>
                </div>
              </div>
              <span className="text-sm text-text-muted tabular-nums shrink-0">{l.date}</span>
            </li>
          ))}
        </ul>
      ),
    },
    {
      id: 'unej',
      icon: FileWarning,
      label: 'Публичные извещения UNEJ',
      status: 'warn',
      content: (
        <ul className="space-y-3" role="list">
          {COMPANY.unej.map((u, i) => (
            <li key={i} className="flex items-center justify-between gap-4 py-2 border-b border-border last:border-0">
              <div className="flex items-center gap-3 min-w-0">
                <span className="flex items-center justify-center h-9 w-9 rounded-lg bg-amber-500/10 shrink-0">
                  <FileWarning size={18} className="text-amber-600" aria-hidden="true" />
                </span>
                <p className="text-sm text-navy min-w-0">{u.notice}</p>
              </div>
              <span className="text-sm text-text-muted tabular-nums shrink-0">{u.date}</span>
            </li>
          ))}
        </ul>
      ),
    },
    {
      id: 'procurement',
      icon: ShoppingBag,
      label: 'Государственные закупки',
      content: (
        <ul className="space-y-3" role="list">
          {COMPANY.procurement.map((p, i) => (
            <li key={i} className="flex items-center justify-between gap-4 py-2 border-b border-border last:border-0">
              <div className="flex items-center gap-3 min-w-0">
                <span className="flex items-center justify-center h-9 w-9 rounded-lg bg-navy/5 shrink-0">
                  <ShoppingBag size={18} className="text-navy" aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="text-sm text-navy truncate">{p.tender}</p>
                  <p className="text-xs text-text-muted">Источник: {p.source}</p>
                </div>
              </div>
              <span className="text-sm text-text-muted tabular-nums shrink-0">{p.date}</span>
            </li>
          ))}
        </ul>
      ),
    },
    {
      id: 'moldac',
      icon: Award,
      label: 'Аккредитации MOLDAC',
      status: 'ok',
      content: (
        <ul className="space-y-3" role="list">
          {COMPANY.moldac.map((m, i) => (
            <li key={i} className="flex items-center justify-between gap-4 py-2">
              <div className="flex items-center gap-3">
                <span className="flex items-center justify-center h-9 w-9 rounded-lg bg-green/10 shrink-0">
                  <Award size={18} className="text-green-dark" aria-hidden="true" />
                </span>
                <p className="text-sm text-navy">{m.cert}</p>
              </div>
              <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-green/10 text-green-dark shrink-0">
                {m.status}
              </span>
            </li>
          ))}
        </ul>
      ),
    },
    {
      id: 'sanctions',
      icon: Ban,
      label: 'Санкционный раздел',
      status: 'ok',
      content: (
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center justify-center h-10 w-10 rounded-full bg-green/10">
            <Check size={20} className="text-green-dark" aria-hidden="true" />
          </span>
          <p className="text-navy">{COMPANY.sanctions}</p>
        </div>
      ),
    },
    {
      id: 'history',
      icon: History,
      label: 'Хронология изменений',
      content: (
        <div className="relative pl-6">
          <div className="absolute left-0 top-2 bottom-2 w-px bg-border" />
          <ul className="space-y-5" role="list">
            {COMPANY.history.map((h, i) => (
              <li key={i} className="relative">
                <span className="absolute -left-[25px] top-1.5 h-2.5 w-2.5 rounded-full bg-green border-2 border-surface" />
                <p className="text-sm text-text-muted tabular-nums">{h.date}</p>
                <p className="text-navy font-medium">{h.event}</p>
              </li>
            ))}
          </ul>
        </div>
      ),
    },
  ];

  return (
    <section id="kartochka" className="relative bg-surface py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-5 sm:px-8">
        <Reveal>
          <div className="max-w-2xl mb-12">
            <span className="text-green-dark text-sm font-semibold tracking-widest uppercase">Карточка компании</span>
            <h2 className="mt-4 text-3xl sm:text-4xl lg:text-5xl font-bold text-navy tracking-tight text-balance">
              Вся картина — на&nbsp;одном экране
            </h2>
            <p className="mt-5 text-text-muted text-lg leading-relaxed text-pretty">
              Откройте карточку компании и изучите сведения, владельцев, руководство, связи, события и факторы риска. Каждый блок раскрывается по мере необходимости.
            </p>
          </div>
        </Reveal>

        {/* Card */}
        <Reveal delay={100}>
          <div className="rounded-3xl border border-border bg-white shadow-xl shadow-navy/5 overflow-hidden">
            {/* Card header */}
            <div className="bg-navy px-6 sm:px-8 py-6 sm:py-8">
              <div className="flex items-start gap-4 flex-wrap">
                <div className="flex items-center justify-center h-14 w-14 rounded-2xl bg-white/10 shrink-0">
                  <Building2 size={28} className="text-white" aria-hidden="true" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl sm:text-2xl font-bold text-white">{COMPANY.name}</h3>
                  <p className="text-white/50 font-mono text-sm mt-1">IDNO {COMPANY.idno}</p>
                </div>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-green px-3 py-1.5 text-sm font-semibold text-white">
                  <Check size={14} aria-hidden="true" />
                  {COMPANY.status}
                </span>
              </div>
            </div>

            {/* Collapsible sections */}
            <div className="divide-y divide-border">
              {sections.map((s) => {
                const Icon = s.icon;
                const isOpen = openSection === s.id;
                const statusColor =
                  s.status === 'ok' ? 'bg-green' :
                  s.status === 'warn' ? 'bg-amber-500' :
                  s.status === 'danger' ? 'bg-red-500' : 'bg-text-muted/40';
                return (
                  <div key={s.id}>
                    <button
                      onClick={() => setOpenSection(isOpen ? null : s.id)}
                      className="w-full flex items-center gap-4 px-6 sm:px-8 py-5 text-left hover:bg-surface/50 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green focus-visible:ring-inset"
                      aria-expanded={isOpen}
                    >
                      <span className={`h-2 w-2 rounded-full ${statusColor} shrink-0`} aria-hidden="true" />
                      <Icon size={20} className="text-navy shrink-0" aria-hidden="true" />
                      <span className="flex-1 font-semibold text-navy">{s.label}</span>
                      <ChevronDown
                        size={20}
                        className={`text-text-muted transition-transform duration-300 shrink-0 ${isOpen ? 'rotate-180' : ''}`}
                        aria-hidden="true"
                      />
                    </button>
                    <div
                      className={`overflow-hidden transition-all duration-300 ease-out ${
                        isOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'
                      }`}
                    >
                      <div className="px-6 sm:px-8 pb-6 pt-1">
                        {s.content}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </Reveal>

        <p className="mt-4 text-xs text-text-muted/60 text-center">
          Демонстрационная карточка вымышленной компании. Реальные персональные данные не используются.
        </p>
      </div>
    </section>
  );
}

function Field({ label, value, mono, highlight }: { label: string; value: string; mono?: boolean; highlight?: 'ok' }) {
  return (
    <div>
      <dt className="text-xs text-text-muted uppercase tracking-wide">{label}</dt>
      <dd className={`mt-1 text-navy font-medium ${mono ? 'font-mono tabular-nums' : ''} ${highlight === 'ok' ? 'text-green-dark' : ''}`}>
        {value}
      </dd>
    </div>
  );
}
