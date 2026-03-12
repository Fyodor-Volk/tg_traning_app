export {};

declare global {
  interface TelegramUser {
    id: number;
    first_name: string;
    last_name?: string;
    username?: string;
    language_code?: string;
  }

  interface TelegramWebApp {
    initData: string;
    initDataUnsafe: {
      user?: TelegramUser;
      [key: string]: unknown;
    };
    ready(): void;
    expand(): void;
    close(): void;
    setBackgroundColor(color: string): void;
    setHeaderColor(color: string): void;
  }

  interface Telegram {
    WebApp: TelegramWebApp;
  }

  interface Window {
    Telegram?: Telegram;
  }
}

