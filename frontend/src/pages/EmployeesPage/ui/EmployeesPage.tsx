import {Link} from 'react-router-dom';

import {Fragment, useEffect, useMemo, useState} from 'react';
import {Helmet} from 'react-helmet';

import styles from './EmployeesPage.module.scss';

import {useAppDispatch, useAppSelector} from '@/app/store/hooks';
import {getIsOpenedPageFilters} from '@/app/store/selectors';
import {handleFilters} from '@/app/store/slices/filters';
import {ColumnsData, EmployeeDataType} from '@/app/types/Employee';
import {userSelector} from '@/entities/User/model/selectors/GetUser';
import NewEmployeeForm from '@/features/CreateNewEmployee';
import TokenForm from '@/features/CreateNewEmployee/ui/TokenForm/TokenForm';
import {useGetEmployees} from '@/features/EmployeesOperations/model/EmployeesApi';
import {useGetProjects} from '@/features/Projects/model/Projects';
import FunnelIcon from '@/shared/assets/funnel.svg?react';
import PlusIcon from '@/shared/assets/plus.svg?react';
import {archivedFilters} from '@/shared/const/filters';
import {statusObjects} from '@/shared/const/StatusItemsConst';
import {convertToSelectOptions} from '@/shared/helpers/convertToSelectOptions';
import {declOfNum} from '@/shared/helpers/declOfNum';
import {isMaxCountHelper} from '@/shared/helpers/isMaxCountHelper';
import {useQueryParams} from '@/shared/hooks/useQueryParams.hook';
import Button from '@/shared/ui/Button';
import Dropdown from '@/shared/ui/Dropdown';
import Modal from '@/shared/ui/Modal';
import StatusItem from '@/shared/ui/StatusItem';
import Table from '@/widgets/Table';
import {TableSearchFilters} from '@/widgets/TableSearchFilters';

export default function EmployeesPage() {
  const [page, setPage] = useState(1);
  const {queryParams} = useQueryParams();

  const [getEmployees, {data: employees, isFetching}] = useGetEmployees();
  const {data: projects} = useGetProjects();

  useEffect(() => {
    queryParams.length > 1 && void getEmployees({page, queryParams});
  }, [page, queryParams]);

  const [isOpenedModalNewEmployee, setIsOpenedModalNewEmployee] = useState(false);
  const [isOpenedModalToken, setIsOpenedModalToken] = useState(false);
  const [token, setToken] = useState('');

  const dispatch = useAppDispatch();
  const {role} = useAppSelector(userSelector);
  const isOpened = useAppSelector(getIsOpenedPageFilters('employeesPage'));

  const handleModalToken = () => {
    setIsOpenedModalToken(prev => !prev);
  };

  const handleModalNewEmployee = () => {
    setIsOpenedModalNewEmployee(prev => !prev);
  };

  const handleFilterBtn = () => {
    dispatch(handleFilters('employeesPage'));
  };

  const employeesColumns: ColumnsData<EmployeeDataType>[] = useMemo(
    () => [
      {
        title: 'ФИО сотрудника',
        key: 'full_name',
        render: (text, record) => <Link to={`/onboarding/employees/${record?.id}`}>{text}</Link>,
      },
      {
        title: 'Проект',
        key: 'projects',
        filter: {
          options: convertToSelectOptions(projects),
        },
        render: (text, record) => {
          const projectsArr = record?.projects_list?.map(({name, id}) => ({name, id})) || [];

          return (
            <Dropdown
              content={
                projectsArr.length > 0
                  ? projectsArr.map(({name, id}) => <Fragment key={id}>{name}</Fragment>)
                  : 'Проекты не назначены'
              }>
              {projectsArr.length}{' '}
              {declOfNum(projectsArr.length, ['проект', 'проекта', 'проектов'])}
            </Dropdown>
          );
        },
      },

      {
        title: 'Куратор',
        key: 'curators',
        render: (text, record) => {
          const curatorsArr =
            record?.curators_list?.map(({full_name, id}) => ({full_name, curatorId: id})) || [];

          return (
            <Dropdown
              content={
                curatorsArr.length > 0
                  ? curatorsArr.map(({full_name, curatorId}) => (
                      <Link to={`/onboarding/curators/${curatorId}`} key={curatorId}>
                        {full_name}
                      </Link>
                    ))
                  : 'Кураторы не назначены'
              }>
              {curatorsArr.length}{' '}
              {declOfNum(curatorsArr.length, ['куратор', 'куратора', 'кураторов'])}
            </Dropdown>
          );
        },
      },
      {
        title: 'Этап онбординга',
        key: 'onboarding_status',
        render: (value, record) => record?.onboarding_status?.poll_title,
      },
      {
        title: 'Статус риска',
        key: 'risk_status_display',
      },
      {
        title: 'Статус опроса',
        key: 'poll_status',
        filter: {
          options: [
            ...Object.entries(statusObjects).map(([key, value]) => ({
              label: value.text,
              value: key,
            })),
          ],
        },
        render: (text, record) => <StatusItem text={record?.onboarding_status?.status} />,
      },
      {
        key: 'is_archived',
        filter: {
          options: archivedFilters,
          initialValue: 'false',
          placeholder: 'Архивирован',
        },
      },
    ],
    [projects],
  );

  const columnsWithFilters = useMemo(
    () => employeesColumns.filter(column => column.filter),
    [employeesColumns],
  );

  return (
    <>
      <Helmet title="Onboarding | Сотрудники" />

      <section className="section">
        <div className={styles.EmployeesHeader}>
          <h2>Сотрудники</h2>

          <div className={styles.EmployeesOptionals}>
            <Button onClick={handleFilterBtn} pressed={isOpened}>
              <FunnelIcon />
              Фильтры
            </Button>
          </div>
        </div>

        <TableSearchFilters
          columnsWithFilters={columnsWithFilters}
          isOpened={isOpened}
          searchPlaceholder="Поиск по сотрудникам"
          searchField="full_name">
          {(role === 'admin' || role === 'hr') && (
            <Button onClick={handleModalNewEmployee} variant="primary">
              <PlusIcon />
              Добавить сотрудника
            </Button>
          )}
        </TableSearchFilters>

        <Table
          isMaxCount={isMaxCountHelper(page, employees)}
          isFetching={isFetching}
          setPage={setPage}
          columns={employeesColumns}
          dataSource={employees?.results}
        />
      </section>

      <Modal
        title="Новый сотрудник"
        isOpened={isOpenedModalNewEmployee}
        onClose={handleModalNewEmployee}>
        <NewEmployeeForm
          setToken={setToken}
          openTokenModal={handleModalToken}
          closeModal={handleModalNewEmployee}
          role="employee"
        />
      </Modal>

      <Modal title="Токен сотрудника" isOpened={isOpenedModalToken} onClose={handleModalToken}>
        <TokenForm access_token={token} />
      </Modal>
    </>
  );
}
