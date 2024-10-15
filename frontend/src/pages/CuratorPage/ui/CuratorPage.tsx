import {useNavigate, useParams} from 'react-router-dom';

import cn from 'classnames';
import {useEffect, useMemo} from 'react';
import {Helmet} from 'react-helmet';
import {toast} from 'react-toastify';

import style from './CuratorPage.module.scss';

import {useAppSelector} from '@/app/store/hooks';
import {userSelector} from '@/entities/User/model/selectors/GetUser';
import {
  useChangeEmployeeData,
  useGetEmployeeByIdQuery,
} from '@/features/EmployeesOperations/model/EmployeesApi';
import {exportAnswers} from '@/features/EmployeesOperations/model/ExportAnswers';
import LeftArrowIcon from '@/shared/assets/leftArrow.svg?react';
import TrashIcon from '@/shared/assets/trash.svg?react';
import UpLoadIcon from '@/shared/assets/upload.svg?react';
import {getTargetEmployees} from '@/shared/helpers/getTargetEmployees';
import Button from '@/shared/ui/Button';
import EditText from '@/shared/ui/EditText';
import Comments from '@/widgets/Comments';
import DataCards from '@/widgets/DataCards';
import EmployeesList from '@/widgets/EmployeesList';

//TODO import Events from '@/widgets/Events';

interface ICuratorPageProps {
  isMyProfile?: boolean;
}

const CuratorPage = ({isMyProfile = false}: ICuratorPageProps) => {
  const {id: userId} = useAppSelector(userSelector);
  const {id: curatorId} = useParams();
  const id = isMyProfile ? userId : curatorId;

  const hasNoId = useMemo(
    () => (isMyProfile && userId === null) || (!isMyProfile && !curatorId),
    [isMyProfile, userId, curatorId],
  );

  const {data: curator} = useGetEmployeeByIdQuery(id, {skip: hasNoId});
  const [changeCuratorData] = useChangeEmployeeData();

  const navigate = useNavigate();

  useEffect(() => {
    hasNoId && navigate(-1);
  }, [hasNoId, navigate]);

  const handleChangeCuratorData = (field: string, text: string | boolean) => {
    void changeCuratorData({id, [field]: text});
  };

  const target_employee = useMemo(
    () => getTargetEmployees(curator?.employees_list),
    [curator?.employees_list],
  );

  const handleExportAnswers = async () => {
    if (id) {
      const res = await exportAnswers({
        employee: id,
        target_employee,
        filename: `Ответы по опросам сотрудников, закрепленных за куратором «${curator?.full_name}»`,
      });

      if (typeof res !== 'string' && !res.ok) {
        toast.warning(res?.statusText || res.detail?.error || 'У куратора нет ответов');
      }
    } else {
      toast.warning('Некорректный идентификатор куратора');
    }
  };

  const handleArchiveCurator = async () => {
    const response = await changeCuratorData({id, is_archived: true});

    response.data &&
      toast('Куратор перенесен в архив', {
        type: 'success',
      });
  };

  return (
    <>
      <Helmet title="Onboarding" />

      <div className={cn(style.curatorPage, 'section')}>
        <div>
          <Button variant="text" onClick={() => navigate(-1)}>
            <LeftArrowIcon />
            Вернуться назад
          </Button>
        </div>
        <h2 className={style.full_name}>
          <EditText
            field="full_name"
            initialText={curator?.full_name}
            id={curatorId}
            changeData={handleChangeCuratorData}
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
        </div>

        <DataCards employee={curator} isCurator={true} />

        <div className={style.tables}>
          <div className={style.tableHeader}>
            <h3>Ответы по сотрудникам</h3>
          </div>

          {curatorId && (
            <EmployeesList
              isForEmployee={false}
              employeeId={curatorId}
              employees_list={curator?.employees_list}
            />
          )}
        </div>
        <div className={style.curatorBody}>
          <Comments id={curatorId} />

          {/* TODO <Events events={employee?.events} /> */}
        </div>
      </div>
    </>
  );
};

export default CuratorPage;
