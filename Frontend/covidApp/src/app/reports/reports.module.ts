import { CovidpredictionsComponent } from './covidpredictions/covidpredictions.component';
import { MatSortModule } from '@angular/material/sort';
import { MatPaginatorModule } from '@angular/material/paginator';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import {ReportsComponent} from './reports.component';
import {MatTabsModule} from '@angular/material/tabs';
import { CovidtableComponent } from './covidtable/covidtable.component';
import { MatTableModule } from '@angular/material/table';
import {  MatFormFieldModule } from '@angular/material/form-field';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';

const routes: Routes = [
  { path: '', component: ReportsComponent }
];

@NgModule({
  declarations: [ReportsComponent,CovidtableComponent, CovidpredictionsComponent],
  imports: [
    CommonModule,
    MatTabsModule,
    MatTableModule,
    MatFormFieldModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatSortModule,
    RouterModule.forChild(routes)
  ],
  exports: [RouterModule]
})
export class ReportsModule { }
