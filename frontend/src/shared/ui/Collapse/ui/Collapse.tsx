import cn from 'classnames';
import {useState} from 'react';

import styles from './Collapse.module.scss';

import {ICollapse} from '@/app/types/Collapse.type';
import ArrowIcon from '@/shared/assets/arrow.svg?react';

const Collapse = ({
  title,
  children,
  icon,
  defaultHidden,
  className,
  isRevert,
  ...props
}: ICollapse) => {
  const [isHidden, setIsHidden] = useState(defaultHidden ?? false);

  const handleHide = () => {
    setIsHidden(prev => !prev);
  };

  return (
    <div className={cn(styles.wrapper, className)} {...props}>
      <button className={cn(styles.btn, {[styles.revert]: isRevert})} onClick={handleHide}>
        {icon ? (
          icon
        ) : (
          <span
            className={cn(styles.icon, {
              [styles.collapsedIcon]: !isHidden,
            })}>
            <ArrowIcon />
          </span>
        )}

        <div className={styles.title}>{title}</div>
      </button>

      <div
        className={cn(styles.body, {
          [styles.hidden]: isHidden,
        })}>
        {!isHidden && children}
      </div>
    </div>
  );
};

export default Collapse;
