import { useTranslations } from 'next-intl';

export default function HomePage() {
  const t = useTranslations('nav');
  return (
    <div>
      <h1>{t('dashboard')}</h1>
    </div>
  );
}
