import {TRole} from './Roles.type';

export interface ICuratorsResponse {
  created_at: Date | string;
  created_by: string | null;
  curators: string[];
  date_of_dismission: Date | string | null;
  date_of_employment: string;
  description: string | null;
  full_name: string;
  id: number;
  is_archived: boolean;
  is_deleted: boolean;
  onboarding_stage: null;
  onboarding_status: null;
  projects: string[];
  role: TRole;
  telegram_nickname: string;
  telegram_user_id: number | null;
  updated_at: Date | string;
  updated_by: string | null;
  user: number;
}
