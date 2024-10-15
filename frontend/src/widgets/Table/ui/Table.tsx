import cn from 'classnames';
import {HTMLAttributes, ReactNode, TableHTMLAttributes, useEffect, useMemo, useState} from 'react';

import styles from './Table.module.scss';

import {ColumnsData} from '@/app/types/Employee';
import UpDownArrowIcon from '@/shared/assets/UpDownArrow.svg?react';
import {PAGES_LIMIT} from '@/shared/const/ApiConst';
import useInfinityScroll from '@/shared/hooks/useInfinityScroll';
import Button from '@/shared/ui/Button';
import Skeleton from '@/shared/ui/Skeleton';

interface ITableProps<RecordType = any> extends TableHTMLAttributes<HTMLTableElement> {
  columns: ColumnsData<RecordType>[];
  dataSource?: RecordType[];
  isFetching?: boolean;
  bordered?: boolean;
  render?: (text: ReactNode) => ReactNode;
  containerProps?: HTMLAttributes<HTMLDivElement>;
  isMaxCount?: boolean;
}

function Table({
  columns,
  dataSource,
  isFetching,
  isMaxCount,
  bordered,
  style,
  ...props
}: ITableProps) {
  const [filterDataSource, setFilterDataSource] = useState(dataSource || []);

  const countOfDisplayColumns = useMemo(() => columns.filter(({title}) => title).length, [columns]);

  useEffect(() => {
    dataSource && setFilterDataSource(dataSource);
  }, [dataSource]);

  const ref = useInfinityScroll(!!isFetching, !!isMaxCount);

  return (
    <table
      ref={ref}
      className={cn(styles.table, {
        [styles.bordered]: bordered,
        [styles.emptyTable]: !dataSource || dataSource.length === 0,
      })}
      style={{
        gridTemplateColumns: `repeat(${countOfDisplayColumns}, minmax(250px, 1fr))`,
        minHeight: filterDataSource.length === 0 ? 350 : 'auto',
        ...style,
      }}
      {...props}>
      <thead>
        <tr>
          {columns.map(
            ({key, title, align = 'left', sorter}) =>
              title && (
                <th key={`${key} - ${Math.random()}`}>
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
        {filterDataSource.length > 0 || isFetching ? (
          <>
            {filterDataSource &&
              filterDataSource.map(item => (
                <tr key={`${item.id} - ${Math.random()}`}>
                  {columns.map(
                    ({key, render, title, align = 'left'}, index) =>
                      title && (
                        <td
                          key={`${item.id} - ${index} - ${Math.random()}`}
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
              Array.from({length: PAGES_LIMIT})
                .fill(null)
                .map((_, index) => (
                  <tr key={index} className={styles.tableSkeleton}>
                    {Array.from({length: countOfDisplayColumns})
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
