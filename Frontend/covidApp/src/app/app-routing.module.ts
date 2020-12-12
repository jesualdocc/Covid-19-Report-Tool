import { LoginComponent } from './login/login.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

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
  path:'home',
  loadChildren:() => import('./home/home.module').then(m=> m.HomeModule),
  data: { showHeader:true, showSidebar:false}
},
{
  path:'dashboard',
  loadChildren:() => import('./dashboard/dashboard.module').then(m=> m.DashboardModule),
  data: { showHeader:true, showSidebar:true}
},
// {
//   path:'login',
//   loadChildren:() => import('./login/login.module').then(m=> m.LoginModule),
//   data: { showHeader:false, showSidebar:false}
// },
{
  path:'registration',
  loadChildren:() => import('./registration/registration.module').then(m=> m.RegistrationModule),
  data: { showHeader:false, showSidebar:false}
}

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
