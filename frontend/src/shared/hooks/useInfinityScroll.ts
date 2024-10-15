import {useEffect, useRef} from 'react';

import {DISTANCE_TO_TABLE_BOTTOM_TO_FETCH, PAGES_LIMIT} from '../const/ApiConst';

import {useAppDispatch, useAppSelector} from '@/app/store/hooks';
import {selectOffset, setOffset} from '@/app/store/slices/filters';

const useInfinityScroll = (isFetching: boolean, isMaxCount: boolean) => {
  const dispatch = useAppDispatch();
  const offset = useAppSelector(selectOffset);

  const ref = useRef<HTMLTableElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const onScroll = () => {
      if (!ref.current) return;

      //ref.current.scrollHeight - общая высота таблицы (включая то, что не видно, если есть прокрутка)
      //ref.current.scrollTop = расстояние, насколько проскролили
      //ref.current.clientHeight — высота видимой части таблицы (то есть высота контейнера, которую видит пользователь).

      //40 - константа, на каком расстоянии (в пикселях) от конца таблицы запрашивать новые данные
      const scrolledToBottom =
        ref.current.scrollHeight - ref.current.scrollTop - ref.current.clientHeight <
        DISTANCE_TO_TABLE_BOTTOM_TO_FETCH;

      if (!isMaxCount && scrolledToBottom && !isFetching) {
        dispatch(setOffset(offset + PAGES_LIMIT));
      }
    };

    ref.current.addEventListener('scroll', onScroll);

    return () => {
      if (!ref.current) return;
      ref.current.removeEventListener('scroll', onScroll);
    };
  }, [isFetching, ref.current]);

  return ref;
};

export default useInfinityScroll;
