import cn from 'classnames';
import {forwardRef, HTMLAttributes, InputHTMLAttributes, Ref} from 'react';

import styles from './Checkbox.module.scss';

interface ICheckboxProps extends InputHTMLAttributes<HTMLInputElement> {
  containerProps?: HTMLAttributes<HTMLDivElement>;
}

const Checkbox = forwardRef(
  ({children, containerProps, className, ...props}: ICheckboxProps, ref: Ref<HTMLInputElement>) => {
    return (
      <div {...containerProps} className={cn(styles.container, containerProps?.className)}>
        <input ref={ref} type="checkbox" className={cn(styles.input, className)} {...props} />
        {children && <span className={styles.btn}>{children}</span>}
      </div>
    );
  },
);

export default Checkbox;
