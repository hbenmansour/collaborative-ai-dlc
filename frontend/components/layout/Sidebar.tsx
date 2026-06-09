'use client';

import { useTranslations } from 'next-intl';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/components/providers/AuthProvider';
import { LocaleSwitcher } from './LocaleSwitcher';

const navItems = [
  { key: 'dashboard', href: '/', icon: '📊' },
  { key: 'contracts', href: '/contracts', icon: '📄' },
  { key: 'customers', href: '/customers', icon: '👥' },
  { key: 'billing', href: '/billing', icon: '💰' },
  { key: 'accounting', href: '/accounting', icon: '📒' },
  { key: 'collections', href: '/collections', icon: '📋' },
  { key: 'reports', href: '/reports', icon: '📈' },
  { key: 'chat', href: '/chat', icon: '🤖' },
  { key: 'settings', href: '/settings', icon: '⚙️' },
] as const;

export function Sidebar() {
  const t = useTranslations('nav');
  const pathname = usePathname();
  const { user, handleSignOut } = useAuth();

  // Extract locale from pathname
  const locale = pathname.split('/')[1] || 'en';

  return (
    <aside className="sidebar" data-testid="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">Leasing ERP</h2>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const fullHref = `/${locale}${item.href}`;
          const isActive =
            item.href === '/'
              ? pathname === `/${locale}` || pathname === `/${locale}/`
              : pathname.startsWith(fullHref);

          return (
            <Link
              key={item.key}
              href={fullHref}
              className={`sidebar-link ${isActive ? 'active' : ''}`}
              data-testid={`nav-${item.key}`}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span>{t(item.key)}</span>
            </Link>
          );
        })}
      </nav>
      <div className="sidebar-footer">
        <LocaleSwitcher />
        {user && (
          <button
            onClick={handleSignOut}
            className="sidebar-signout"
            data-testid="sign-out-btn"
          >
            {user.username}
          </button>
        )}
      </div>
      <style jsx>{`
        .sidebar {
          position: fixed;
          top: 0;
          left: 0;
          width: var(--sidebar-width);
          height: 100vh;
          background: var(--color-sidebar-bg);
          color: var(--color-sidebar-text);
          display: flex;
          flex-direction: column;
          overflow-y: auto;
        }
        .sidebar-header {
          padding: 20px 16px;
          border-bottom: 1px solid var(--color-sidebar-hover);
        }
        .sidebar-title {
          font-size: 18px;
          font-weight: 700;
        }
        .sidebar-nav {
          flex: 1;
          padding: 8px;
        }
        .sidebar-link {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 12px;
          border-radius: 6px;
          color: var(--color-sidebar-text);
          text-decoration: none;
          font-size: 14px;
          transition: background 0.15s;
        }
        .sidebar-link:hover,
        .sidebar-link.active {
          background: var(--color-sidebar-hover);
        }
        .sidebar-icon {
          font-size: 16px;
        }
        .sidebar-footer {
          padding: 12px 16px;
          border-top: 1px solid var(--color-sidebar-hover);
        }
        .sidebar-signout {
          background: none;
          border: none;
          color: var(--color-sidebar-text);
          cursor: pointer;
          font-size: 12px;
          padding: 4px 0;
          opacity: 0.7;
        }
      `}</style>
    </aside>
  );
}
