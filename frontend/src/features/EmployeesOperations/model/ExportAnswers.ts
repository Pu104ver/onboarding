import Cookies from 'js-cookie';

import {IExportAnswersRequest} from '@/app/types/Employee';

interface IError extends Response {
  detail: {
    error: string;
  };
  error: string;
}

export const exportAnswers = async ({
  employee,
  target_employee = [],
  filename = '',
}: IExportAnswersRequest) => {
  try {
    const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}export-answers/`, {
      method: 'POST',
      headers: {
        'Content-type': 'application/json',
        Authorization: `Token ${Cookies.get('token')}`,
      },
      body: JSON.stringify({
        employee: [+employee],
        target_employee,
        file_format: 'xlsx',
      }),
    });

    if (!response.ok) {
      throw new Error(JSON.stringify(await response.json()));
    }

    const formattedResponse = await response.blob();
    const blobFile = new Blob([formattedResponse], {
      type: response.headers.get('Content-type') as string,
    });

    const url = URL.createObjectURL(blobFile);

    Object.assign(document.createElement('a'), {
      href: url,
      download: filename,
    }).click();

    URL.revokeObjectURL(url);

    return {
      ...response,
      ok: true,
      data: url,
    };
  } catch (err) {
    if (typeof err === 'string') {
      const response = JSON.parse(err) as IError;

      return {
        ...response,
        data: null,
      };
    } else if ((JSON.parse((err as Error).message) as IError).detail) {
      return JSON.parse((err as Error).message) as IError;
    } else {
      return {
        ok: false,
        data: null,
        detail: {
          error: 'Некорректный идентификатор сотрудника',
        },
        statusText: 'Некорректный идентификатор сотрудника',
      };
    }
  }
};
