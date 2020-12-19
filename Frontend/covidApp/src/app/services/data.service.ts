import { LoginService } from 'src/app/login/login.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BehaviorSubject } from 'rxjs';
import { Users } from '../registration/Users';
import { ICovidData } from '../reports/CovidData';
import { baseUrl, baseTestingUrl } from './../../environments/environment';

@Injectable({
  providedIn: 'root'
})

//Service to share data between unrelated components
export class DataService {

mainRoute:string;
private sidebar = new BehaviorSubject(false);
currentSidebarStatus = this.sidebar.asObservable();

private pageTitle = new BehaviorSubject("");
currentPageTitle = this.pageTitle.asObservable();

  constructor(private http:HttpClient, private loginService:LoginService) {
    this.mainRoute = baseUrl;
  }

  showSideBar(status:boolean){
    this.sidebar.next(status);
  }

  changePageTitle(title:string){

    this.pageTitle.next(title);
  }

  getCounties():Observable<any>{

    var url = this.mainRoute + '/counties';
    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({'Content-Type': 'application/json'})
    }

    return this.http.get(url, httpOptions);
  }

  getAllUsers():Observable<any>{

    var url = this.mainRoute + '/listof';

    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({'Content-Type': 'application/json'})
    }

    return this.http.get<any>(url, httpOptions);
  }



  addUser(data:Users):Observable<any>{
    var url = this.mainRoute + '/registration';
    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({'Content-Type': 'application/json'})
    }

    return this.http.post<any>(url, data, httpOptions);
  }


  updateUser(data:Users):Observable<any>{
    var url = this.mainRoute + '/updadeinfo';

    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    }

    return this.http.put<any>(url, data, httpOptions);
  }

  getCovidData(data:Users):Observable<any>{
    var url = this.mainRoute + '/data';
    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'token': this.loginService.getToken()
      })
    }
    return this.http.post<any>(url, data, httpOptions);
  }

}
