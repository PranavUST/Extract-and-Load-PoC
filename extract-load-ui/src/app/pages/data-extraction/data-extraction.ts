import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { SourceConfig } from './source-config/source-config';
import { TargetConfig } from './target-config/target-config';
import { TemplateList } from './template-list/template-list';

@Component({
  standalone: true,
  selector: 'app-data-extraction',
  templateUrl: './data-extraction.html',
  imports: [
    CommonModule,
    MatTabsModule,
    SourceConfig,
    TargetConfig,
    TemplateList
  ]
})
export class DataExtraction {}
