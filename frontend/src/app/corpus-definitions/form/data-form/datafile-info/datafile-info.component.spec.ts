import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DatafileInfoComponent } from './datafile-info.component';
import { SharedModule } from '@shared/shared.module';
import { dataFileFactory } from 'mock-data/corpus-definition';

describe('DatafileInfoComponent', () => {
    let component: DatafileInfoComponent;
    let fixture: ComponentFixture<DatafileInfoComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [DatafileInfoComponent],
            imports: [SharedModule],
        })
            .compileComponents();

        fixture = TestBed.createComponent(DatafileInfoComponent);
        component = fixture.componentInstance;
        component.currentDataFile = dataFileFactory();
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
