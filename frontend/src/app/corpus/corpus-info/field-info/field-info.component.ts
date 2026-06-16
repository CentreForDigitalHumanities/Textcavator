import { Component, Input, OnInit } from '@angular/core';
import { CorpusField } from '@models';
import * as _ from 'lodash';

@Component({
    selector: 'ia-field-info',
    templateUrl: './field-info.component.html',
    styleUrls: ['./field-info.component.scss'],
    standalone: false
})
export class FieldInfoComponent implements OnInit {
    @Input({ required: true }) field!: CorpusField;
    @Input() coverage?: number;
    @Input() cardinality?: number;

    mappingNames: Record<string, string> = {
        text: 'text',
        keyword: 'categorical',
        integer: 'numeric',
        float: 'numeric',
        date: 'date',
        boolean: 'binary'
    };

    constructor() { }

    get coveragePercentage() {
        if (this.coverage) {
            return (this.coverage * 100).toPrecision(3);
        } else {
            return this.coverage; // return undefined or 0 as-is
        }
    }

    ngOnInit(): void {
    }

}
