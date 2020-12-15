import { SettingsComponent } from './settings.component';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule } from '@angular/router';
import {MatTabsModule} from '@angular/material/tabs';

const routes: Routes = [
  { path: '', component: SettingsComponent }
];

@NgModule({
  declarations: [SettingsComponent],
  imports: [
    CommonModule,
    MatTabsModule,
    RouterModule.forChild(routes)
  ],
  exports: [RouterModule]
})
export class SettingsModule { }
