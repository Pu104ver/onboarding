import {Link} from 'react-router-dom';

import classNames from 'classnames';

import style from './DataCards.module.scss';

import {EmployeeDataType} from '@/app/types/Employee';
import {useGetCuratorsDictionary} from '@/features/CuratorsOperations/model/CuratorsApi';
import {
  useChangeEmployeeData,
  useCompletePoll,
  useGetStatusDictionary,
} from '@/features/EmployeesOperations/model/EmployeesApi';
import {useGetProjects} from '@/features/Projects/model/Projects';
import {convertToSelectOptions} from '@/shared/helpers/convertToSelectOptions';
import Button from '@/shared/ui/Button';
import StatusItem from '@/shared/ui/StatusItem';
import EditDate from '@/widgets/EditDate';
import EditMultipleSelect from '@/widgets/EditMultipleSelect';
import EditSelect from '@/widgets/EditSelect';

interface IDataCardsProps {
  employee?: EmployeeDataType;
  isCurator?: boolean;
}

const DataCards = ({employee, isCurator}: IDataCardsProps) => {
  const [completePoll] = useCompletePoll();
  const {data: statusDictionary} = useGetStatusDictionary();
  const {data: curators} = useGetCuratorsDictionary();
  const {data: project} = useGetProjects();
  const [changeEmployeeData] = useChangeEmployeeData();

  const curatorsList = convertToSelectOptions(employee?.curators_list || []);
  const projectsList = convertToSelectOptions(employee?.projects_list || []);
  const curatorsOptions = convertToSelectOptions(curators);
  const projectsOptions = convertToSelectOptions(project);

  const changeEmployeeDataFunc = (field: string, text: string) => {
    void changeEmployeeData({id: employee?.id, [field]: text});
  };

  const changeEmployeeMultiDataFunc = (field: string, text: string[]) => {
    void changeEmployeeData({
      id: employee?.id,
      [field]: text.map(value => Number(value)),
    });
  };

  return (
    <ul className={classNames(style.datacards, {[style.isCurator]: isCurator})}>
      <li className={style.datacard}>
        <h4>Проект</h4>
        <EditMultipleSelect
          field="projects"
          initialValueArray={projectsList}
          selectArray={projectsOptions}
          changeData={changeEmployeeMultiDataFunc}
          placeholder="Выберите проект"
        />
      </li>

      {!isCurator && (
        <li className={style.datacard}>
          <h4>Куратор</h4>
          <EditMultipleSelect
            field="curators"
            render={option => (
              <Link key={option.value} to={`/onboarding/curators/${option.value}`}>
                {option.label}
              </Link>
            )}
            initialValueArray={curatorsList}
            selectArray={curatorsOptions}
            changeData={changeEmployeeMultiDataFunc}
            placeholder="Выберите куратора"
          />
        </li>
      )}

      {!isCurator && (
        <li className={style.blockWithTwoParams}>
          <div className={style.blockInDataCard}>
            <h4>
              Этап онбординга
              {employee?.onboarding_status?.id &&
                employee?.onboarding_status?.status !== 'completed' && (
                  <Button
                    onClick={() =>
                      completePoll({
                        pollId: employee?.onboarding_status?.id,
                        employeeId: employee.id,
                      })
                    }>
                    Пропустить
                  </Button>
                )}
            </h4>
            <p>{employee?.onboarding_status?.poll_title || 'Не указан'}</p>
          </div>
          <hr />
          <div className={style.blockInDataCard}>
            <h4>Статус заполнения</h4>
            <StatusItem text={employee?.onboarding_status?.status} />
          </div>
        </li>
      )}

      <li className={style.datacard}>
        <h4>Никнейм в Telegram</h4>
        <Button copyable>{employee?.telegram_nickname || 'Не указан'}</Button>
      </li>

      {!isCurator && (
        <li className={style.datacard}>
          <h4>Дата 1-го рабочего дня</h4>
          <p>
            <EditDate
              field="date_of_employment"
              initialDate={employee?.date_of_employment}
              changeData={changeEmployeeDataFunc}
            />
          </p>
        </li>
      )}

      {!isCurator && (
        <li className={style.datacard}>
          <h4>Статус сотрудника</h4>
          <EditSelect
            field="status"
            initialValue={employee?.status}
            selectArray={statusDictionary}
            changeData={changeEmployeeDataFunc}
            placeholder="Статус сотрудника"
          />
        </li>
      )}
      {!isCurator && (
        <li className={style.datacard}>
          <h4>Встреча по итогам ИС</h4>
          <p>
            <EditDate
              showTimeSelect
              timeIntervals={60}
              timeCaption="Время"
              field="date_meeting"
              dateFormat="dd.MM.yyyy HH:mm"
              initialDate={employee?.date_meeting}
              changeData={changeEmployeeDataFunc}
            />
          </p>
        </li>
      )}
    </ul>
  );
};

export default DataCards;
