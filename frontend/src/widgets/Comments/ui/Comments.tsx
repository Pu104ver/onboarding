import style from './Comments.module.scss';

import {useGetCommentsForEmployee} from '@/features/EmployeeCommentsOperations/model/EmployeeCommentsOperations';
import {AddCommentBlock} from '@/features/EmployeeCommentsOperations/ui';
import Comment from '@/shared/ui/Comment';

interface CommentProps {
  id?: string;
}
const Comments = ({id}: CommentProps) => {
  const {data: comments} = useGetCommentsForEmployee(id);
  return (
    <div className={style.comments}>
      <h3>Комментарии по сотруднику</h3>
      <AddCommentBlock id={id} />
      {comments?.map((comment, key) => <Comment {...comment} key={key} />)}
    </div>
  );
};

export default Comments;
