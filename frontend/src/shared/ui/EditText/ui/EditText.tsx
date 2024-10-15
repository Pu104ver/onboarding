import {useEffect, useState} from 'react';

import style from './EditText.module.scss';

import CheckMarkIcon from '@/shared/assets/checkmark.svg?react';
import PenIcon from '@/shared/assets/pencil.svg?react';
import XIcon from '@/shared/assets/x.svg?react';
import {useClickEsc} from '@/shared/hooks/useClickEsc.hook';
import Input from '@/shared/ui/Input';
interface EditProps {
  field: string;
  initialText?: string;
  id?: number | string;
  changeData: (field: string, text: string) => void;
}
const EditText = ({field, initialText, changeData}: EditProps) => {
  const [isChange, setIsChange] = useState(false);
  const [text, setText] = useState(initialText);

  useEffect(() => {
    setText(initialText);
  }, [initialText]);

  useClickEsc(isChange, setIsChange);

  const closeEdit = () => {
    setIsChange(false);
    setText(initialText);
  };

  const handleChange = () => {
    text && changeData(field, text);
    setText(text);
  };

  return (
    <div className={style.Edit}>
      {isChange ? (
        <div className={style.editTools}>
          <Input maxLength={50} value={text} onChange={e => setText(e.target.value)} />
          <XIcon onClick={closeEdit} />
          <CheckMarkIcon
            className={style.checkmark}
            onClick={() => {
              setIsChange(false);
              handleChange();
            }}
          />
        </div>
      ) : (
        <>
          {text}
          <PenIcon className={style.icon} onClick={() => setIsChange(true)} />
        </>
      )}
    </div>
  );
};

export default EditText;
