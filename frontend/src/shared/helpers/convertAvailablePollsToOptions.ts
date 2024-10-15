import {IPoll} from '@/app/types/Employee';
import {TSelectOption} from '@/app/types/Select';

export const convertAvailablePollsToOptions = (polls: IPoll[] | undefined): TSelectOption[] =>
  polls?.map(poll => ({label: `${poll.title} (${poll.related_object.name})`, value: poll.id})) ||
  [];
