import {forwardRef, InputHTMLAttributes, ReactNode, Ref} from 'react';

import styles from './Switch.module.scss';

interface ISwitchProps extends InputHTMLAttributes<HTMLInputElement> {
  agreementText?: ReactNode;
  disagreementText?: ReactNode;
}

const Switch = forwardRef(
  ({agreementText, disagreementText, ...props}: ISwitchProps, ref: Ref<HTMLInputElement>) => {
    return (
      <div className={styles.switch}>
        {disagreementText && <>{disagreementText}</>}

        <div className={styles.container}>
          <input ref={ref} type="checkbox" className={styles.switchInput} {...props} />

          <span className={styles.switchSlider}>
            <span className={styles.switchSliderCheckmark}></span>
            <div className={styles.switchCircle} />
          </span>
        </div>

        {agreementText && <>{agreementText}</>}
      </div>
    );
  },
);

export default Switch;
