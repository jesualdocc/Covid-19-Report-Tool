
import { CovidtableComponent } from './reports/covidtable/covidtable.component';
import { RouteguardService as RouteGuard} from './services/routeguard.service';
import { RegistrationComponent } from './registration/registration.component';
import { LoginComponent } from './login/login.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';


const routes: Routes = [
{
  path: '',
  pathMatch: 'full',
  component:HomeComponent,
  data: { showHeader:true, showSidebar:false}
},
{
  path:'home',
  redirectTo:''
},
{
  path:'login',
  component:LoginComponent,
  data: { showHeader:false, showSidebar:false}
},
{
  path:'globeview',
  loadChildren:() => import('./home/globe-threejs/globe-threejs.module').then(m=> m.GlobeThreejsModule),
  data: { showHeader:true, showSidebar:false, showFooter: false}
},
{
  path:'twitter',
  loadChildren:()=> import ('./twitter/twitter.module').then(m=>m.TwitterModule),
  data: { showHeader:true, showSidebar:true},
  canActivate:[RouteGuard]
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
