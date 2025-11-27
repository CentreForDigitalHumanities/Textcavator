import { NgModule } from '@angular/core';
import { ElasticSearchService } from '@services';
import { SharedModule } from '@shared/shared.module';
import { DialogModule } from 'primeng/dialog';
import { CorpusModule } from '../corpus/corpus.module';
import { SearchRelevanceComponent } from '../search';
import { TagModule } from '../tag/tag.module';
import { ContentFieldPreviewComponent } from './content-field-preview/content-field-preview.component';
import { ContentFieldComponent } from './content-field/content-field.component';
import { DocumentPageComponent } from './document-page/document-page.component';
import { DocumentPopupComponent } from './document-popup/document-popup.component';
import { DocumentPreviewComponent } from './document-preview/document-preview.component';
import { DocumentViewComponent } from './document-view/document-view.component';
import { EntityLegendComponent } from './entity-legend/entity-legend.component';
import { EntityToggleComponent } from './entity-toggle/entity-toggle.component';
import { ImageViewModule } from './image-view/image-view.module';
import { MetadataFieldComponent } from './metadata-field/metadata-field.component';
import { DateRangePipe } from './pipes/date-range.pipe';
import { ElasticsearchHighlightPipe } from './pipes/elasticsearch-highlight.pipe';
import { EntityPipe } from './pipes/entity.pipe';
import { GeoDataPipe } from './pipes/geo-data.pipe';
import { KeywordPipe } from './pipes/keyword.pipe';
import { ParagraphPipe } from './pipes/paragraph.pipe';
import { SnippetPipe } from './pipes/snippet.pipe';

@NgModule({
    declarations: [
        DocumentViewComponent,
        DocumentPageComponent,
        SearchRelevanceComponent,
        DocumentPopupComponent,
        DocumentPreviewComponent,
        EntityLegendComponent,
        EntityToggleComponent,
        MetadataFieldComponent,
        ElasticsearchHighlightPipe,
        EntityPipe,
        GeoDataPipe,
        ParagraphPipe,
        SnippetPipe,
        ContentFieldPreviewComponent,
        KeywordPipe,
        ContentFieldComponent,
        DateRangePipe,
    ],
    imports: [
        DialogModule,
        CorpusModule,
        SharedModule,
        ImageViewModule,
        TagModule,
    ], exports: [
        DocumentPreviewComponent,
        DocumentPageComponent,
        DocumentPopupComponent,
    ],
    providers: [
        ElasticSearchService,
    ]
})
export class DocumentModule { }
