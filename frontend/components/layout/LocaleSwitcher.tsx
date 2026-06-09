'use client';

import { usePathname, useRouter } from 'next/navigation';
import { locales } from '@/i18n/config';

export function LocaleSwitcher() {
  const pathname = usePathname();
  const router = useRouter();

  function switchLocale(newLocale: string) {
    const segments = pathname.split('/');
    segments[1] = newLocale;
    router.push(segments.join('/'));
  }

  const currentLocale = pathname.split('/')[1] || 'en';

  return (
    <div className="locale-switcher" data-testid="locale-switcher">
      {locales.map((locale) => (
        <button
          key={locale}
          onClick={() => switchLocale(locale)}
          className={currentLocale === locale ? 'active' : ''}
          data-testid={`locale-${locale}`}
        >
          {locale.toUpperCase()}
        </button>
      ))}
      <style jsx>{`
        .locale-switcher {
          display: flex;
          gap: 4px;
          margin-bottom: 8px;
        }
        button {
          background: none;
          border: 1px solid var(--color-sidebar-hover);
          color: var(--color-sidebar-text);
          padding: 4px 8px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        }
        button.active {
          background: var(--color-sidebar-hover);
          font-weight: 600;
        }
      `}</style>
    </div>
  );
}
