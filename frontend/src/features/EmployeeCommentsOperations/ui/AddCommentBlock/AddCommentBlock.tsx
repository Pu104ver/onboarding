import {useState} from 'react';

import {useCreateCommentForEmployee} from '../../model/EmployeeCommentsOperations';

import style from './AddCommentBlock.module.scss';

import {useAppSelector} from '@/app/store/hooks';
import {userSelector} from '@/entities/User/model/selectors/GetUser';
import PencilIcon from '@/shared/assets/pencil.svg?react';
import XIcon from '@/shared/assets/x.svg?react';
import Button from '@/shared/ui/Button';
import Input from '@/shared/ui/Input';

interface AddCommentBlockProps {
  id?: string;
}

const AddCommentBlock = ({id}: AddCommentBlockProps) => {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState('');
  const {id: author} = useAppSelector(userSelector);

  const [addCommentForEmployee] = useCreateCommentForEmployee();

  const addComment = () => {
    void addCommentForEmployee({author: author, employee: id, text: text});
    setOpen(false);
    setText('');
  };
  return (
    <>
      {!open ? (
        <Button onClick={() => setOpen(true)}>
          <PencilIcon />
          <p>Добавить комментарий</p>
        </Button>
      ) : (
        <div className={style.AddCommentBlock}>
          <div>
            <Input isMulti value={text} onChange={e => setText(e.target.value)} />
            <div className={style.tools}>
              <Button onClick={addComment}>Отправить</Button>
              <XIcon
                className={style.xIcon}
                onClick={() => {
                  setOpen(false);
                  setText('');
                }}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AddCommentBlock;
