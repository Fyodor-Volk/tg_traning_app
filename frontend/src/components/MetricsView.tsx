import { useEffect, useState } from "react";
import type { AxiosError, AxiosInstance } from "axios";

import type { BodyMetric } from "../types/api";

interface MetricsViewProps {
  api: AxiosInstance;
}

export const MetricsView: React.FC<MetricsViewProps> = ({ api }) => {
  const [date, setDate] = useState<string>(() => new Date().toISOString().slice(0, 10));
  const [metricId, setMetricId] = useState<number | null>(null);
  const [weight, setWeight] = useState<string>("");
  const [height, setHeight] = useState<string>("");
  const [chest, setChest] = useState<string>("");
  const [waist, setWaist] = useState<string>("");
  const [hips, setHips] = useState<string>("");
  const [biceps, setBiceps] = useState<string>("");
  const [notes, setNotes] = useState("");
  const [history, setHistory] = useState<BodyMetric[]>([]);
  const [loading, setLoading] = useState(false);

  const clearForm = () => {
    setMetricId(null);
    setWeight("");
    setHeight("");
    setChest("");
    setWaist("");
    setHips("");
    setBiceps("");
    setNotes("");
  };

  const applyMetricToForm = (metric: BodyMetric) => {
    setMetricId(metric.id);
    setWeight(metric.weight?.toString() ?? "");
    setHeight(metric.height?.toString() ?? "");
    setChest(metric.chest?.toString() ?? "");
    setWaist(metric.waist?.toString() ?? "");
    setHips(metric.hips?.toString() ?? "");
    setBiceps(metric.biceps?.toString() ?? "");
    setNotes(metric.notes ?? "");
  };

  const loadHistory = async () => {
    const { data } = await api.get<BodyMetric[]>("/metrics/history");
    setHistory(data);
  };

  const loadMetricForDate = async (dateValue: string) => {
    try {
      const { data } = await api.get<BodyMetric>(`/metrics/${dateValue}`);
      applyMetricToForm(data);
    } catch (err: unknown) {
      const axErr = err as AxiosError;
      if (axErr.response?.status === 404) {
        clearForm();
        return;
      }
      throw err;
    }
  };

  useEffect(() => {
    const bootstrap = async () => {
      try {
        setLoading(true);
        await Promise.all([loadHistory(), loadMetricForDate(date)]);
      } finally {
        setLoading(false);
      }
    };

    void bootstrap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const changeDate = async (value: string) => {
    setDate(value);
    try {
      setLoading(true);
      await loadMetricForDate(value);
    } finally {
      setLoading(false);
    }
  };

  const buildPayload = () => ({
    date,
    weight: weight === "" ? null : Number(weight),
    height: height === "" ? null : Number(height),
    chest: chest === "" ? null : Number(chest),
    waist: waist === "" ? null : Number(waist),
    hips: hips === "" ? null : Number(hips),
    biceps: biceps === "" ? null : Number(biceps),
    notes: notes || null
  });

  const submit = async () => {
    try {
      setLoading(true);
      if (metricId === null) {
        await api.post("/metrics", buildPayload());
      } else {
        await api.put(`/metrics/${metricId}`, buildPayload());
      }
      await Promise.all([loadHistory(), loadMetricForDate(date)]);
    } finally {
      setLoading(false);
    }
  };

  const remove = async () => {
    if (metricId === null) return;
    try {
      setLoading(true);
      await api.delete(`/metrics/${metricId}`);
      clearForm();
      await loadHistory();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="card space-y-3">
        <h2 className="text-base font-semibold">Параметры на дату</h2>
        <div className="flex gap-2 items-center">
          <span className="text-sm">Дата</span>
          <input
            type="date"
            className="input max-w-[160px]"
            value={date}
            onChange={(e) => void changeDate(e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <input
            className="input"
            type="number"
            placeholder="Вес (кг)"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
          />
          <input
            className="input"
            type="number"
            placeholder="Рост (см)"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
          />
          <input
            className="input"
            type="number"
            placeholder="Грудь (см)"
            value={chest}
            onChange={(e) => setChest(e.target.value)}
          />
          <input
            className="input"
            type="number"
            placeholder="Талия (см)"
            value={waist}
            onChange={(e) => setWaist(e.target.value)}
          />
          <input
            className="input"
            type="number"
            placeholder="Бедра (см)"
            value={hips}
            onChange={(e) => setHips(e.target.value)}
          />
          <input
            className="input"
            type="number"
            placeholder="Бицепс (см)"
            value={biceps}
            onChange={(e) => setBiceps(e.target.value)}
          />
        </div>
        <textarea
          className="input min-h-[60px]"
          placeholder="Заметки"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <div className="flex gap-2">
          <button type="button" className="btn-primary flex-1" onClick={submit} disabled={loading}>
            {metricId === null ? "Сохранить" : "Обновить"}
          </button>
          {metricId !== null && (
            <button type="button" className="btn-primary flex-1" onClick={remove} disabled={loading}>
              Удалить
            </button>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <h2 className="text-base font-semibold px-1">История</h2>
        {loading && history.length === 0 ? (
          <p className="text-sm text-slate-400 px-1">Загрузка...</p>
        ) : history.length === 0 ? (
          <p className="text-sm text-slate-400 px-1">Записей пока нет.</p>
        ) : (
          <div className="space-y-2">
            {history.map((m) => (
              <div key={m.id} className="card space-y-1 text-xs text-slate-200">
                <div className="flex justify-between text-slate-300">
                  <span>{m.date}</span>
                  {m.weight && <span>{m.weight} кг</span>}
                </div>
                <div className="grid grid-cols-2 gap-1">
                  {m.height && <span>Рост: {m.height} см</span>}
                  {m.chest && <span>Грудь: {m.chest} см</span>}
                  {m.waist && <span>Талия: {m.waist} см</span>}
                  {m.hips && <span>Бедра: {m.hips} см</span>}
                  {m.biceps && <span>Бицепс: {m.biceps} см</span>}
                </div>
                {m.notes && <p className="text-slate-300">{m.notes}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
