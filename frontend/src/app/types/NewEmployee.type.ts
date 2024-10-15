import {TRole} from './Roles.type';
import {TSelectMultiOption} from './Select';

export interface INewEmployeeForm {
  full_name: string;
  email: string;
  telegram_nickname: string;
  date_of_employment: Date | null;
  role: TRole;
  curators?: TSelectMultiOption;
  projects?: TSelectMultiOption;
}

export interface INewEmployeeRequest
  extends Omit<INewEmployeeForm, 'date_of_employment' | 'curators' | 'projects'> {
  date_of_employment: string | null;
  curators?: number[];
  projects?: number[];
}

export interface INewEmployeeResponse {
  uid: string;
  token: string;
  employee_id: number;
}
