import {RefObject, useEffect} from 'react';

export const useClickOutside = (
  ref: RefObject<HTMLElement>,
  callback: () => void,
  additionalCondition: boolean = true,
) => {
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as HTMLDivElement) && additionalCondition) {
        callback();
      }
    };

    if (additionalCondition) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [ref, callback, additionalCondition]);
};
