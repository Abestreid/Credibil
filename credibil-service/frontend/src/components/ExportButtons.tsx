import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import i18n from '@/i18n';

interface ExportButtonsProps {
  entityType: 'company' | 'person';
  entityId: string;
}

export default function ExportButtons({ entityType, entityId }: ExportButtonsProps) {
  const { t } = useTranslation();
  const [exporting, setExporting] = useState<'pdf' | 'xlsx' | null>(null);

  const handleExport = async (format: 'pdf' | 'xlsx') => {
    setExporting(format);
    try {
      const lang = i18n.language?.startsWith('ru') ? 'ru' : 'ro';
      const url = `/api/v1/export/${entityType}/${encodeURIComponent(entityId)}/${format}?lang=${lang}`;
      const resp = await fetch(url);
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }
      const blob = await resp.blob();
      const ext = format === 'pdf' ? 'pdf' : 'xlsx';

      // Extract filename from Content-Disposition (prefer filename*=UTF-8)
      const cd = resp.headers.get('Content-Disposition') || '';
      let filename = `credibil_report.${ext}`;
      const utf8Match = cd.match(/filename\*=UTF-8''([^;\n]+)/);
      if (utf8Match) {
        filename = decodeURIComponent(utf8Match[1]);
      } else {
        const m = cd.match(/filename="?([^";\n]+)"?/);
        if (m) filename = m[1];
      }

      const url2 = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url2;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url2), 5000);
    } catch (err) {
      alert(t('export.error'));
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => handleExport('pdf')}
        disabled={exporting !== null}
        title={t('export.tooltipPdf')}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {exporting === 'pdf' ? (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
            <path d="M4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V5.5L9.5 0H4zm5 0v5h4L9 0zM4.5 8h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1zm0 2.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1zm0 2.5h4a.5.5 0 0 1 0 1h-4a.5.5 0 0 1 0-1z" />
          </svg>
        )}
        {t('export.pdf')}
      </button>
      <button
        onClick={() => handleExport('xlsx')}
        disabled={exporting !== null}
        title={t('export.tooltipXlsx')}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {exporting === 'xlsx' ? (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
            <path d="M4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V5.5L9.5 0H4zm5 0v5h4L9 0zM5.5 9l1.5 2 1.5-2h1l-2 2.5L9.5 14h-1L7 12l-1.5 2h-1l2-2.5L4.5 9h1z" />
          </svg>
        )}
        {t('export.xlsx')}
      </button>
    </div>
  );
}
