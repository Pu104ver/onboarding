import {IEmployeesItem} from '@/app/types/Employee';
import {useCompletePoll} from '@/features/EmployeesOperations/model/EmployeesApi';
import Button from '@/shared/ui/Button';

interface ISkipButtonProps {
  record?: IEmployeesItem;
}

export const SkipButton = ({record}: ISkipButtonProps) => {
  const [completePoll] = useCompletePoll();

  return !record || !record?.onboarding_status?.status ? (
    'Не пройдено ни одного опроса'
  ) : record?.onboarding_status?.status !== 'completed' ? (
    <Button
      onClick={() =>
        completePoll({
          pollId: record?.onboarding_status?.id,
          employeeId: record?.user_details.id,
        })
      }>
      Пропустить
    </Button>
  ) : (
    'Все опросы пройдены'
  );
};
