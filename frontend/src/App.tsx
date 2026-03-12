import "./index.css";

import { useEffect, useMemo, useState } from "react";
import type { AxiosError } from "axios";

import { createApiClient } from "./lib/api";
import { useTelegramWebApp } from "./hooks/useTelegramWebApp";
import type { User } from "./types/api";
import { TemplatesView } from "./components/TemplatesView";
import { CalendarView } from "./components/CalendarView";
import { MetricsView } from "./components/MetricsView";

type Tab = "calendar" | "templates" | "metrics";

export const App: React.FC = () => {
  const tg = useTelegramWebApp();
  const [user, setUser] = useState<User | null>(null);
  const [tab, setTab] = useState<Tab>("calendar");
  const [error, setError] = useState<string | null>(null);

  const devTelegramId = (import.meta.env.VITE_DEV_TELEGRAM_ID as string | undefined) ?? undefined;

  const api = useMemo(
    () => createApiClient({ initData: tg.initData, devTelegramId }),
    [tg.initData, devTelegramId]
  );

  useEffect(() => {
    const fetchUser = async () => {
      try {
        if (tg.initData) {
          const { data } = await api.post<User>("/auth/telegram", { init_data: tg.initData });
          setUser(data);
          return;
        }

        if (import.meta.env.DEV && devTelegramId) {
          const { data } = await api.get<User>("/auth/me");
          setUser(data);
          return;
        }

        setError("Приложение должно быть открыто внутри Telegram Mini App.");
      } catch (err: unknown) {
        console.error(err);
        const axErr = err as AxiosError<{ detail?: string }>;
        const backendDetail = axErr.response?.data?.detail;
        if (backendDetail) {
          setError(backendDetail);
          return;
        }
        if (axErr.code === "ERR_NETWORK") {
          setError("Не удалось подключиться к API (http://localhost:8000). Проверь, что backend запущен.");
          return;
        }
        setError(axErr.message || "Не удалось авторизоваться.");
      }
    };
    if (tg.isReady && !user) {
      void fetchUser();
    }
  }, [api, tg.initData, tg.isReady, user, devTelegramId]);

  const renderContent = () => {
    if (!tg.isReady) {
      return <p className="text-sm text-slate-300 px-2">Инициализация Mini App...</p>;
    }

    if (error) {
      return (
        <p className="text-sm text-red-300 px-2">
          {error}
        </p>
      );
    }

    if (!user) {
      return <p className="text-sm text-slate-300 px-2">Авторизация...</p>;
    }

    switch (tab) {
      case "templates":
        return <TemplatesView api={api} />;
      case "metrics":
        return <MetricsView api={api} />;
      case "calendar":
      default:
        return <CalendarView api={api} />;
    }
  };

  const firstName = tg.user?.first_name ?? "";

  return (
    <div className="min-h-screen flex flex-col max-w-md mx-auto">
      <header className="px-4 pt-3 pb-2 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Тренировочный дневник</h1>
          <p className="text-xs text-slate-300">
            {firstName ? `Привет, ${firstName}!` : "Фиксируй тренировки и прогресс."}
          </p>
          {import.meta.env.DEV && !tg.initData && devTelegramId && (
            <p className="text-[11px] text-slate-400 mt-1">
              Dev mode: X-Dev-Telegram-Id={devTelegramId}
            </p>
          )}
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-3 pb-20 space-y-4">
        {renderContent()}
      </main>

      <nav className="fixed bottom-0 left-0 right-0 bg-tgSurface/95 border-t border-slate-800">
        <div className="max-w-md mx-auto flex">
          <button
            type="button"
            className={`flex-1 py-3 text-xs ${
              tab === "calendar" ? "text-tgAccent font-semibold" : "text-slate-300"
            }`}
            onClick={() => setTab("calendar")}
          >
            Календарь
          </button>
          <button
            type="button"
            className={`flex-1 py-3 text-xs ${
              tab === "templates" ? "text-tgAccent font-semibold" : "text-slate-300"
            }`}
            onClick={() => setTab("templates")}
          >
            Шаблоны
          </button>
          <button
            type="button"
            className={`flex-1 py-3 text-xs ${
              tab === "metrics" ? "text-tgAccent font-semibold" : "text-slate-300"
            }`}
            onClick={() => setTab("metrics")}
          >
            Метрики
          </button>
        </div>
      </nav>
    </div>
  );
};
