import {useEffect} from 'react';

export const useClickEsc = (isChange: boolean, setIsChange: (isChange: boolean) => void) => {
  useEffect(() => {
    const closeModalOnEsc = (e: KeyboardEvent) => {
      if (isChange && e.code === 'Escape') {
        setIsChange(false);
      }
    };

    document.addEventListener('keydown', closeModalOnEsc);

    return () => {
      document.removeEventListener('keydown', closeModalOnEsc);
    };
  }, [isChange]);
};
