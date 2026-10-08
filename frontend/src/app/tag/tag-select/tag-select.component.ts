import {
    AfterViewInit,
    Component,
    ElementRef,
    EventEmitter,
    Input,
    OnDestroy,
    Output,
    ViewChild,
} from '@angular/core';
import * as _ from 'lodash';
import { Observable, Subject } from 'rxjs';
import { Tag } from '@models';
import { TagService } from '@services/tag.service';
import { takeUntil } from 'rxjs/operators';
import { actionIcons, formIcons } from '@shared/icons';
import { DropdownComponent } from '@shared/dropdown/dropdown.component';

@Component({
    selector: 'ia-tag-select',
    templateUrl: './tag-select.component.html',
    styleUrls: ['./tag-select.component.scss'],
    standalone: false
})
export class TagSelectComponent implements AfterViewInit, OnDestroy {
    @Input() exclude: Tag[];
    @Output() selection = new EventEmitter<Tag>();
    @Output() cancel = new EventEmitter<void>();

    @ViewChild('newTagNameInput') newTagNameInput: ElementRef<HTMLInputElement>;
    @ViewChild('selectToggle') selectToggle: ElementRef<HTMLButtonElement>;

    tags$: Observable<Tag[]>;
    destroy$ = new Subject<void>();

    formIcons = formIcons;
    actionIcons = actionIcons;

    selectedTag: Tag;

    createMode = false;
    newTagName: string;

    constructor(private tagService: TagService) {
        this.tags$ = this.tagService.tags$;
    }

    ngAfterViewInit() {
        this.selectToggle.nativeElement.focus();
    }

    filterTags(tags: Tag[], exclude?: Tag[]): Tag[] {
        return _.differenceBy(tags, exclude || [], 'name');
    }

    addTag() {
        this.selection.emit(this.selectedTag);
        this.selectedTag = undefined;
    }

    createTag() {
        this.tagService
            .makeTag(this.newTagName)
            .pipe(takeUntil(this.destroy$))
            .subscribe((res) => {
                this.selection.emit(res);
                this.createMode = false;
            });
    }

    toggleCreate(): void {
        this.selectedTag = undefined;
        this.createMode = true;
        setTimeout(() => this.newTagNameInput.nativeElement.focus());
    }

    ngOnDestroy(): void {
        this.destroy$.next(undefined);
        this.destroy$.complete();
    }
}
