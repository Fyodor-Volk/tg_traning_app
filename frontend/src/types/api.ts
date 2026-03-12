export interface User {
  id: number;
  telegram_id: number;
  created_at: string;
}

export interface TemplateExercise {
  id: number;
  exercise_name: string;
  sets_default: number;
  reps_default: number;
  weight_default: number | null;
}

export interface WorkoutTemplate {
  id: number;
  name: string;
  created_at: string;
  exercises: TemplateExercise[];
}

export interface SessionExercise {
  id: number;
  exercise_name: string;
  sets: number;
  reps: number;
  weight: number | null;
  is_completed: boolean;
}

export interface WorkoutSession {
  id: number;
  user_id: number;
  date: string;
  template_id: number | null;
  template_ids: number[];
  notes: string | null;
  created_at: string;
  exercises: SessionExercise[];
}

export interface CalendarDaySessions {
  date: string;
  sessions: WorkoutSession[];
}

export interface BodyMetric {
  id: number;
  user_id: number;
  date: string;
  weight: number | null;
  height: number | null;
  chest: number | null;
  waist: number | null;
  hips: number | null;
  biceps: number | null;
  notes: string | null;
}
