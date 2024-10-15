import cn from 'classnames';
import {InputHTMLAttributes, ReactNode, Ref, forwardRef} from 'react';

import style from './Input.module.scss';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement | HTMLTextAreaElement> {
  icon?: ReactNode;
  loading?: boolean;
  isMulti?: boolean;
}
const Input = forwardRef(function Input(
  {isMulti, icon, className, loading, disabled, ...props}: InputProps,
  ref: Ref<HTMLInputElement>,
) {
  return (
    <div
      className={cn(style.CustomInput, className, {
        [style.loading]: loading,
      })}>
      {icon && <div className={style.icon}>{icon}</div>}
      {isMulti ? (
        <textarea disabled={loading || disabled} {...props} />
      ) : (
        <input disabled={loading || disabled} {...props} ref={ref} />
      )}
    </div>
  );
});

export default Input;
