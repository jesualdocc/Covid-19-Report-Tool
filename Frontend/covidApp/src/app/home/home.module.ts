import { HomeComponent } from './home.component';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatSidenavModule } from '@angular/material/sidenav';



@NgModule({
  declarations: [HomeComponent],
  imports: [
    CommonModule,
    MatSidenavModule
  ]
})
export class HomeModule { }
