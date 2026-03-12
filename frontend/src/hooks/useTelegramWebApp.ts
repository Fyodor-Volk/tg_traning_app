import { useEffect, useState } from "react";

export interface TelegramContext {
  initData: string;
  user?: TelegramUser;
  isReady: boolean;
}

export const useTelegramWebApp = (): TelegramContext => {
  const [state, setState] = useState<TelegramContext>({
    initData: "",
    user: undefined,
    isReady: false
  });

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) {
      setState((prev) => ({ ...prev, isReady: true }));
      return;
    }

    tg.ready();
    tg.expand();
    tg.setBackgroundColor("#0e1621");
    tg.setHeaderColor("#0e1621");

    setState({
      initData: tg.initData,
      user: tg.initDataUnsafe.user,
      isReady: true
    });
  }, []);

  return state;
};

