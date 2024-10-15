import cn from 'classnames';
import {HTMLAttributes, ReactNode, useCallback, useRef, useState} from 'react';

import styles from './Dropdown.module.scss';

import {useClickOutside} from '@/shared/hooks/useClickOutside.hook';

interface IDropdownProps extends Omit<HTMLAttributes<HTMLDivElement>, 'content'> {
  children: ReactNode;
  content?: ReactNode;
  placement?: 'left' | 'right';
  buttonProps?: HTMLAttributes<HTMLButtonElement>;
}

const Dropdown = ({
  children,
  content,
  placement = 'right',
  buttonProps,
  ...props
}: IDropdownProps) => {
  const contentRef = useRef<HTMLDivElement>(null);
  const [isAnimationActive, setIsAnimationActive] = useState(false);
  const [isVisibleContent, setIsVisibleContent] = useState(false);

  const handleDropdownVisible = () => {
    if (isVisibleContent) {
      setIsAnimationActive(false);

      if (isAnimationActive) {
        setTimeout(() => {
          setIsVisibleContent(false);
        }, 300);
      }
    } else {
      setIsVisibleContent(true);

      if (!isAnimationActive) {
        setIsAnimationActive(true);
      }
    }
  };

  const handleClose = useCallback(() => {
    setIsAnimationActive(false);

    setTimeout(() => {
      setIsVisibleContent(false);
    }, 300);
  }, []);

  useClickOutside(contentRef, handleClose, isAnimationActive && isVisibleContent);

  return (
    <div className={styles.container} {...props}>
      <button type="button" className={styles.btn} onClick={handleDropdownVisible} {...buttonProps}>
        {children}
      </button>

      {isVisibleContent && (
        <div
          ref={contentRef}
          className={cn(styles.dropdownContainer, {
            [styles.hidden]: !isAnimationActive,
            [styles[placement]]: placement,
          })}>
          <div className={cn(styles.content, {[styles.hiddenContent]: !isAnimationActive})}>
            {content}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dropdown;
