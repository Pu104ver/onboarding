import {format} from 'date-fns';
import {useEffect, useMemo} from 'react';
import {Controller, SubmitHandler, useForm} from 'react-hook-form';

import styles from './NewEmployeeForm.module.scss';

import {INewEmployeeForm} from '@/app/types/NewEmployee.type';
import {TRole} from '@/app/types/Roles.type';
import {TSelectOption} from '@/app/types/Select';
import {useGetCuratorsPinnedToProjects} from '@/features/CuratorsOperations/model/CuratorsApi';
import {useCreateEmployee} from '@/features/EmployeesOperations/model/EmployeesApi';
import {useGetProjects} from '@/features/Projects/model/Projects';
import {DATE_FOR_BACKEND} from '@/shared/const/DateStrings';
import {convertToSelectOptions} from '@/shared/helpers/convertToSelectOptions';
import Button from '@/shared/ui/Button';
import Calendar from '@/shared/ui/Calendar';
import Input from '@/shared/ui/Input';
import Select from '@/shared/ui/Select';
import {
  checkEmail,
  checkEmpty,
  checkOnlyLettersAndDash,
  checkTelegramNickname,
} from '@/shared/validation/validation';

interface INewEmployeeFormProps {
  setToken: (token: string) => void;
  openTokenModal: () => void;
  closeModal?: () => void;
  role: TRole;
}

const getRoleText = (role: TRole, endOfWord: string = 'a') =>
  role === 'curator' ? 'куратор' + endOfWord : 'сотрудник' + endOfWord;

const NewEmployeeForm = ({setToken, openTokenModal, closeModal, role}: INewEmployeeFormProps) => {
  const {
    register,
    formState: {errors},
    watch,
    setValue,
    handleSubmit,
    reset,
    control,
  } = useForm<INewEmployeeForm>();

  const hasNoSelectedProject = useMemo(
    () => !watch('projects') || watch('projects')?.length === 0,
    [watch('projects')],
  );

  const {data: projects} = useGetProjects();
  const [getCurators, {data: curators, isFetching: isFetchingCurators}] =
    useGetCuratorsPinnedToProjects();

  useEffect(() => {
    if (hasNoSelectedProject) {
      setValue('curators', null);
    } else {
      watch('projects') &&
        void getCurators(watch('projects')?.map(project => Number(project.value)) || []);
    }
  }, [watch('projects')]);

  const [createEmployee, {isLoading: isLoadingCreate}] = useCreateEmployee();

  const onSubmit: SubmitHandler<INewEmployeeForm> = async fields => {
    const {projects, curators, ...body} = fields;
    const projectsForSubmit = projects?.map(project => Number(project.value));
    const curatorsForSubmit = curators?.map(curator => Number(curator.value));

    await createEmployee({
      ...body,
      role,
      projects: projectsForSubmit,
      curators: curatorsForSubmit,
      date_of_employment:
        fields.date_of_employment && format(fields.date_of_employment, DATE_FOR_BACKEND),
    }).then(({data}) => {
      if (data) {
        setToken(`${data.uid}_${data.token}`);
        openTokenModal();

        closeModal && closeModal();
        reset();
      }
    });
  };

  const projectOptions: TSelectOption[] = useMemo(
    () => convertToSelectOptions(projects),
    [projects],
  );

  const curatorsOptions: TSelectOption[] = useMemo(
    () => convertToSelectOptions(curators),
    [curators],
  );

  const roleText = useMemo(() => getRoleText(role), [role]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={styles.form}>
      <label htmlFor="full_name">
        <p>ФИО {roleText}</p>

        <Input
          id="full_name"
          placeholder={`Введите ФИО ${roleText}`}
          {...register('full_name', {
            required: true,
            validate: value =>
              checkEmpty(value, `Введите ФИО ${roleText}`) === true &&
              checkOnlyLettersAndDash(
                value,
                `ФИО ${roleText} не может содержать спецсимволы и цифры`,
              ),
          })}
        />
        {errors.full_name && (
          <p className={styles.errorMsg}>{errors.full_name.message || `Введите ФИО ${roleText}`}</p>
        )}
      </label>

      <label htmlFor="email">
        <p>Email {roleText}</p>

        <Input
          id="email"
          placeholder={`Введите email ${roleText}`}
          {...register('email', {
            required: true,
            validate: value => checkEmail(value, 'Введите корректный email'),
          })}
        />
        {errors.email && (
          <p className={styles.errorMsg}>{errors.email.message || `Введите email ${roleText}`}</p>
        )}
      </label>

      <label htmlFor="telegram_nickname">
        <p>Никнейм в Telegram</p>

        <Input
          id="telegram_nickname"
          placeholder="divergent"
          icon={<span className={styles.tgPreffix}>@</span>}
          {...register('telegram_nickname', {
            validate: value => checkTelegramNickname(value, 'Введите никнейм в Telegram'),
          })}
        />
        {errors.telegram_nickname && (
          <p className={styles.errorMsg}>
            {errors.telegram_nickname.message || 'Введите никнейм в Telegram'}
          </p>
        )}
      </label>

      <label htmlFor="project">
        <p>Название проекта</p>

        <Controller
          control={control}
          name="projects"
          rules={{required: role === 'employee'}}
          render={({field: {value, onChange}, fieldState: {error}}) => (
            <>
              <Select
                id="projects"
                options={projectOptions}
                placeholder="Выберите проект"
                value={value}
                isMulti
                selectMultiValues={onChange}
                noOptionsMessage={() => 'Нет проектов'}
              />

              {error && <p className={styles.errorMsg}>Выберите проект</p>}
            </>
          )}
        />
      </label>

      {role === 'employee' && (
        <label htmlFor="curators">
          <p>Куратор</p>

          <Controller
            control={control}
            name="curators"
            rules={{required: role === 'employee'}}
            render={({field: {value, onChange}, fieldState: {error}}) => (
              <>
                <Select
                  id="curators"
                  options={curatorsOptions}
                  placeholder="Выберите куратора"
                  value={value}
                  isMulti
                  selectMultiValues={onChange}
                  isDisabled={hasNoSelectedProject}
                  isLoading={isFetchingCurators}
                  loadingMessage={() => 'Загрузка кураторов...'}
                  noOptionsMessage={() => 'Нет кураторов на этих проектах'}
                />

                {error && <p className={styles.errorMsg}>Выберите куратора</p>}
              </>
            )}
          />
        </label>
      )}

      {role === 'employee' && (
        <label htmlFor="date_of_employment">
          <p>Дата 1-го рабочего дня</p>

          <Controller
            name="date_of_employment"
            control={control}
            rules={{required: role === 'employee'}}
            render={({field: {onChange, value}}) => (
              <Calendar
                id="date_of_employment"
                onChange={onChange}
                selected={value ? new Date(+value) : null}
                placeholderText="Укажите первый рабочий день"
                popperPlacement="top"
              />
            )}
          />

          {errors.date_of_employment && (
            <p className={styles.errorMsg}>Укажите первый рабочий день {roleText}</p>
          )}
        </label>
      )}

      <Button
        type="submit"
        variant="primary"
        loading={isLoadingCreate}
        className={styles.submitBtn}>
        Добавить
      </Button>
    </form>
  );
};

export default NewEmployeeForm;
