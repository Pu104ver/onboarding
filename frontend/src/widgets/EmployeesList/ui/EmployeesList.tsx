import styles from './EmployeesList.module.scss';

import {IEmployeesItem} from '@/app/types/Employee';
import {EmployeeAnswersTable} from '@/features/PullsOperations';
import {EmployeesTableWithPolls} from '@/pages/CuratorPage/ui/EmployeesTableWithPolls';
import Collapse from '@/shared/ui/Collapse';

interface IEmployeesListProps {
  employees_list?: IEmployeesItem[] | null;
  isForEmployee?: boolean;
  employeeId?: string | number;
}

const filteredEmployeesList = (
  employeeId: IEmployeesListProps['employeeId'],
  employees_list?: IEmployeesListProps['employees_list'],
) => employees_list?.filter(employee => employee.id === employeeId) || [];

const EmployeesList = ({employees_list, employeeId, isForEmployee}: IEmployeesListProps) => {
  return (
    <ul className={styles.employeesList}>
      {employees_list?.map(({full_name, id}) => (
        <li key={id}>
          <Collapse isRevert title={full_name} defaultHidden={true}>
            {employees_list && (
              <EmployeesTableWithPolls employees_list={filteredEmployeesList(id, employees_list)} />
            )}

            <EmployeeAnswersTable
              id={(isForEmployee ? id : employeeId) || ''}
              target_employee_id={isForEmployee ? employeeId : id}
            />
          </Collapse>
        </li>
      ))}
    </ul>
  );
};

export default EmployeesList;
