export interface IErrorResponse {
  data: {
    [key: string]: string | string[];
  };
  status: number;
}
