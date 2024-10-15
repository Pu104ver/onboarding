import {IEmployeesItem} from '@/app/types/Employee';

export const getTargetEmployees = (employees?: IEmployeesItem[]) =>
  employees?.map(employee => employee.id) || [];
