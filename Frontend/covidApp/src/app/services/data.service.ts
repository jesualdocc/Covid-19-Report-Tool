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

location:any; //To share county and state for non-logged user
mainRoute:string;
private sidebar = new BehaviorSubject(false);
currentSidebarStatus = this.sidebar.asObservable();

private isGlobeView = new BehaviorSubject(false);
currentView = this.isGlobeView.asObservable();

private pageTitle = new BehaviorSubject("");
currentPageTitle = this.pageTitle.asObservable();

  constructor(private http:HttpClient, private loginService:LoginService) {
    this.mainRoute = baseUrl;
  }

  showSideBar(status:boolean){
    this.sidebar.next(status);
  }

  changeView(status:boolean){
    this.isGlobeView.next(status);
  }

  changePageTitle(title:string){

    this.pageTitle.next(title);
  }

  getTweets():Observable<any>{

    var url = this.mainRoute + '/twitter';
    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({
        'token': this.loginService.getToken()
      })
    }

    var user = this.loginService.user;

    return this.http.post<any>(url, user, httpOptions)
  }

  getCounties(state:any):Observable<any>{

    var url = this.mainRoute + '/counties';
    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({
        'Content-Type':'application/json'
      })
    }

    return this.http.post(url,state, httpOptions);
  }

  getAllUsers():Observable<any>{

    var url = this.mainRoute + '/listof';

    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({
        'Content-Type':'application/json'
      })
    }

    return this.http.get<any>(url, httpOptions);
  }



  addUser(data:Users):Observable<any>{
    var url = this.mainRoute + '/registration';
    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({
        'Content-Type':'application/json'
      })
    }

    return this.http.post<any>(url, data, httpOptions);
  }


  updateUser(data:Users, changeType:string):Observable<any>{
    var url = this.mainRoute + '/profileinfo';

    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({
        'changeType':changeType,
        'token': this.loginService.getToken()
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
        'Content-Type':'application/json',
        'token': this.loginService.getToken()
      })
    }
    return this.http.post<any>(url, data, httpOptions);
  }

  getPredictions():Observable<any>{
    var url = this.mainRoute + '/predictions';

    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({
        'token': this.loginService.getToken()
      })
    }

    var user = this.loginService.user;

    return this.http.post<any>(url, user, httpOptions)
  }

  getGlobeData():Observable<any>{
    var url = this.mainRoute + '/globedata';

    var httpOptions = {
      observe : 'response' as const,
      responseType:'json' as const,
      headers: new HttpHeaders({
        'token': this.loginService.getToken()
      })
    }

    return this.http.get<any>(url,httpOptions)
  }

}
