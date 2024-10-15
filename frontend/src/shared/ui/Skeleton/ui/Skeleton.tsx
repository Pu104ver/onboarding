import cn from 'classnames';
import {HTMLAttributes} from 'react';

import styles from './Skeleton.module.scss';

interface ISkeletonProps extends HTMLAttributes<HTMLDivElement> {
  block?: boolean;
  active?: boolean;
  variant?: 'circle';
}

const Skeleton = ({block, active, variant, className, ...props}: ISkeletonProps) => {
  return (
    <div
      className={cn(styles.wrapper, className, {
        [styles.block]: block,
        [styles.active]: active,
        [styles.circle]: variant === 'circle',
      })}
      {...props}
    />
  );
};

export default Skeleton;
