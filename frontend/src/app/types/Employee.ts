import {ReactNode} from 'react';

import {TRole} from './Roles.type';

import {TSelectOption} from '@/app/types/Select';
import {statusObjectsKeyType} from '@/shared/const/StatusItemsConst';

export interface ITableFilter {
  options?: TSelectOption[];
  initialValue?: string;
  placeholder?: string;
  isMulti?: boolean;
}

// Мы описываем здесь колонки для таблицы. Для каждой колонки мы можем указать ее:
// title - название;
// key - он нужен для уникальных ключей для map и также этот key используется, чтобы обратиться к полю в объекте с бека (пример будет ниже);
// align - выравнивание данных в таблице по левому/центральному/правому краю;
// sorter - заготовка для сортировки по убыванию/возрастанию данных;
// filter - для фильтров таблиц, которые вынесены в url и которые отображаются над таблицей с данными;
// render - метод, благодаря которому можно либо вывести данные с бека, никак их не обработав (например если нам нужно вывести просто стрингу), либо кастомизировать отрисовку данных в таблице благодаря второму значению, которое прокидывается в этот метод - record

// Пример данных с бека и их отрисовка в таблице
// TODO: доделать пример для отображения...
export interface ColumnsData<RecordType> {
  title?: string;
  key: string;
  align?: 'left' | 'center' | ' right';
  sorter?: (a: RecordType, b: RecordType) => void;
  filter?: ITableFilter;
  render?: (value: string, record?: RecordType) => ReactNode;
}

export interface ICurators {
  id: number;
  curator: number;
  employee: number;
  full_name?: string;
}

export interface IEmployee {
  id: number;
  employeeName: string;
  projects?: string[];
  curator: string;
  stage: string;
  status: statusObjectsKeyType;
  full_name: string;
}

export interface ICurator extends Omit<IEmployee, 'curator'> {
  employees: string;
}

export type TimeOfDay = 'morning' | 'evening';

interface Project {
  id: number;
  name: string;
  project: number;
  employee: number;

  is_deleted: boolean;

  created_at: string;
  created_by: string | null;

  date_end: Date;
  date_start: Date;

  updated_at: string;
  updated_by: string | null;
}

export interface IPoll {
  id: number;
  title: string;
  message: string;
  time_of_day: string;
  intended_for: string;
  questions: QuestionType[];
  poll_type: string;
  poll_number: number;
  related_object: {
    id: number;
    type: string;
    name: string;
  };
}

export interface StatusItem {
  id: number;
  employee_id: number;
  employee: string;

  target_employee_id: string | null;
  target_employee: string | null;
  poll_status_display: string;
  poll_title: string;

  status: string;

  started_at: string | null;
  completed_at: string | null;
  date_planned_at: string | null;
  time_planned_at: string;
}

interface Answer {
  id: number;
  employee_id: number;
  employee: string;
  target_employee_id: string | null;
  target_employee: string | null;
  question: number;
  answer: string;
  created_at: string;
  requires_attention: boolean;
}

interface QuestionType {
  answers: Answer[];
  id: number;
  text: string;
  question_type: string;
  show: boolean;
}

export interface IUserDetails {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  username: string;
}

export interface IEmployeesItem {
  id: number;
  full_name: string;
  role: TRole;
  telegram_nickname: string;
  onboarding_status: StatusItem | null;

  user_details: IUserDetails;

  date_meeting: string | null;

  risk_status: string;
  risk_status_display: string;

  status: string;
  status_display: string;
}

export type EmployeeDataType = {
  id: number;
  full_name: string;
  telegram_user_id: number | null;
  user: number;
  telegram_nickname: string;
  onboarding_status: StatusItem | null;
  lastAnswer: string;
  description?: string;
  date_meeting: Date | null;

  is_curator_employee: boolean;
  is_archived: boolean;
  is_deleted: boolean;

  role: TRole;
  status?: string;

  projects_list: Project[] | null;
  curators_list: IEmployeesItem[] | null;
  employees_list?: IEmployeesItem[];

  date_of_employment: string;
  date_of_dismission: string | null;
  created_by: number;
  created_at: string;
  updated_by: number;

  events: {
    id: number;
    title: string;
    time: string;
    status: string;
  }[];
};

export interface EmployeesPageRequest {
  offset: number;
  queryParams: string;
}

export type TEmployeeByIdRequest = string | number | null | undefined;

export interface CommentResponse {
  id: TEmployeeByIdRequest;
  author: TEmployeeByIdRequest;
  author_fullname: string;
  employee: TEmployeeByIdRequest;
  text: string;
  created_at: Date;
  updated_at: Date;
  updated_by: Date | null;
}
export interface CommentRequest {
  author: TEmployeeByIdRequest;
  employee: TEmployeeByIdRequest;
  text: string;
}

export type EmployeeDataTypeRequest = Omit<Partial<EmployeeDataType>, 'id'> & {
  id: TEmployeeByIdRequest;
};

export interface ICompletePollRequest {
  pollId?: string | number;
  employeeId: TEmployeeByIdRequest;
}

export interface ILaunchPollRequest {
  employee: TEmployeeByIdRequest;
  target_employee?: number;
  poll: number;
  date_planned_at: string;
}

export type TPollType = 'onboarding' | 'offboarding' | 'feedback';

export interface IILaunchPollForm extends Omit<ILaunchPollRequest, 'poll' | 'target_employee'> {
  poll?: TSelectOption | null;
  target_employee?: TSelectOption | null;
}

export interface IAvailablePollsRequest {
  poll_type: TPollType;
  employee: TEmployeeByIdRequest;
  intended_for: TRole;
}

export interface IAvailablePollsForm {
  poll_type: TSelectOption;
  employee: TEmployeeByIdRequest;
  intended_for: TRole;
}

export interface IExportAnswersRequest {
  employee: string | number;
  target_employee?: TEmployeeByIdRequest[];
  filename: string;
}
