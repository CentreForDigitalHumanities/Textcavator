import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { commonTestBed } from '@app/common-test-bed';

import { DownloadHistoryComponent } from './download-history.component';
import { Download } from '@app/models';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

describe('DownloadHistoryComponent', () => {
    let component: DownloadHistoryComponent;
    let fixture: ComponentFixture<DownloadHistoryComponent>;

    beforeEach(waitForAsync(() => {
        commonTestBed().testingModule.compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(DownloadHistoryComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('opens options modal', () => {
        let modalService = TestBed.inject(NgbModal);
        expect(modalService.hasOpenModals()).toBe(false);

        const download: Download = {
            id: 1,
            download_type: 'search_results',
            started: new Date(2026, 1, 1),
            corpus: 'troonredes',
            parameters: {
                corpus: 'troonredes',
                fields: ['content'],
                route: '/search/troonredes',
                extra: [],
                es_query: { query: { match_all: {} } }
            },
            status: 'done',
        };
        component.downloads = [download];
        component.showOptions(download);

        expect(modalService.hasOpenModals()).toBe(true);
    });
});
