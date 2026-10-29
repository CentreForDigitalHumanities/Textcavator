import { FreqTableHeader } from "@app/models";
import _ from "lodash";

export const wideFormatAvailable = (headers?: FreqTableHeader[]): boolean => {
    return !!headers?.find(header => header.isMainFactor);
}

export const transformWideFormat = (
    data: object[],
    headers: FreqTableHeader[],
): [FreqTableHeader[], object[]] =>  {
        const mainFactor = headers.find(header => header.isMainFactor);

        const mainFactorValues = _.uniqBy(
            data.map(row => row[mainFactor.key]),
            value => formatValue(value, mainFactor)
        );

        const newHeaders = wideFormatHeaders(headers, mainFactor, mainFactorValues);

        // other factors
        const factorColumns = filterFactors(newHeaders);

        const newData = _.uniqBy(
            data,
            row => {
                const factorValues = factorColumns.map(column => getValue(row, column));
                return _.join(factorValues, '/');
            }
        );

        mainFactorValues.forEach(factorValue => {
            const filteredData = data.filter(row => getValue(row, mainFactor) === formatValue(factorValue, mainFactor));

            newData.forEach(newRow => {
                headers.forEach(header => {
                    if (! header.isSecondaryFactor) {
                        const key = wideFormatColumnKey(header, mainFactor, factorValue);

                        const rowData = filteredData.find(row =>
                            _.every(
                                factorColumns,
                                factor => getValue(row, factor) === getValue(newRow, factor)
                            )
                        );

                        if (rowData !== undefined) {
                            const value = rowData[header.key];
                            newRow[key] = value;
                        }
                    }
                });
            });
        });

        return [newHeaders, newData];
}

const wideFormatHeaders = (headers: FreqTableHeader[], mainFactor: FreqTableHeader, factorValues: any[]) => {
    const newLabel = (header: FreqTableHeader, factor: FreqTableHeader, factorValue) =>
        `${header.label} (${formatValue(factorValue, factor)})`;

    const otherHeaders = headers.filter((header, index) => header.key !== mainFactor.key);
    const newHeaders: FreqTableHeader[] = _.flatMap(otherHeaders, header => {
        if (header.isSecondaryFactor) {
            // other factors are kept as-is
            return [header];
        } else {
            // for non-factor headers, make one column for each value of `mainFactor`
            return _.map(factorValues, value => (
                {
                    label: newLabel(header, mainFactor, value),
                    key: wideFormatColumnKey(header, mainFactor, value),
                    format: header.format,
                    formatDownload: header.formatDownload,
                } as FreqTableHeader
            ));
        }
    });

    return newHeaders;
}

const wideFormatColumnKey = (header: FreqTableHeader, mainFactor: FreqTableHeader, mainFactorValue): string => {
    return `${header.key}###${formatValue(mainFactorValue, mainFactor)}`;
}

const filterFactors = (headers: FreqTableHeader[]): FreqTableHeader[] => {
    return headers.filter(header => header.isSecondaryFactor);
}


export const formatValue = (value, column: FreqTableHeader, download = false) => {
    if (download && column.formatDownload) {
        return column.formatDownload(value);
    }
    if (column.format) {
        return column.format(value);
    }
    return value;
}


export const getValue = (row: object, column: FreqTableHeader, download = false) => {
    return formatValue(row[column.key], column, download);
}
