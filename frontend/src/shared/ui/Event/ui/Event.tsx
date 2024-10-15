import style from './Event.module.scss';

import StatusItem from '@/shared/ui/StatusItem';

interface EventType {
  id: string;
  title: string;
  time: string;
  status: string;
}

const Event = ({event}: {event: EventType}) => {
  return (
    <div className={style.event}>
      <div className={style.eventBody}>
        <p>{event.title}</p>

        <p>{event.time}</p>
      </div>
      <div className={style.eventStatus}>
        <StatusItem text={event.status} />
      </div>
    </div>
  );
};

export default Event;
