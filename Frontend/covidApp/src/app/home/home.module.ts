import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { TableComponent } from './table/table.component';
import { GlobeThreejsComponent } from './globe-threejs/globe-threejs.component';

@NgModule({
  declarations: [TableComponent, GlobeThreejsComponent],
  imports: [
    CommonModule
  ]
})
export class HomeModule { }
