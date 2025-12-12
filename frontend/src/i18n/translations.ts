/**
 * @fileoverview Application translations for multilingual support
 */

export type Language = 'az' | 'en' | 'ru';

export interface Translations {
  app: {
    title: string;
    subtitle: string;
  };
  welcome: {
    title: string;
    subtitle: string;
    cta: string;
    features: {
      ai: { title: string; description: string };
      search: { title: string; description: string };
      trends: { title: string; description: string };
      instant: { title: string; description: string };
    };
  };
  chat: {
    inputPlaceholder: string;
    send: string;
    typing: string;
    aiReady: string;
  };
  filters: {
    today: string;
    week: string;
    month: string;
    year: string;
    all: string;
  };
  quickQueries: {
    title: string;
    positive: string;
    loudest: string;
    today: string;
    politics: string;
    tech: string;
  };
  trending: {
    title: string;
    mentions: string;
  };
  categories: {
    title: string;
  };
  latestNews: {
    title: string;
    important: string;
    justNow: string;
    hoursAgo: string;
    yesterday: string;
    daysAgo: string;
  };
  sentiment: {
    positive: string;
    negative: string;
    neutral: string;
  };
  indexStatus: {
    title: string;
    synced: string;
    syncing: string;
    error: string;
    unknown: string;
    lastUpdate: string;
    lastSync: string;
    totalDocs: string;
    totalNews: string;
  };
  theme: {
    light: string;
    dark: string;
  };
  topEvents: string;
}

