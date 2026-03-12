import { useEffect, useState } from "react";
import type { AxiosInstance } from "axios";

import type { WorkoutTemplate } from "../types/api";

interface TemplatesViewProps {
  api: AxiosInstance;
}

interface TemplateExerciseDraft {
  exercise_name: string;
  sets_default: number;
  reps_default: number;
  weight_default: number | null;
}

const emptyExerciseDraft = (): TemplateExerciseDraft => ({
  exercise_name: "",
  sets_default: 3,
  reps_default: 10,
  weight_default: null
});

export const TemplatesView: React.FC<TemplatesViewProps> = ({ api }) => {
  const [templates, setTemplates] = useState<WorkoutTemplate[]>([]);
  const [name, setName] = useState("");
  const [exerciseDraft, setExerciseDraft] = useState<TemplateExerciseDraft>(emptyExerciseDraft());
  const [draftExercises, setDraftExercises] = useState<TemplateExerciseDraft[]>([]);
  const [editingTemplateId, setEditingTemplateId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const { data } = await api.get<WorkoutTemplate[]>("/templates");
      setTemplates(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadTemplates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const addDraftExercise = () => {
    if (!exerciseDraft.exercise_name.trim()) return;
    setDraftExercises((prev) => [...prev, exerciseDraft]);
    setExerciseDraft(emptyExerciseDraft());
  };

  const removeDraftExercise = (index: number) => {
    setDraftExercises((prev) => prev.filter((_, i) => i !== index));
  };

  const createTemplate = async () => {
    if (!name.trim()) return;
    try {
      setLoading(true);
      await api.post("/templates", {
        name,
        exercises: draftExercises
      });
      setName("");
      setDraftExercises([]);
      await loadTemplates();
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (template: WorkoutTemplate) => {
    setEditingTemplateId(template.id);
    setName(template.name);
    setDraftExercises(
      template.exercises.map((ex) => ({
        exercise_name: ex.exercise_name,
        sets_default: ex.sets_default,
        reps_default: ex.reps_default,
        weight_default: ex.weight_default
      }))
    );
  };

  const cancelEdit = () => {
    setEditingTemplateId(null);
    setName("");
    setDraftExercises([]);
    setExerciseDraft(emptyExerciseDraft());
  };

  const saveTemplate = async () => {
    if (!name.trim()) return;
    try {
      setLoading(true);
      if (editingTemplateId === null) {
        await createTemplate();
        return;
      }
      await api.put(`/templates/${editingTemplateId}`, {
        name,
        exercises: draftExercises
      });
      await loadTemplates();
      cancelEdit();
    } finally {
      setLoading(false);
    }
  };

  const deleteTemplate = async (id: number) => {
    await api.delete(`/templates/${id}`);
    if (editingTemplateId === id) {
      cancelEdit();
    }
    await loadTemplates();
  };

  return (
    <div className="space-y-4">
      <div className="card space-y-3">
        <h2 className="text-base font-semibold">
          {editingTemplateId ? "Редактирование шаблона" : "Новый шаблон"}
        </h2>
        <input
          className="input"
          placeholder="Название тренировки"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

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
              value={exerciseDraft.sets_default}
              onChange={(e) =>
                setExerciseDraft((prev) => ({
                  ...prev,
                  sets_default: Number(e.target.value) || 1
                }))
              }
            />
            <input
              className="input"
              type="number"
              min={1}
              value={exerciseDraft.reps_default}
              onChange={(e) =>
                setExerciseDraft((prev) => ({
                  ...prev,
                  reps_default: Number(e.target.value) || 1
                }))
              }
            />
            <input
              className="input"
              type="number"
              min={0}
              step={0.5}
              placeholder="Вес"
              value={exerciseDraft.weight_default ?? ""}
              onChange={(e) =>
                setExerciseDraft((prev) => ({
                  ...prev,
                  weight_default: e.target.value === "" ? null : Number(e.target.value)
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
              <div key={`${ex.exercise_name}-${idx}`} className="flex items-center justify-between gap-2">
                <span>{ex.exercise_name}</span>
                <span className="shrink-0">
                  {ex.sets_default}x{ex.reps_default}
                  {ex.weight_default ? ` • ${ex.weight_default} кг` : ""}
                </span>
                <button
                  type="button"
                  className="text-red-400"
                  onClick={() => removeDraftExercise(idx)}
                >
                  Убрать
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          <button
            type="button"
            className="btn-primary flex-1"
            onClick={saveTemplate}
            disabled={loading}
          >
            {editingTemplateId ? "Сохранить изменения" : "Сохранить шаблон"}
          </button>
          {editingTemplateId && (
            <button type="button" className="btn-primary flex-1" onClick={cancelEdit}>
              Отмена
            </button>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <h2 className="text-base font-semibold px-1">Мои шаблоны</h2>
        {loading && templates.length === 0 ? (
          <p className="text-sm text-slate-400 px-1">Загрузка...</p>
        ) : templates.length === 0 ? (
          <p className="text-sm text-slate-400 px-1">Пока нет шаблонов.</p>
        ) : (
          <div className="space-y-2">
            {templates.map((tpl) => (
              <div key={tpl.id} className="card flex flex-col gap-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium text-sm">{tpl.name}</span>
                  <div className="flex gap-2 text-xs">
                    <button type="button" className="text-sky-300" onClick={() => startEdit(tpl)}>
                      Редактировать
                    </button>
                    <button
                      type="button"
                      className="text-red-400"
                      onClick={() => void deleteTemplate(tpl.id)}
                    >
                      Удалить
                    </button>
                  </div>
                </div>
                <div className="space-y-1 text-xs text-slate-300">
                  {tpl.exercises.map((ex) => (
                    <div key={ex.id} className="flex justify-between">
                      <span>{ex.exercise_name}</span>
                      <span>
                        {ex.sets_default}x{ex.reps_default}
                        {ex.weight_default ? ` • ${ex.weight_default} кг` : ""}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
