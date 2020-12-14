import { ILogin} from './login';
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders  } from '@angular/common/http';
import { baseUrl, baseTestingUrl } from './../../environments/environment';
import { Observable } from 'rxjs';
import { LocalStorageService } from 'ngx-webstorage';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class LoginService {
token:string;
isLoggedIn:boolean;

  constructor(private http:HttpClient, private localStorage:LocalStorageService, private router:Router) {
  }

  loginHandler(data:ILogin):Observable<ILogin>{
    var requestToken = 'no';

    if(this.token == null || this.token == "" || this.token == undefined){
      requestToken = 'yes';
    }

    var httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'tokenNeeded': requestToken
      }),
    }
    return this.http.post<ILogin>( baseTestingUrl+'/login', data, httpOptions);
  }

  isTokenExpired():boolean{
    return false;
  }

  getToken():string{

    if(this.isTokenExpired()){

      this.deleteTokenData();
      this.logout();

      return "";
    }

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

  deleteTokenData(){
    this.localStorage.clear('token');
    this.localStorage.clear('tokenExpiration');
  }




}
