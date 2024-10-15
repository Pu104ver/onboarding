import style from './Events.module.scss';

import Event from '@/shared/ui/Event';

interface EventType {
  id: string;
  title: string;
  time: string;
  status: string;
}
const Events = ({events}: {events: EventType[]}) => {
  return (
    <div className={style.events}>
      <h3>Записи на мероприятия</h3>
      {events.map(event => (
        <Event event={event} key={event.id} />
      ))}
    </div>
  );
};

export default Events;
