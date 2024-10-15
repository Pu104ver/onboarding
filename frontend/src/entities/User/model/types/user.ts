import {ILoginResponse} from '@/app/types/Login.type';

export interface User extends Omit<ILoginResponse, 'token' | 'message'> {}

export interface UserSchema {
  id: number | null;
  user: User | null;
  description: string | null;
  date_of_dismission: Date | null;
  date_of_employment: Date | null;
  full_name: string | null;
  projects: string[];
  role: string | null;
  telegram_nickname: string | null;
}