export const translations: Record<Language, Translations> = {
  az: {
    app: {
      title: 'NewsChat',
      subtitle: 'AI ilə xəbər analitikası',
    },
    welcome: {
      title: 'NewsChat-a xoş gəlmisiniz!',
      subtitle: 'Xəbərləri təhlil etmək üçün şəxsi AI köməkçiniz. Azərbaycanda baş verən hadisələr haqqında istənilən sual verin.',
      cta: 'Sualdan başlayın və ya aşağıdan sürətli sorğu seçin',
      features: {
        ai: {
          title: 'AI Analitika',
          description: 'Süni intellekt ilə ağıllı xəbər təhlili',
        },
        search: {
          title: 'Sürətli Axtarış',
          description: 'İstənilən xəbəri saniyələr ərzində tapın',
        },
        trends: {
          title: 'Trendlər',
          description: 'Ən aktual mövzuları izləyin',
        },
        instant: {
          title: 'Dərhal',
          description: 'Real vaxtda cavablar alın',
        },
      },
    },
    chat: {
      inputPlaceholder: 'Xəbərlər haqqında sual verin...',
      send: 'Göndər',
      typing: 'yazır',
      aiReady: 'AI kömək etməyə hazırdır',
    },
    filters: {
      today: 'Bu gün',
      week: 'Həftə',
      month: 'Ay',
      year: '2025',
      all: 'Hamısı',
    },
    quickQueries: {
      title: 'Sürətli sorğular',
      positive: 'Qarabağ - Ayaks matçı haqqında',
      loudest: 'Qarabağ - Çelsi matçı haqqında',
      today: '"Qobu Park"dakı yanğın haqqında',
      politics: 'Generalın oğlunun həbs edilməsi haqqında',
      tech: 'İtkin balıqçıların xilas edilməsi haqqında',
    },
    trending: {
      title: 'İsti Mövzular',
      mentions: 'qeyd',
    },
    categories: {
      title: 'Kateqoriyalar',
    },
    latestNews: {
      title: 'Son Xəbərlər',
      important: 'Vacib',
      justNow: 'İndicə',
      hoursAgo: 's əvvəl',
      yesterday: 'Dünən',
      daysAgo: 'g əvvəl',
    },
    sentiment: {
      positive: 'Pozitiv',
      negative: 'Neqativ',
      neutral: 'Neytral',
    },
    indexStatus: {
      title: 'İndeks statusu',
      synced: 'Sinxronlaşdırılıb',
      syncing: 'Sinxronlaşdırılır...',
      error: 'Xəta',
      unknown: 'Naməlum',
      lastUpdate: 'Son yeniləmə:',
      lastSync: 'Son yeniləmə:',
      totalDocs: 'Sənədlər:',
      totalNews: 'Bütün xəbərlər:',
    },
    theme: {
      light: 'İşıqlı tema',
      dark: 'Qaranlıq tema',
    },
    topEvents: 'Mənbələr',
  },
  en: {
    app: {
      title: 'NewsChat',
      subtitle: 'AI-powered news analytics',
    },
    welcome: {
      title: 'Welcome to NewsChat!',
      subtitle: 'Your personal AI assistant for news analysis. Ask any question about events in Azerbaijan.',
      cta: 'Start with a question or select a quick query below',
      features: {
        ai: {
          title: 'AI Analytics',
          description: 'Smart news analysis with artificial intelligence',
        },
        search: {
          title: 'Fast Search',
          description: 'Find any news in seconds',
        },
        trends: {
          title: 'Trends',
          description: 'Track the most relevant topics',
        },
        instant: {
          title: 'Instant',
          description: 'Get answers in real-time',
        },
      },
    },
    chat: {
      inputPlaceholder: 'Ask about news...',
      send: 'Send',
      typing: 'typing',
      aiReady: 'AI is ready to help',
    },
    filters: {
      today: 'Today',
      week: 'Week',
      month: 'Month',
      year: '2025',
      all: 'All',
    },
    quickQueries: {
      title: 'Quick queries',
      positive: 'About Qarabag - Ajax match',
      loudest: 'About Qarabag - Chelsea match',
      today: 'About "Qobu Park" fire',
      politics: 'About general\'s son arrest',
      tech: 'About missing fishermen rescue',
    },
    trending: {
      title: 'Hot Topics',
      mentions: 'mentions',
    },
    categories: {
      title: 'Categories',
    },
    latestNews: {
      title: 'Latest News',
      important: 'Important',
      justNow: 'Just now',
      hoursAgo: 'h ago',
      yesterday: 'Yesterday',
      daysAgo: 'd ago',
    },
    sentiment: {
      positive: 'Positive',
      negative: 'Negative',
      neutral: 'Neutral',
    },
    indexStatus: {
      title: 'Index status',
      synced: 'Synced',
      syncing: 'Syncing...',
      error: 'Error',
      unknown: 'Unknown',
      lastUpdate: 'Last update:',
      lastSync: 'Last sync:',
      totalDocs: 'Documents:',
      totalNews: 'Total news:',
    },
    theme: {
      light: 'Light theme',
      dark: 'Dark theme',
    },
    topEvents: 'Top events',
  },
  ru: {
    app: {
      title: 'NewsChat',
      subtitle: 'AI-powered новостная аналитика',
    },
    welcome: {
      title: 'Добро пожаловать в NewsChat!',
      subtitle: 'Ваш персональный AI-ассистент для анализа новостей. Задайте любой вопрос о событиях в Азербайджане.',
      cta: 'Начните с вопроса или выберите быстрый запрос ниже',
      features: {
        ai: {
          title: 'AI-аналитика',
          description: 'Умный анализ новостей с помощью искусственного интеллекта',
        },
        search: {
          title: 'Быстрый поиск',
          description: 'Найдите любую новость за считанные секунды',
        },
        trends: {
          title: 'Тренды',
          description: 'Следите за самыми актуальными темами',
        },
        instant: {
          title: 'Мгновенно',
          description: 'Получайте ответы в режиме реального времени',
        },
      },
    },
    chat: {
      inputPlaceholder: 'Задайте вопрос о новостях...',
      send: 'Отправить',
      typing: 'печатает',
      aiReady: 'AI готов помочь',
    },
    filters: {
      today: 'Сегодня',
      week: 'Неделя',
      month: 'Месяц',
      year: '2025',
      all: 'Все',
    },
    quickQueries: {
      title: 'Быстрые запросы',
      positive: 'О матче Карабах - Аякс',
      loudest: 'О матче Карабах - Челси',
      today: 'О пожаре в "Qobu Park"',
      politics: 'Об аресте сына генерала',
      tech: 'О спасении пропавших рыбаков',
    },
    trending: {
      title: 'Горячие темы',
      mentions: 'упоминаний',
    },
    categories: {
      title: 'Категории',
    },
    latestNews: {
      title: 'Последние новости',
      important: 'Важно',
      justNow: 'Только что',
      hoursAgo: 'ч назад',
      yesterday: 'Вчера',
      daysAgo: 'д назад',
    },
    sentiment: {
      positive: 'Позитивно',
      negative: 'Негативно',
      neutral: 'Нейтрально',
    },
    indexStatus: {
      title: 'Статус индекса',
      synced: 'Синхронизировано',
      syncing: 'Синхронизация...',
      error: 'Ошибка',
      unknown: 'Неизвестно',
      lastUpdate: 'Последнее обновление:',
      lastSync: 'Последняя синхронизация:',
      totalDocs: 'Документов:',
      totalNews: 'Всего новостей:',
    },
    theme: {
      light: 'Светлая тема',
      dark: 'Темная тема',
    },
    topEvents: 'Топ события',
  },
};
