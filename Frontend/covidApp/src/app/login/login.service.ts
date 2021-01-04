import { DataService } from './../services/data.service';
import { ILogin} from './login';
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders  } from '@angular/common/http';
import { baseUrl, baseTestingUrl } from './../../environments/environment';
import { Observable } from 'rxjs';
import { LocalStorageService } from 'ngx-webstorage';
import { Router } from '@angular/router';
import { Users } from '../registration/Users';

@Injectable({
  providedIn: 'root'
})
export class LoginService {
token:string;
isLoggedIn:boolean;
headers:HttpHeaders;
user:any;

  constructor(private http:HttpClient, private localStorage:LocalStorageService,
     private router:Router) {
  }

  loginHandler(data:any):Observable<any>{

    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const
    }
    return this.http.post<any>(baseUrl +'/login', data, httpOptions);
  }

  getToken():string{

    this.token = this.localStorage.retrieve('token');

    if(this.token == null || this.token == "" || this.token == undefined){
      this.logout();
      return "";
    }

    return this.token;
  }

  logout(){
    this.isLoggedIn = false;
    this.router.navigate(['/home']);
  }

  isAuthenticated():boolean{
    return this.isLoggedIn;
  }

  deleteTokenData(){
    this.localStorage.clear('token');

  }




}
