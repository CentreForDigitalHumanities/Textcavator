import { Component, Input, OnDestroy, Output } from '@angular/core';
import {
    APICorpusDefinitionField,
    CorpusDataFile,
    FIELD_TYPE_OPTIONS,
} from '@models/corpus-definition';
import { isNil } from 'lodash';
import { Subject } from 'rxjs';

@Component({
    selector: 'ia-datafile-info',
    templateUrl: './datafile-info.component.html',
    styleUrl: './datafile-info.component.scss',
    standalone: false,
})
export class DatafileInfoComponent implements OnDestroy {
    @Input({ required: true }) currentDataFile!: CorpusDataFile;
    @Input({ required: false }) newDataFile: CorpusDataFile;

    @Output() onCurrentSelected = new Subject<void>();
    @Output() onNewSelected = new Subject<void>();

    isNil = isNil;

    fieldTypeLabel(value: APICorpusDefinitionField['type']) {
        return FIELD_TYPE_OPTIONS.find((option) => option.value == value)
            ?.label;
    }

    selectFile(output: Subject<void>): void {
        output.next();
    }

    ngOnDestroy(): void {
        this.onCurrentSelected.complete();
        this.onNewSelected.complete();
    }
}
