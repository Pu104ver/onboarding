import cn from 'classnames';
import {
  Dispatch,
  HTMLAttributes,
  ReactNode,
  SetStateAction,
  TableHTMLAttributes,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

import styles from './Table.module.scss';

import {ColumnsData} from '@/app/types/Employee';
import UpDownArrowIcon from '@/shared/assets/UpDownArrow.svg?react';
import {useQueryParams} from '@/shared/hooks/useQueryParams.hook';
import Button from '@/shared/ui/Button';
import Skeleton from '@/shared/ui/Skeleton';

interface ITableProps<RecordType = any> extends TableHTMLAttributes<HTMLTableElement> {
  columns: ColumnsData<RecordType>[];
  dataSource?: RecordType[];
  isFetching?: boolean;
  setPage?: Dispatch<SetStateAction<number>>;
  bordered?: boolean;
  render?: (text: ReactNode) => ReactNode;
  containerProps?: HTMLAttributes<HTMLDivElement>;
  isMaxCount?: boolean;
}

function Table({
  columns,
  dataSource,
  isFetching,
  setPage,
  isMaxCount,
  bordered,
  style,
  ...props
}: ITableProps) {
  const [filterDataSource, setFilterDataSource] = useState(dataSource || []);
  const tableRef = useRef<HTMLTableElement>(null);
  const {queryParams} = useQueryParams();

  const countOfDisplayColumns = useMemo(() => columns.filter(({title}) => title).length, [columns]);

  useEffect(() => {
    dataSource && setFilterDataSource(dataSource);
  }, [dataSource]);

  useEffect(() => {
    setPage && setPage(1);
  }, [queryParams, setPage]);

  const scrollHandler = useCallback(() => {
    if (tableRef.current) {
      if (
        tableRef.current.scrollHeight -
          (tableRef?.current.scrollTop + tableRef?.current.clientHeight) <=
        1
      ) {
        if (setPage && !isFetching && !isMaxCount) {
          setPage(p => p + 1);
        }
      }
    }
  }, [setPage, isFetching, isMaxCount]);

  return (
    <table
      className={cn(styles.table, {
        [styles.bordered]: bordered,
        [styles.emptyTable]: !dataSource || dataSource.length === 0,
      })}
      style={{
        gridTemplateColumns: `repeat(${countOfDisplayColumns}, minmax(200px, 1fr))`,
        ...style,
      }}
      onScroll={scrollHandler}
      ref={tableRef}
      {...props}>
      <thead>
        <tr>
          {columns.map(
            ({key, title, align = 'left', sorter}) =>
              title && (
                <th key={key}>
                  <div className={styles.titleBlock}>
                    <div
                      className={cn(styles.titleContainer, {
                        [styles[align]]: align,
                      })}>
                      <span>{title}</span>

                      {sorter && (
                        <Button variant="text" className={styles.upDownBtn}>
                          <UpDownArrowIcon />
                        </Button>
                      )}
                    </div>
                  </div>
                </th>
              ),
          )}
        </tr>
      </thead>

      <tbody>
        {filterDataSource?.length > 0 || isFetching ? (
          <>
            {filterDataSource?.length > 0 &&
              filterDataSource.map(item => (
                <tr key={item.id}>
                  {columns.map(
                    ({key, render, title, align = 'left'}, id) =>
                      title && (
                        <td
                          key={`${item.id}${id}`}
                          className={cn({
                            [styles[align]]: align,
                          })}>
                          {render ? render(item[key], item) : item[key]}
                        </td>
                      ),
                  )}
                </tr>
              ))}

            {isFetching &&
              Array.from({length: 5})
                .fill(null)
                .map((_, index) => (
                  <tr key={index} className={styles.tableSkeleton}>
                    {Array.from({length: columns.length})
                      .fill(null)
                      .map((_, i) => (
                        <td key={`${index}-${i}`}>
                          <Skeleton block />
                        </td>
                      ))}
                  </tr>
                ))}
          </>
        ) : (
          <tr className={styles.emptyRow}></tr>
        )}
      </tbody>
    </table>
  );
}

export default Table;
