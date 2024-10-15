import cn from 'classnames';

import style from './EmployeeAnswersTable.module.scss';

import {useGetEmployeePollsQuery} from '@/features/PullsOperations/model/PollsApi';
import {convertDateFromBackToFront} from '@/shared/helpers/convertDateFromBackToFront';
import Collapse from '@/shared/ui/Collapse';
import Skeleton from '@/shared/ui/Skeleton';

interface IEmployeeAnswersTableProps {
  id: string | number;
  target_employee_id?: string | number;
}
const EmployeeAnswersTable = ({id, target_employee_id}: IEmployeeAnswersTableProps) => {
  const {data, isFetching} = useGetEmployeePollsQuery({
    id,
    target_employee_id,
  });

  return (
    <div className={style.EmployeeAnswersTable}>
      <ul>
        {isFetching ? (
          <Skeleton className={style.tableSkeleton} />
        ) : data && data.length > 0 ? (
          data.map(item => (
            <li key={item.id} className={style.stageBlock}>
              <Collapse
                isRevert
                defaultHidden={true}
                title={<h4>Этап онбординга: {item.title}</h4>}>
                <ul className={style.questionsBlock}>
                  <li className={style.Header}>
                    <h4>Вопрос:</h4> <h4>Ответ:</h4>
                  </li>

                  {item.questions.map(({answers, question_type, text, id}) =>
                    question_type === 'finish' || question_type === 'next' ? null : (
                      <li key={id} className={style.questionBlock}>
                        <p>{text}</p>

                        <ul>
                          {answers.map(({answer, requires_attention, created_at, id}) => (
                            <li key={id} className={cn({[style.attention]: requires_attention})}>
                              {answer}
                              <span>{convertDateFromBackToFront(created_at)}</span>
                            </li>
                          ))}
                        </ul>
                      </li>
                    ),
                  )}
                </ul>
              </Collapse>
            </li>
          ))
        ) : (
          <h5 className={style.emptyTitle}>Сотрудник не отвечал на вопросы</h5>
        )}
      </ul>
    </div>
  );
};

export default EmployeeAnswersTable;
