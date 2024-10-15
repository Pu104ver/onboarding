import {useNavigate, useParams} from 'react-router-dom';

import cn from 'classnames';
import Cookies from 'js-cookie';
import {useEffect, useMemo, useState} from 'react';
import {Helmet} from 'react-helmet';
import {toast} from 'react-toastify';

import styles from './EmployeePage.module.scss';

import {useAppDispatch, useAppSelector} from '@/app/store/hooks';
import {userSelector} from '@/entities/User/model/selectors/GetUser';
import {logout} from '@/entities/User/model/slice/UserSlice';
import {
  useChangeEmployeeData,
  useGetEmployeeByIdQuery,
} from '@/features/EmployeesOperations/model/EmployeesApi';
import {exportAnswers} from '@/features/EmployeesOperations/model/ExportAnswers';
import {EmployeeAnswersTable} from '@/features/PullsOperations';
import EmployeeIcon from '@/shared/assets/employee.svg?react';
import LeftArrowIcon from '@/shared/assets/leftArrow.svg?react';
import TrashIcon from '@/shared/assets/trash.svg?react';
import UpLoadIcon from '@/shared/assets/upload.svg?react';
import Button from '@/shared/ui/Button';
import EditText from '@/shared/ui/EditText';
import Comments from '@/widgets/Comments';
import DataCards from '@/widgets/DataCards';
import EmployeesList from '@/widgets/EmployeesList';

//TODO import Events from '@/widgets/Events';

interface IEmployeePageProps {
  isMyProfile?: boolean;
}

const EmployeePage = ({isMyProfile = false}: IEmployeePageProps) => {
  const {id: userId} = useAppSelector(userSelector);
  const {id: employeeId} = useParams();
  const id = isMyProfile ? userId : employeeId;

  const hasNoId = useMemo(
    () => (isMyProfile && userId === null) || (!isMyProfile && !employeeId),
    [isMyProfile, userId, employeeId],
  );

  const {data: employee} = useGetEmployeeByIdQuery(id, {skip: hasNoId});
  const [changeEmployeeData] = useChangeEmployeeData();
  const [isCuratorShow, setIsCuratorShow] = useState(false);

  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  useEffect(() => {
    hasNoId && navigate(-1);
  }, [hasNoId, navigate]);

  const handleChangeEmployeeData = (field: string, text: string | boolean) => {
    void changeEmployeeData({id, [field]: text});
  };

  const handleExportAnswers = async () => {
    if (id) {
      const res = await exportAnswers({
        employee: id,
        filename: `Ответы по опросам сотрудника «${employee?.full_name}»`,
      });

      if (typeof res !== 'string' && !res.ok) {
        toast.warning(res.statusText || res.detail?.error || 'У сотрудника нет ответов');
      }
    } else {
      toast.warning('Некорректный идентификатор сотрудника');
    }
  };

  const handleArchiveCurator = async () => {
    const response = await changeEmployeeData({id, is_archived: true});

    response.data &&
      toast('Сотрудник перенесен в архив', {
        type: 'success',
      });
  };

  const handleLogout = () => {
    Cookies.remove('access_token');
    dispatch(logout());
  };

  return (
    <>
      <Helmet title="Onboarding" />

      <div className={cn(styles.employeePage, 'section')}>
        <div className={styles.header}>
          <Button variant="text" onClick={() => navigate(-1)}>
            <LeftArrowIcon />
            Вернуться назад
          </Button>

          {isMyProfile && (
            <Button onClick={handleLogout} variant="text" danger>
              Выйти
            </Button>
          )}
        </div>

        <h2 className={styles.full_name}>
          <EditText
            field="full_name"
            initialText={employee?.full_name}
            id={employeeId}
            changeData={handleChangeEmployeeData}
          />
        </h2>

        <div className="flex">
          <Button variant="text" onClick={handleArchiveCurator}>
            <TrashIcon />
            Перенести в архив
          </Button>

          <Button variant="text" onClick={handleExportAnswers}>
            <UpLoadIcon />
            Выгрузить ответы
          </Button>

          {employee && (
            <Button
              variant="text"
              onClick={() =>
                handleChangeEmployeeData('is_curator_employee', !employee.is_curator_employee)
              }>
              <EmployeeIcon />
              {employee.is_curator_employee ? 'Убрать роль куратора' : 'Сделать куратором'}
            </Button>
          )}
        </div>
        <DataCards employee={employee} />
        <div className={styles.tables}>
          <div className={styles.tableHeader}>
            <h3
              className={cn({[styles.active]: !isCuratorShow})}
              onClick={() => setIsCuratorShow(false)}>
              Собственные ответы
            </h3>
            <span>|</span>
            <h3
              className={cn({[styles.active]: isCuratorShow})}
              onClick={() => setIsCuratorShow(true)}>
              Обратная связь от кураторов
            </h3>
          </div>

          {isCuratorShow && employeeId ? (
            <EmployeesList
              isForEmployee
              employeeId={employeeId}
              employees_list={employee?.curators_list}
            />
          ) : (
            id && <EmployeeAnswersTable id={id} />
          )}
        </div>

        {!isMyProfile && <Comments id={employeeId} />}
        {/* TODO<div className={style.employeeBody}>
          <Events events={employee?.events} />
        </div> */}
      </div>
    </>
  );
};

export default EmployeePage;
