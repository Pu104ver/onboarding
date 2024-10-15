import cn from 'classnames';
import {HTMLAttributes} from 'react';

import styles from './Loader.module.scss';

interface ILoaderProps extends HTMLAttributes<HTMLDivElement> {
  size?: number | string;
}

const Loader = ({size = 16, className, ...props}: ILoaderProps) => {
  return (
    <div style={{width: size, height: size}} className={cn(styles.loader, className)} {...props} />
  );
};

export default Loader;
