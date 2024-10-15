import {format} from 'date-fns';

import style from './Comment.module.scss';

import {CommentResponse} from '@/app/types/Employee';
import {RUS_DATE_WITH_TIME} from '@/shared/const/DateStrings';

const Comment = ({author_fullname, text, created_at}: CommentResponse) => {
  return (
    <div className={style.comment}>
      <div className={style.commentHeader}>
        <h4>Автор:{author_fullname}</h4>
        <h4>•</h4>
        <h4>{format(created_at, RUS_DATE_WITH_TIME)}</h4>
      </div>

      <p>{text}</p>
    </div>
  );
};

export default Comment;
