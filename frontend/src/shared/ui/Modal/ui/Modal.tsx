import classNames from 'classnames';
import {ReactNode, useEffect, useState} from 'react';

import style from './Modal.module.scss';

import CloseIcon from '@/shared/assets/x.svg?react';

interface ModalProps {
  isOpened: boolean;
  title?: ReactNode;
  icon?: ReactNode;
  children?: ReactNode;
  onClose?: () => void;
}
const Modal = ({isOpened = false, title, icon, children, onClose}: ModalProps) => {
  const [closing, setClosing] = useState(false);

  const onContentClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  const closeHandler = () => {
    if (onClose) {
      setClosing(true);

      setTimeout(() => {
        onClose();
        setClosing(false);
      }, 200);
    }
  };

  useEffect(() => {
    const closeModalOnEsc = (e: KeyboardEvent) => {
      if (isOpened && onClose && e.code === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', closeModalOnEsc);

    return () => {
      document.removeEventListener('keydown', closeModalOnEsc);
    };
  }, [isOpened, onClose]);

  return (
    <div
      className={classNames(style.modal, {
        [style.opened]: isOpened,
        [style.closing]: closing,
      })}>
      <div className={style.overlay} onClick={closeHandler}>
        <div className={style.content} onClick={onContentClick}>
          <div className={style.header}>
            {title && <h1 className={style.title}>{title}</h1>}
            <button className={style.closeBtn} onClick={closeHandler}>
              {icon ? icon : <CloseIcon />}
            </button>
          </div>

          <div className={style.body}>{children}</div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
