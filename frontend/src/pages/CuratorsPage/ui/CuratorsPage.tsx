import {Link} from 'react-router-dom';

import {useMemo, useState} from 'react';
import {Helmet} from 'react-helmet';

import style from './CuratorsPage.module.scss';

import {useAppDispatch, useAppSelector} from '@/app/store/hooks';
import {getIsOpenedPageFilters} from '@/app/store/selectors';
import {handleOpenFilters, selectOffset} from '@/app/store/slices/filters';
import {ColumnsData, EmployeeDataType} from '@/app/types/Employee';
import {userSelector} from '@/entities/User/model/selectors/GetUser';
import NewEmployeeForm from '@/features/CreateNewEmployee';
import TokenForm from '@/features/CreateNewEmployee/ui/TokenForm/TokenForm';
import {useGetCurators} from '@/features/CuratorsOperations/model/CuratorsApi';
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

export default function CuratorsPage() {
  const offset = useAppSelector(selectOffset);
  const {queryParams, isOffsetReset} = useQueryParams();

  const {data: curators, isFetching} = useGetCurators(
    {offset, queryParams},
    {
      skip: !isOffsetReset,
    },
  );
  const {data: projects} = useGetProjects();

  const [isOpenedModalNewEmployee, setIsOpenedModalNewEmployee] = useState(false);
  const [isOpenedModalToken, setIsOpenedModalToken] = useState(false);
  const [token, setToken] = useState('');

  const dispatch = useAppDispatch();
  const isOpened = useAppSelector(getIsOpenedPageFilters);

  const {role} = useAppSelector(userSelector);

  const handleFilterBtn = () => {
    dispatch(handleOpenFilters());
  };

  const handleModalNewEmployee = () => {
    setIsOpenedModalNewEmployee(prev => !prev);
  };

  const handleModalToken = () => {
    setIsOpenedModalToken(prev => !prev);
  };

  const curatorsColumns: ColumnsData<EmployeeDataType>[] = useMemo(
    () => [
      {
        title: 'ФИО куратора',
        key: 'full_name',
        render: (text, record) => <Link to={`/onboarding/curators/${record?.id}`}>{text}</Link>,
      },
      {
        title: 'Проект',
        key: 'projects',
        filter: {
          options: convertToSelectOptions(projects),
          isMulti: true,
        },
        render: (text, record) => {
          const projectsArr = record?.projects_list?.map(({name, id}) => ({name, id})) || [];

          return (
            <Dropdown
              content={
                <ul className={style.dropdownList}>
                  {projectsArr.length > 0
                    ? projectsArr.map(({name, id}) => <li key={id}>{name}</li>)
                    : 'Проекты не назначены'}
                </ul>
              }>
              {projectsArr.length}{' '}
              {declOfNum(projectsArr.length, ['проект', 'проекта', 'проектов'])}
            </Dropdown>
          );
        },
      },
      {
        title: 'Сотрудники',
        key: 'employees_list',
        render: (value, record) => (
          <Dropdown
            content={
              <ul className={style.dropdownList}>
                {value.length > 0 ? (
                  record?.employees_list?.map(({id, full_name}) => (
                    <li key={id}>
                      <Link to={`/onboarding/employees/${id}`}>{full_name}</Link>
                    </li>
                  ))
                ) : (
                  <li>Нет сотрудников</li>
                )}
              </ul>
            }>
            {value.length} чел.
          </Dropdown>
        ),
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
    () => curatorsColumns.filter(column => column.filter),
    [curatorsColumns],
  );

  return (
    <>
      <Helmet title="Onboarding | Кураторы" />

      <section className="section" style={{height: '100vh'}}>
        <div className={style.CuratorsHeader}>
          <h2>Кураторы</h2>

          <Button onClick={handleFilterBtn} pressed={isOpened}>
            <FunnelIcon />
            Фильтры
          </Button>
        </div>

        <TableSearchFilters
          columnsWithFilters={columnsWithFilters}
          isOpened={isOpened}
          searchPlaceholder="Поиск по кураторам"
          searchField="full_name">
          {(role === 'admin' || role === 'hr') && (
            <Button onClick={handleModalNewEmployee} variant="primary">
              <PlusIcon />
              Добавить куратора
            </Button>
          )}
        </TableSearchFilters>

        <Table
          isMaxCount={isMaxCountHelper(offset, curators)}
          isFetching={isFetching}
          columns={curatorsColumns}
          dataSource={curators?.results}
        />
      </section>

      <Modal
        title="Новый куратор"
        isOpened={isOpenedModalNewEmployee}
        onClose={handleModalNewEmployee}>
        <NewEmployeeForm
          setToken={setToken}
          openTokenModal={handleModalToken}
          closeModal={handleModalNewEmployee}
          role="curator"
        />
      </Modal>

      <Modal title="Токен куратора" isOpened={isOpenedModalToken} onClose={handleModalToken}>
        <TokenForm token={token} />
      </Modal>
    </>
  );
}
