export interface IProject {
  id: number;
  created_at: Date | string;
  created_by: string | null;
  date_end: Date | string;
  date_start: Date | string;
  is_deleted: boolean;
  name: string;
  updated_at: Date | null;
  updated_by: string | null;
}
