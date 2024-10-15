import {useNavigate, useParams} from 'react-router-dom';

import cn from 'classnames';
import {format} from 'date-fns';
import Cookies from 'js-cookie';
import {useEffect, useMemo, useState} from 'react';
import {Helmet} from 'react-helmet';
import {Controller, SubmitHandler, useForm} from 'react-hook-form';
import {toast} from 'react-toastify';

import styles from './EmployeePage.module.scss';

import {useAppDispatch, useAppSelector} from '@/app/store/hooks';
import {IAvailablePollsForm, IILaunchPollForm, TPollType} from '@/app/types/Employee';
import {TSelectOption} from '@/app/types/Select';
import {userSelector} from '@/entities/User/model/selectors/GetUser';
import {logout} from '@/entities/User/model/slice/UserSlice';
import {
  useChangeEmployeeData,
  useLaunchPoll,
  useGetEmployeeByIdQuery,
  useGetAvailablePolls,
} from '@/features/EmployeesOperations/model/EmployeesApi';
import {exportAnswers} from '@/features/EmployeesOperations/model/ExportAnswers';
import {EmployeeAnswersTable} from '@/features/PullsOperations';
import EmployeeIcon from '@/shared/assets/employee.svg?react';
import LeftArrowIcon from '@/shared/assets/leftArrow.svg?react';
import PollIcon from '@/shared/assets/poll.svg?react';
import TrashIcon from '@/shared/assets/trash.svg?react';
import UpLoadIcon from '@/shared/assets/upload.svg?react';
import {DATE_FOR_BACKEND} from '@/shared/const/DateStrings';
import {pollsTypeFilters} from '@/shared/const/filters';
import {convertAvailablePollsToOptions} from '@/shared/helpers/convertAvailablePollsToOptions';
import {SuspenseProfilePage} from '@/shared/suspense/SuspenseProfilePage';
import Button from '@/shared/ui/Button';
import EditText from '@/shared/ui/EditText';
import Modal from '@/shared/ui/Modal';
import Select from '@/shared/ui/Select';
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

  const {data: employee, isFetching, isError} = useGetEmployeeByIdQuery(id, {skip: hasNoId});
  const [changeEmployeeData] = useChangeEmployeeData();

  const [isCuratorShow, setIsCuratorShow] = useState(false);
  const [isOpenedLaunchPollModal, setIsOpenedLaunchPollModal] = useState(false);

  const handleOpenLaunchPollModal = () => {
    setIsOpenedLaunchPollModal(prev => !prev);
  };

  const {
    watch,
    setValue,
    formState: {errors},
    handleSubmit,
    reset,
    control,
  } = useForm<IILaunchPollForm & IAvailablePollsForm>();

  const [launchPoll, {isLoading: isLoadingLaunchingPoll}] = useLaunchPoll();
  const [getAvailablePolls, {data: availablePolls, isFetching: isFetchingAvailablePolls}] =
    useGetAvailablePolls();

  const onSubmitLaunchPoll: SubmitHandler<
    IILaunchPollForm & IAvailablePollsForm
  > = async fields => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const {poll, poll_type, ...body} = fields;
    const pollForSubmit = Number(poll?.value);

    await launchPoll({
      ...body,
      poll: pollForSubmit,
      employee: employee?.id,
      target_employee: undefined,
      date_planned_at: format(new Date(), DATE_FOR_BACKEND),
    }).then(({data}) => {
      if (data) {
        reset();
        handleOpenLaunchPollModal();
      }
    });
  };

  const availablePollsOptions: TSelectOption[] = useMemo(
    () => convertAvailablePollsToOptions(availablePolls),
    [availablePolls],
  );

  const hasNoSelectedPollType = useMemo(() => !watch('poll_type'), [watch('poll_type')]);

  useEffect(() => {
    if (hasNoSelectedPollType) {
      setValue('poll', null);
    } else {
      watch('poll_type') &&
        employee?.role &&
        void getAvailablePolls({
          employee: employee?.id,
          intended_for: employee.role,
          poll_type: watch('poll_type').value.toString() as TPollType,
        });
    }
  }, [watch('poll_type')]);

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
      toast.warning('Не удалось выгрузить ответы сотрудника');
    }
  };

  const handleArchiveEmployee = async () => {
    const response = await changeEmployeeData({id, is_archived: !employee?.is_archived});

    response.data &&
      toast(
        response.data.is_archived ? 'Сотрудник перенесен в архив' : 'Сотрудника вернули из архива',
        {
          type: 'success',
        },
      );
  };

  const handleLogout = () => {
    Cookies.remove('token');
    dispatch(logout());
  };

  if (isFetching || isError) {
    return <SuspenseProfilePage isError={isError} />;
  }

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
          <Button variant="text" onClick={handleArchiveEmployee}>
            <TrashIcon />
            {employee?.is_archived ? 'Вернуть из архива' : 'Перенести в архив'}
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

          <Button variant="text" onClick={handleOpenLaunchPollModal}>
            <PollIcon />
            Запустить опрос
          </Button>
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

      <Modal
        isOpened={isOpenedLaunchPollModal}
        title="Запуск опроса"
        onClose={handleOpenLaunchPollModal}>
        <form onSubmit={handleSubmit(onSubmitLaunchPoll)} className={styles.form}>
          <label htmlFor="project">
            <p>Выберите тип опроса</p>

            <Controller
              control={control}
              name="poll_type"
              render={({field: {value, onChange}}) => (
                <>
                  <Select
                    id="poll"
                    options={pollsTypeFilters}
                    placeholder="Выберите тип опроса"
                    value={value}
                    selectSingleValue={onChange}
                  />

                  {errors.poll && <p className={styles.errorMsg}>Выберите опрос</p>}
                </>
              )}
            />
          </label>

          <label htmlFor="project">
            <p>Какой опрос запустить?</p>

            <Controller
              control={control}
              name="poll"
              render={({field: {value, onChange}}) => (
                <>
                  <Select
                    id="poll"
                    options={availablePollsOptions}
                    placeholder="Выберите опрос"
                    value={value}
                    selectSingleValue={onChange}
                    isDisabled={hasNoSelectedPollType}
                    isLoading={isFetchingAvailablePolls}
                    loadingMessage={() => 'Загрузка кураторов...'}
                  />

                  {errors.poll && <p className={styles.errorMsg}>Выберите опрос</p>}
                </>
              )}
            />
          </label>

          <Button
            type="submit"
            variant="primary"
            loading={isLoadingLaunchingPoll}
            className={styles.submitBtn}>
            Запустить
          </Button>
        </form>
      </Modal>
    </>
  );
};

export default EmployeePage;
