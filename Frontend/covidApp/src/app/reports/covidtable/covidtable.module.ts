import { MatInputModule } from '@angular/material/input';
import { CovidtableComponent } from './covidtable.component';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table/';
import { MatPaginator } from '@angular/material/paginator';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { RouterModule, Routes } from '@angular/router';
import { FlexLayoutModule } from '@angular/flex-layout';

const routes: Routes = [
  { path: '', component: CovidtableComponent }
];


@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    MatPaginator,
    MatTableModule,
    MatFormFieldModule,
    MatSortModule,
    MatInputModule,
    FlexLayoutModule,
    RouterModule.forChild(routes)
  ],
  exports: [RouterModule]
})
export class CovidtableModule { }
