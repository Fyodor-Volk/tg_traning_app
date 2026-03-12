import { useEffect, useState } from "react";
import type { AxiosInstance } from "axios";

import type { CalendarDaySessions, SessionExercise, WorkoutTemplate } from "../types/api";

interface CalendarViewProps {
  api: AxiosInstance;
}

interface NewSessionExercise {
  exercise_name: string;
  sets: number;
  reps: number;
  weight: number | null;
  is_completed: boolean;
}

const emptyExerciseDraft = (): NewSessionExercise => ({
  exercise_name: "",
  sets: 3,
  reps: 10,
  weight: null,
  is_completed: false
});

export const CalendarView: React.FC<CalendarViewProps> = ({ api }) => {
  const [selectedDate, setSelectedDate] = useState<string>(() => new Date().toISOString().slice(0, 10));
  const [dayData, setDayData] = useState<CalendarDaySessions | null>(null);
  const [templates, setTemplates] = useState<WorkoutTemplate[]>([]);
  const [templateToAddId, setTemplateToAddId] = useState<string>("");
  const [exerciseDraft, setExerciseDraft] = useState<NewSessionExercise>(emptyExerciseDraft());
  const [draftExercises, setDraftExercises] = useState<NewSessionExercise[]>([]);
  const [notes, setNotes] = useState("");
  const [sessionNotes, setSessionNotes] = useState<Record<number, string>>({});
  const [exerciseEdits, setExerciseEdits] = useState<Record<number, NewSessionExercise>>({});
  const [sessionExerciseDrafts, setSessionExerciseDrafts] = useState<Record<number, NewSessionExercise>>({});
  const [loading, setLoading] = useState(false);

  const loadTemplates = async () => {
    const { data } = await api.get<WorkoutTemplate[]>("/templates");
    setTemplates(data);
  };

  const hydrateSessionDrafts = (calendar: CalendarDaySessions) => {
    const notesMap: Record<number, string> = {};
    const exMap: Record<number, NewSessionExercise> = {};
    const addMap: Record<number, NewSessionExercise> = {};

    calendar.sessions.forEach((session) => {
      notesMap[session.id] = session.notes ?? "";
      addMap[session.id] = emptyExerciseDraft();
      session.exercises.forEach((ex) => {
        exMap[ex.id] = {
          exercise_name: ex.exercise_name,
          sets: ex.sets,
          reps: ex.reps,
          weight: ex.weight,
          is_completed: ex.is_completed
        };
      });
    });

    setSessionNotes(notesMap);
    setExerciseEdits(exMap);
    setSessionExerciseDrafts(addMap);
  };

  const loadDay = async (dateStr: string) => {
    try {
      setLoading(true);
      const { data } = await api.get<CalendarDaySessions>(`/calendar/${dateStr}`);
      setDayData(data);
      hydrateSessionDrafts(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void Promise.all([loadTemplates(), loadDay(selectedDate)]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDateChange = (value: string) => {
    setSelectedDate(value);
    void loadDay(value);
  };

  const addTemplateToWorkout = (templateIdValue: string) => {
    if (!templateIdValue) return;
    const templateId = Number(templateIdValue);
    const template = templates.find((tpl) => tpl.id === templateId);
    if (!template) return;

    const exercisesFromTemplate: NewSessionExercise[] = template.exercises.map((ex) => ({
      exercise_name: ex.exercise_name,
      sets: ex.sets_default,
      reps: ex.reps_default,
      weight: ex.weight_default,
      is_completed: false
    }));

    setDraftExercises((prev) => [...prev, ...exercisesFromTemplate]);
    setTemplateToAddId("");
  };

  const addDraftExercise = () => {
    if (!exerciseDraft.exercise_name.trim()) return;
    setDraftExercises((prev) => [...prev, exerciseDraft]);
    setExerciseDraft(emptyExerciseDraft());
  };

  const createSession = async () => {
    if (!selectedDate) return;
    try {
      setLoading(true);
      await api.post("/sessions", {
        date: selectedDate,
        notes: notes || null,
        exercises: draftExercises
      });
      setDraftExercises([]);
      setExerciseDraft(emptyExerciseDraft());
      setTemplateToAddId("");
      setNotes("");
      await loadDay(selectedDate);
    } finally {
      setLoading(false);
    }
  };

  const updateSession = async (sessionId: number) => {
    await api.put(`/sessions/${sessionId}`, {
      notes: sessionNotes[sessionId] ?? ""
    });
    await loadDay(selectedDate);
  };

  const deleteSession = async (sessionId: number) => {
    await api.delete(`/sessions/${sessionId}`);
    await loadDay(selectedDate);
  };

  const updateSessionExercise = async (sessionId: number, exerciseId: number) => {
    const payload = exerciseEdits[exerciseId];
    if (!payload) return;
    await api.put(`/sessions/${sessionId}/exercises/${exerciseId}`, payload);
    await loadDay(selectedDate);
  };

  const toggleExerciseDone = async (sessionId: number, exercise: SessionExercise) => {
    await api.put(`/sessions/${sessionId}/exercises/${exercise.id}`, {
      is_completed: !exercise.is_completed
    });
    await loadDay(selectedDate);
  };

  const addExerciseToSession = async (sessionId: number) => {
    const draft = sessionExerciseDrafts[sessionId];
    if (!draft || !draft.exercise_name.trim()) return;

    await api.post(`/sessions/${sessionId}/exercises`, draft);
    await loadDay(selectedDate);
  };

  const deleteSessionExercise = async (sessionId: number, exerciseId: number) => {
    await api.delete(`/sessions/${sessionId}/exercises/${exerciseId}`);
    await loadDay(selectedDate);
  };

  const getTemplateName = (id: number): string => templates.find((tpl) => tpl.id === id)?.name ?? `#${id}`;

  return (
    <div className="space-y-4">
      <div className="card space-y-3">
        <div className="flex items-center justify-between gap-2">
          <span className="text-sm font-semibold">Дата</span>
          <input
            type="date"
            className="input max-w-[140px]"
            value={selectedDate}
            onChange={(e) => handleDateChange(e.target.value)}
          />
        </div>

        <textarea
          className="input min-h-[60px]"
          placeholder="Заметки о тренировке"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />

        <div className="space-y-2 text-xs">
          <p className="text-slate-300">Выбрать из шаблона</p>
          <div className="flex gap-2">
            <select
              className="input"
              value={templateToAddId}
              onChange={(e) => setTemplateToAddId(e.target.value)}
            >
              <option value="">Выбрать из шаблона</option>
              {templates.map((tpl) => (
                <option key={tpl.id} value={tpl.id}>
                  {tpl.name}
                </option>
              ))}
            </select>
            <button
              type="button"
              className="btn-primary shrink-0"
              onClick={() => addTemplateToWorkout(templateToAddId)}
              disabled={!templateToAddId}
            >
              Добавить
            </button>
          </div>
        </div>

        <div className="space-y-2">
          <input
            className="input"
            placeholder="Упражнение"
            value={exerciseDraft.exercise_name}
            onChange={(e) =>
              setExerciseDraft((prev) => ({ ...prev, exercise_name: e.target.value }))
            }
          />
          <div className="flex gap-2">
            <input
              className="input"
              type="number"
              min={1}
              value={exerciseDraft.sets}
              onChange={(e) =>
                setExerciseDraft((prev) => ({
                  ...prev,
                  sets: Number(e.target.value) || 1
                }))
              }
            />
            <input
              className="input"
              type="number"
              min={1}
              value={exerciseDraft.reps}
              onChange={(e) =>
                setExerciseDraft((prev) => ({
                  ...prev,
                  reps: Number(e.target.value) || 1
                }))
              }
            />
            <input
              className="input"
              type="number"
              min={0}
              step={0.5}
              placeholder="Вес"
              value={exerciseDraft.weight ?? ""}
              onChange={(e) =>
                setExerciseDraft((prev) => ({
                  ...prev,
                  weight: e.target.value === "" ? null : Number(e.target.value)
                }))
              }
            />
          </div>
          <button type="button" className="btn-primary w-full" onClick={addDraftExercise}>
            Добавить упражнение
          </button>
        </div>

        {draftExercises.length > 0 && (
          <div className="space-y-1 text-xs text-slate-300">
            {draftExercises.map((ex, idx) => (
              <div key={`${ex.exercise_name}-${idx}`} className="flex justify-between">
                <span>{ex.exercise_name}</span>
                <span>
                  {ex.sets}x{ex.reps}
                  {ex.weight ? ` • ${ex.weight} кг` : ""}
                </span>
              </div>
            ))}
          </div>
        )}

        <button
          type="button"
          className="btn-primary w-full mt-2"
          onClick={createSession}
          disabled={loading}
        >
          Сохранить сессию
        </button>
      </div>

      <div className="space-y-2">
        <h2 className="text-base font-semibold px-1">Тренировки за день</h2>
        {loading && !dayData ? (
          <p className="text-sm text-slate-400 px-1">Загрузка...</p>
        ) : !dayData || dayData.sessions.length === 0 ? (
          <p className="text-sm text-slate-400 px-1">Тренировок пока нет.</p>
        ) : (
          <div className="space-y-2">
            {dayData.sessions.map((session) => (
              <div key={session.id} className="card space-y-2">
                <div className="text-xs text-slate-300 space-y-1">
                  <div className="flex justify-between">
                    <span>{new Date(session.created_at).toLocaleTimeString()}</span>
                    <button
                      type="button"
                      className="text-red-400"
                      onClick={() => void deleteSession(session.id)}
                    >
                      Удалить сессию
                    </button>
                  </div>
                  {session.template_ids.length > 0 && (
                    <p>Шаблоны: {session.template_ids.map((id) => getTemplateName(id)).join(", ")}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <textarea
                    className="input min-h-[56px]"
                    value={sessionNotes[session.id] ?? ""}
                    onChange={(e) =>
                      setSessionNotes((prev) => ({
                        ...prev,
                        [session.id]: e.target.value
                      }))
                    }
                  />
                  <button
                    type="button"
                    className="btn-primary w-full"
                    onClick={() => void updateSession(session.id)}
                  >
                    Сохранить заметки
                  </button>
                </div>

                <div className="space-y-2 text-xs text-slate-200">
                  {session.exercises.map((ex) => {
                    const edit = exerciseEdits[ex.id] ?? {
                      exercise_name: ex.exercise_name,
                      sets: ex.sets,
                      reps: ex.reps,
                      weight: ex.weight,
                      is_completed: ex.is_completed
                    };

                    return (
                      <div key={ex.id} className="rounded-lg border border-slate-700 p-2 space-y-2">
                        <div className="flex items-center justify-between gap-2">
                          <label className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={ex.is_completed}
                              onChange={() => void toggleExerciseDone(session.id, ex)}
                            />
                            <span className={ex.is_completed ? "line-through text-slate-400" : ""}>
                              Выполнено
                            </span>
                          </label>
                          <button
                            type="button"
                            className="text-red-400"
                            onClick={() => void deleteSessionExercise(session.id, ex.id)}
                          >
                            Удалить
                          </button>
                        </div>
                        <input
                          className="input"
                          value={edit.exercise_name}
                          onChange={(e) =>
                            setExerciseEdits((prev) => ({
                              ...prev,
                              [ex.id]: { ...edit, exercise_name: e.target.value }
                            }))
                          }
                        />
                        <div className="grid grid-cols-3 gap-2">
                          <input
                            className="input"
                            type="number"
                            min={1}
                            value={edit.sets}
                            onChange={(e) =>
                              setExerciseEdits((prev) => ({
                                ...prev,
                                [ex.id]: { ...edit, sets: Number(e.target.value) || 1 }
                              }))
                            }
                          />
                          <input
                            className="input"
                            type="number"
                            min={1}
                            value={edit.reps}
                            onChange={(e) =>
                              setExerciseEdits((prev) => ({
                                ...prev,
                                [ex.id]: { ...edit, reps: Number(e.target.value) || 1 }
                              }))
                            }
                          />
                          <input
                            className="input"
                            type="number"
                            min={0}
                            step={0.5}
                            value={edit.weight ?? ""}
                            onChange={(e) =>
                              setExerciseEdits((prev) => ({
                                ...prev,
                                [ex.id]: {
                                  ...edit,
                                  weight: e.target.value === "" ? null : Number(e.target.value)
                                }
                              }))
                            }
                          />
                        </div>
                        <button
                          type="button"
                          className="btn-primary w-full"
                          onClick={() => void updateSessionExercise(session.id, ex.id)}
                        >
                          Сохранить упражнение
                        </button>
                      </div>
                    );
                  })}
                </div>

                <div className="space-y-2 rounded-lg border border-slate-700 p-2">
                  <p className="text-xs text-slate-300">Добавить упражнение в сессию</p>
                  <input
                    className="input"
                    placeholder="Название"
                    value={sessionExerciseDrafts[session.id]?.exercise_name ?? ""}
                    onChange={(e) =>
                      setSessionExerciseDrafts((prev) => ({
                        ...prev,
                        [session.id]: {
                          ...(prev[session.id] ?? emptyExerciseDraft()),
                          exercise_name: e.target.value
                        }
                      }))
                    }
                  />
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      className="input"
                      type="number"
                      min={1}
                      value={sessionExerciseDrafts[session.id]?.sets ?? 3}
                      onChange={(e) =>
                        setSessionExerciseDrafts((prev) => ({
                          ...prev,
                          [session.id]: {
                            ...(prev[session.id] ?? emptyExerciseDraft()),
                            sets: Number(e.target.value) || 1
                          }
                        }))
                      }
                    />
                    <input
                      className="input"
                      type="number"
                      min={1}
                      value={sessionExerciseDrafts[session.id]?.reps ?? 10}
                      onChange={(e) =>
                        setSessionExerciseDrafts((prev) => ({
                          ...prev,
                          [session.id]: {
                            ...(prev[session.id] ?? emptyExerciseDraft()),
                            reps: Number(e.target.value) || 1
                          }
                        }))
                      }
                    />
                    <input
                      className="input"
                      type="number"
                      min={0}
                      step={0.5}
                      value={sessionExerciseDrafts[session.id]?.weight ?? ""}
                      onChange={(e) =>
                        setSessionExerciseDrafts((prev) => ({
                          ...prev,
                          [session.id]: {
                            ...(prev[session.id] ?? emptyExerciseDraft()),
                            weight: e.target.value === "" ? null : Number(e.target.value)
                          }
                        }))
                      }
                    />
                  </div>
                  <button
                    type="button"
                    className="btn-primary w-full"
                    onClick={() => void addExerciseToSession(session.id)}
                  >
                    Добавить в сессию
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
