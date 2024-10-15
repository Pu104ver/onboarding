import cn from 'classnames';
import {ReactNode, ButtonHTMLAttributes, HTMLAttributes, useState} from 'react';

import styles from './Button.module.scss';

import CheckMarkIcon from '@/shared/assets/checkmark.svg?react';
import CopyIcon from '@/shared/assets/copy.svg?react';
import Loader from '@/shared/ui/Loader';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'text';
  danger?: boolean;
  pressed?: boolean;
  loading?: boolean;
  copyable?: boolean | string;
  copyContent?: string;
  containerProps?: HTMLAttributes<HTMLDivElement>;
}

const Button = ({
  children,
  className,
  variant,
  disabled,
  containerProps,
  danger = false,
  pressed = false,
  loading = false,
  copyable = false,
  ...props
}: ButtonProps) => {
  const [isCopied, setIsCopied] = useState(false);

  const copyHandler = async (text: string) => {
    await navigator?.clipboard?.writeText(text);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const copy = () => {
    if (typeof copyable === 'string') {
      void copyHandler(copyable);
    } else if (typeof children === 'string') {
      void copyHandler(children);
    }
  };

  return (
    <div className={styles.container} {...containerProps}>
      <button
        className={cn(styles.button, className, {
          [styles.primary]: variant === 'primary',
          [styles.text]: variant === 'text',
          [styles.copyable]: copyable,
          [styles.pressed]: pressed,
          [styles.loading]: loading,
          [styles.danger]: danger,
        })}
        disabled={loading || disabled}
        {...props}>
        {loading && (
          <Loader
            className={cn({
              [styles.primaryLoader]: variant === 'primary',
            })}
          />
        )}
        {children}
      </button>

      {copyable && (
        <button onClick={copy} className={styles.copyBtn}>
          {isCopied ? (
            <CheckMarkIcon className={styles.copyIcon} />
          ) : (
            <CopyIcon className={styles.copyIcon} />
          )}
        </button>
      )}
    </div>
  );
};

export default Button;
