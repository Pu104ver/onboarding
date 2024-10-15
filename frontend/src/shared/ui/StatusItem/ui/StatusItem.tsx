import style from './StatusItem.module.scss';

import {statusObjects, statusObjectsKeyType} from '@/shared/const/StatusItemsConst';

function StatusItem({text}: {text?: string}) {
  const status = (text as statusObjectsKeyType) || 'none';
  return (
    <div className={style.status}>
      {statusObjects[status]?.icon}
      <p className={style[status]}>{statusObjects[status]?.text}</p>
    </div>
  );
}

export default StatusItem;
