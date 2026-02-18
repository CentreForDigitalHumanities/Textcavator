import { Subject } from 'rxjs';
import { FoundDocument } from './found-document';
import { CorpusField } from './corpus';
import * as _ from 'lodash';

export type DocumentView = 'content' | 'scan';

export interface DocumentFocus {
    document: FoundDocument;
    view: DocumentView;
}

export class DocumentPage {
    focus$ = new Subject<DocumentFocus>();

    constructor(
        public documents: FoundDocument[],
        public total: number,
        public fields?: CorpusField[],
        public from: number = 0,
    ) {
        this.documents.forEach((d, i) => d.position = i + 1);
    }

    focus(document: FoundDocument, view: DocumentView = 'content') {
        this.focus$.next({ document, view });
    }

    focusNext(document: FoundDocument) {
        this.focusShift(document, 1);
    }

    focusPrevious(document: FoundDocument) {
        this.focusShift(document, -1);
    }

    blur() {
        this.focus$.next(undefined);
    }

    /** set focus to a position relative to the given document */
    private focusShift(document: FoundDocument, shift: number) {
        this.focusPosition(document.position + shift);
    }

    /** focus on the document at the given position in the page */
    private focusPosition(position: number) {
        const index = _.clamp(position - 1, 0, this.documents.length - 1);
        this.focus(this.documents[index]);
    }
}
