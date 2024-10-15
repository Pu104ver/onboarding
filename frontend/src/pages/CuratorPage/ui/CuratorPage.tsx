import {useNavigate, useParams} from 'react-router-dom';

import cn from 'classnames';
import {format} from 'date-fns';
import {useEffect, useMemo, useState} from 'react';
import {Helmet} from 'react-helmet';
import {Controller, SubmitHandler, useForm} from 'react-hook-form';
import {toast} from 'react-toastify';

import style from './CuratorPage.module.scss';

import {useAppSelector} from '@/app/store/hooks';
import {IAvailablePollsForm, IILaunchPollForm, IPoll, TPollType} from '@/app/types/Employee';
import {TSelectOption} from '@/app/types/Select';
import {userSelector} from '@/entities/User/model/selectors/GetUser';
import {
  useChangeEmployeeData,
  useGetAvailablePolls,
  useGetEmployeeByIdQuery,
  useLaunchPoll,
} from '@/features/EmployeesOperations/model/EmployeesApi';
import {exportAnswers} from '@/features/EmployeesOperations/model/ExportAnswers';
import LeftArrowIcon from '@/shared/assets/leftArrow.svg?react';
import PollIcon from '@/shared/assets/poll.svg?react';
import TrashIcon from '@/shared/assets/trash.svg?react';
import UpLoadIcon from '@/shared/assets/upload.svg?react';
import {DATE_FOR_BACKEND} from '@/shared/const/DateStrings';
import {pollsTypeFilters} from '@/shared/const/filters';
import {convertToSelectOptions} from '@/shared/helpers/convertToSelectOptions';
import {getTargetEmployees} from '@/shared/helpers/getTargetEmployees';
import {SuspenseProfilePage} from '@/shared/suspense/SuspenseProfilePage';
import Button from '@/shared/ui/Button';
import EditText from '@/shared/ui/EditText';
import Modal from '@/shared/ui/Modal';
import Select from '@/shared/ui/Select';
import Comments from '@/widgets/Comments';
import DataCards from '@/widgets/DataCards';
import EmployeesList from '@/widgets/EmployeesList';

//TODO import Events from '@/widgets/Events';

interface ICuratorPageProps {
  isMyProfile?: boolean;
}

const convertAvailablePollsToOptions = (polls: IPoll[] | undefined): TSelectOption[] =>
  polls?.map(poll => ({label: `${poll.title} (${poll.related_object.name})`, value: poll.id})) ||
  [];

const CuratorPage = ({isMyProfile = false}: ICuratorPageProps) => {
  const {id: userId} = useAppSelector(userSelector);
  const {id: curatorId} = useParams();
  const id = isMyProfile ? userId : curatorId;

  const hasNoId = useMemo(
    () => (isMyProfile && userId === null) || (!isMyProfile && !curatorId),
    [isMyProfile, userId, curatorId],
  );

  const {data: curator, isFetching, isError} = useGetEmployeeByIdQuery(id, {skip: hasNoId});
  const [changeCuratorData] = useChangeEmployeeData();

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
    const {poll, target_employee, ...body} = fields;
    const pollForSubmit = Number(poll?.value);

    await launchPoll({
      ...body,
      poll: pollForSubmit,
      employee: curator?.id,
      target_employee: Number(target_employee?.value),
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
        curator?.role &&
        void getAvailablePolls({
          employee: curator?.id,
          intended_for: curator?.role,
          poll_type: watch('poll_type').value.toString() as TPollType,
        });
    }
  }, [watch('poll_type')]);

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

  const targetEmployeeOptions: TSelectOption[] = useMemo(
    () => convertToSelectOptions(curator?.employees_list),
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
      toast.warning('Не удалось выгрузить ответы куратора');
    }
  };

  const handleArchiveCurator = async () => {
    const response = await changeCuratorData({id, is_archived: !curator?.is_archived});

    response.data &&
      toast(
        response.data.is_archived ? 'Куратор перенесен в архив' : 'Куратора вернули из архива',
        {
          type: 'success',
        },
      );
  };

  if (isFetching || isError) {
    return <SuspenseProfilePage isError={isError} />;
  }

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
            {curator?.is_archived ? 'Вернуть из архива' : 'Перенести в архив'}
          </Button>

          <Button variant="text" onClick={handleExportAnswers}>
            <UpLoadIcon />
            Выгрузить ответы
          </Button>

          <Button variant="text" onClick={handleOpenLaunchPollModal}>
            <PollIcon />
            Запустить опрос
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

      <Modal
        isOpened={isOpenedLaunchPollModal}
        title="Запуск опроса"
        onClose={handleOpenLaunchPollModal}>
        <form onSubmit={handleSubmit(onSubmitLaunchPoll)} className={style.form}>
          <label htmlFor="project">
            <p>Выберите тип опроса</p>

            <Controller
              control={control}
              name="poll_type"
              render={({field: {value, onChange}}) => (
                <>
                  <Select
                    id="poll_type"
                    options={pollsTypeFilters}
                    placeholder="Выберите тип опроса"
                    value={value}
                    selectSingleValue={onChange}
                  />

                  {errors.poll && <p className={style.errorMsg}>Выберите опрос</p>}
                </>
              )}
            />
          </label>

          <label htmlFor="target_employee">
            <p>Выберите сотрудника, которому хотите запустить опрос</p>

            <Controller
              control={control}
              name="target_employee"
              render={({field: {value, onChange}}) => (
                <>
                  <Select
                    id="target_employee"
                    options={targetEmployeeOptions}
                    placeholder="Выберите сотрудника"
                    value={value}
                    selectSingleValue={onChange}
                    noOptionsMessage={() => 'У этого куратора нет сотрудников'}
                  />

                  {errors.poll && <p className={style.errorMsg}>Выберите сотрудника</p>}
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
                    noOptionsMessage={() => 'Нет доступных опросов'}
                  />

                  {errors.poll && <p className={style.errorMsg}>Выберите опрос</p>}
                </>
              )}
            />
          </label>

          <Button
            type="submit"
            variant="primary"
            loading={isLoadingLaunchingPoll}
            className={style.submitBtn}>
            Запустить
          </Button>
        </form>
      </Modal>
    </>
  );
};

export default CuratorPage;
