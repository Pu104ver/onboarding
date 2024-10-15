import {Link} from 'react-router-dom';

import styles from './EmployeesTableWithPools.module.scss';
import {SkipButton} from './SkipButton';

import {ColumnsData, ICurators, IEmployeesItem} from '@/app/types/Employee';
import StatusItem from '@/shared/ui/StatusItem';
import Table from '@/widgets/Table';

interface IEmployeesTableProps {
  employees_list?: IEmployeesItem[] | ICurators[];
}

export const EmployeesTableWithPolls = ({employees_list}: IEmployeesTableProps) => {
  const employeesColumns: ColumnsData<IEmployeesItem>[] = [
    {
      title: 'ФИО сотрудника',
      key: 'full_name',
      render: (text, record) => (
        <Link to={`/onboarding/${record?.role}s/${record?.id}`}>{text}</Link>
      ),
    },
    {
      title: 'Этап онбординга',
      key: 'onboarding_status',
      render: (value, record) =>
        record?.onboarding_status?.poll_title || 'Не приступил к онбордингу',
    },
    {
      title: 'Статус заполнения',
      key: 'poll_status',
      render: (text, record) => <StatusItem text={record?.onboarding_status?.status} />,
    },
    {
      title: 'Пропустить опрос',
      key: 'skip_poll',
      align: 'center',
      render: (value, record) => (
        <div className={styles.skipBtnContainer}>
          <SkipButton record={record} />
        </div>
      ),
    },
  ];

  return (
    <div className={styles.employeesTableWithPools}>
      <Table columns={employeesColumns} dataSource={employees_list} />
    </div>
  );
};
