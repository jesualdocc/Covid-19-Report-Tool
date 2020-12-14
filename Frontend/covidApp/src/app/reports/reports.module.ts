import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import {ReportsComponent} from './reports.component';
import {MatTabsModule} from '@angular/material/tabs';

const routes: Routes = [
  { path: '', component: ReportsComponent }
];

@NgModule({
  declarations: [ReportsComponent],
  imports: [
    CommonModule,
    MatTabsModule,
    RouterModule.forChild(routes)
  ],
  exports: [RouterModule]
})
export class ReportsModule { }
