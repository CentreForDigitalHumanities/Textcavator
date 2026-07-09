/* eslint-disable quotes */
import { Component, ElementRef, EventEmitter, Input, Output, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import embed, { VisualizationSpec } from 'vega-embed';

import { Corpus, CorpusField, GeoDocument, GeoLocation, QueryModel } from '@models';
import { VisualizationService } from '@services';
import { MapDataResults } from '@models/map-data';
import { RouterStoreService } from 'app/store/router-store.service';


@Component({
    selector: 'ia-map',
    templateUrl: './map.component.html',
    styleUrls: ['./map.component.scss'],
    standalone: false
})
export class MapComponent implements OnChanges {
    @ViewChild('vegaMap') vegaMap!: ElementRef;
    @Input() visualizedField: CorpusField;
    @Input() queryModel: QueryModel;
    @Input() corpus: Corpus;
    @Input() resultsCount: number;
    @Input() asTable: boolean;

    @Output() mapError = new EventEmitter();

    mapCenter: GeoLocation | null;
    results: GeoDocument[];

    isLoading$ = new BehaviorSubject<boolean>(false);

    mapColors = {
        landStroke: {
            light: '#BDAE8A',
            dark: '#6c5a46',
        },
        landFill: {
            light: '#E5D3B3',
            dark: '#4d3e2e',
        },
    };

    private mapDataResults: MapDataResults;

    constructor(
        private routerStoreService: RouterStoreService,
        private visualizationService: VisualizationService
    ) { }

    get readyToLoad() {
        return (
            this.corpus &&
            this.visualizedField &&
            this.queryModel
        );
    }


    ngOnChanges(changes: SimpleChanges) {
        if (this.readyToLoad) {

            if (changes.corpus || changes.visualizedField || changes.queryModel) {
                this.mapDataResults?.complete();

                this.mapDataResults = new MapDataResults(
                    this.routerStoreService,
                    this.queryModel,
                    this.visualizationService
                );

                this.mapDataResults.result$.subscribe(data => {
                    this.results = data.geoDocuments;
                    this.mapCenter = data.mapCenter;
                    this.renderChart();
                });


                this.mapDataResults.error$.subscribe(error => this.emitError(error));
            }
        }
    }


    ngOnDestroy(): void {
        this.mapDataResults?.complete();
    }


    getVegaSpec(): VisualizationSpec {
        // Returns a Vega map specification
        // Uses pan/zoom signals from https://vega.github.io/vega/examples/zoomable-world-map/
        return {
            "$schema": "https://vega.github.io/schema/vega/v6.json",
            "description": "An interactive map supporting pan and zoom.",
            "width": { "signal": "width" },
            "height": { "signal": "height" },
            "autosize": "none",

            "signals": [
                {
                    name: "corpusName",
                    value: this.corpus.name
                },
                { "name": "tx", "update": "width / 2" },
                { "name": "ty", "update": "height / 2" },
                {
                    "name": "scale",
                    "value": 500,
                    "on": [{
                        "events": { "type": "wheel", "consume": true },
                        "update": "clamp(scale * pow(1.0005, -event.deltaY * pow(16, event.deltaMode)), 150, 3000)"
                    }]
                },
                {
                    "name": "angles",
                    "value": [0, 0],
                    "on": [{
                        "events": "pointerdown",
                        "update": "[rotateX, centerY]"
                    }]
                },
                {
                    "name": "cloned",
                    "value": null,
                    "on": [{
                        "events": "pointerdown",
                        "update": "copy('projection')"
                    }]
                },
                {
                    "name": "start",
                    "value": null,
                    "on": [{
                        "events": "pointerdown",
                        "update": "invert(cloned, xy())"
                    }]
                },
                {
                    "name": "drag", "value": null,
                    "on": [{
                        "events": "[pointerdown, window:pointerup] > window:pointermove",
                        "update": "invert(cloned, xy())"
                    }]
                },
                {
                    "name": "delta", "value": null,
                    "on": [{
                        "events": { "signal": "drag" },
                        "update": "[drag[0] - start[0], start[1] - drag[1]]"
                    }]
                },
                {
                    "name": "rotateX", "value": 0,
                    "on": [{
                        "events": { "signal": "delta" },
                        "update": "angles[0] + delta[0]"
                    }]
                },
                {
                    "name": "centerY", "value": this.mapCenter.location.lat,
                    "on": [{
                        "events": { "signal": "delta" },
                        "update": "clamp(angles[1] + delta[1], -60, 60)"
                    }]
                },
                {
                    'name': 'theme',
                    'description': 'Current site theme (light/dark)',
                    'bind': {
                        'element': '#current-theme',
                    }
                },
            ],

            "projections": [
                {
                    "name": "projection",
                    "type": "mercator",
                    "scale": { "signal": "scale" },
                    "rotate": [{ "signal": "rotateX" }, 0, 0],
                    "center": [this.mapCenter.location.lon, { "signal": "centerY" }],
                    "translate": [{ "signal": "tx" }, { "signal": "ty" }],
                }
            ],

            "data": [
                {
                    "name": "world",
                    "url": "assets/world-atlas/land-110m.json",
                    "format": {
                        "type": "topojson",
                        "mesh": "land",
                        "filter": "exterior"
                    }
                },
                {
                    "name": "points",
                    "format": { "type": "json" },
                    "values": this.results
                }
            ],

            "marks": [
                {
                    "type": "shape",
                    "from": { "data": "world" },
                    "encode": {
                        "enter": {
                            "strokeWidth": { "value": 0.75 },
                        },
                        "update": {
                            "fill": {'signal': `theme === "dark" ? "${this.mapColors.landFill.dark}" : "${this.mapColors.landFill.light}"`},
                            "stroke": {'signal': `theme === "dark" ? "${this.mapColors.landStroke.dark}" : "${this.mapColors.landStroke.light}"`},
                        }
                    },
                    "transform": [
                        { "type": "geoshape", "projection": "projection" }
                    ]
                },
                {
                    "type": "shape",
                    "from": { "data": "points" },
                    "encode": {
                        "enter": {
                            "width": { "value": 3 },
                            "height": { "value": 3 },
                            "fill": { "value": "#303F9F" },
                            "stroke": { "value": "grey" },
                            "tooltip": { "field": "properties.id" },
                            "href": { "signal": "'/document/' + corpusName + '/' + datum.properties.id" },
                        },
                    },
                    "transform": [
                        {
                            "type": "geoshape",
                            "projection": "projection",
                        }
                    ]
                }
            ]
        };
    }



    async renderChart(): Promise<void> {
        const spec = this.getVegaSpec();
        const aspectRatio = 2 / 3;
        const width = this.vegaMap.nativeElement.offsetWidth;
        const height = width * aspectRatio;

        try {
            await embed(this.vegaMap.nativeElement, spec, {
                mode: 'vega',
                renderer: 'canvas',
                width: width,
                height: height,
                actions: false,
                tooltip: true,
            });
        } catch (error) {
            this.emitError(error);
        }
    }

    emitError(error: { message: string }) {
        this.mapError.emit(error?.message);
    }

}
