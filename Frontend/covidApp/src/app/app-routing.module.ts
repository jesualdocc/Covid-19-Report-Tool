
import { CovidtableComponent } from './reports/covidtable/covidtable.component';
import { RouteguardService as RouteGuard} from './services/routeguard.service';
import { RegistrationComponent } from './registration/registration.component';
import { LoginComponent } from './login/login.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { TestComponent } from './test/test.component';

const routes: Routes = [
{
  path: '',
  redirectTo: '/home',
  pathMatch: 'full'
},
{
  path:'login',
  component:LoginComponent,
  data: { showHeader:false, showSidebar:false}
},
{
  path:'teste',
  component:TestComponent,
  data: { showHeader:false, showSidebar:false}
},
{
  path:'home',
  loadChildren:() => import('./home/home.module').then(m=> m.HomeModule),
  data: { showHeader:true, showSidebar:false}
},
{
  path:'dashboard',
  loadChildren:() => import('./dashboard/dashboard.module').then(m=> m.DashboardModule),
  data: { showHeader:true, showSidebar:true},
  canActivate:[RouteGuard]
},
{
  path:'reports',
  loadChildren:() => import('./reports/reports.module').then(m=> m.ReportsModule),
  data: { showHeader:true, showSidebar:true},
  canActivate:[RouteGuard]
},
{
  path:'settings',
  loadChildren:() => import('./settings/settings.module').then(m=> m.SettingsModule),
  data: { showHeader:true, showSidebar:true},
  canActivate:[RouteGuard]
},
{
  path:'registration',
  component:RegistrationComponent,
  data: { showHeader:false, showSidebar:false}
}

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
