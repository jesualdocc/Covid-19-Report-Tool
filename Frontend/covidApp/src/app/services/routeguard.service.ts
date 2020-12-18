import { LoginService } from 'src/app/login/login.service';
import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RouteguardService implements CanActivate {

  constructor(private loginService:LoginService, private router:Router) { }

  canActivate():boolean {

    if(!this.loginService.isAuthenticated()){
      this.router.navigate(['/login']);
      return false;
    }

    return true;
  }
}
