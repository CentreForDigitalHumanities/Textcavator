import { NgModule } from '@angular/core';
import { WordmodelsService } from '@services';
import { SharedModule } from '@shared/shared.module';
import { CorpusModule } from '../corpus/corpus.module';
import { VisualizationModule } from '../visualization/visualization.module';
import { QueryFeedbackComponent } from './query-feedback/query-feedback.component';
import { RelatedWordsComponent } from './related-words/related-words.component';
import { SimilarityChartComponent } from './similarity-chart/similarity-chart.component';
import { TimeIntervalSliderComponent } from './similarity-chart/time-interval-slider/time-interval-slider.component';
import { WordModelsComponent } from './word-models.component';
import { WordSimilarityComponent } from './word-similarity/word-similarity.component';
import { NeighborNetworkComponent } from './neighbor-network/neighbor-network.component';


@NgModule({
    providers: [
        WordmodelsService,
    ],
    declarations: [
        WordModelsComponent,
        QueryFeedbackComponent,
        RelatedWordsComponent,
        WordSimilarityComponent,
        SimilarityChartComponent,
        TimeIntervalSliderComponent,
        NeighborNetworkComponent,
    ], exports: [
        WordModelsComponent,
    ],
    imports: [
        CorpusModule,
        SharedModule,
        VisualizationModule,
    ],
})
export class WordModelsModule { }
