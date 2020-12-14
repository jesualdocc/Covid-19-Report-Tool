import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BehaviorSubject } from 'rxjs';
import { Users } from '../registration/Users';
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

  constructor(private http:HttpClient) {
    this.mainRoute = baseTestingUrl;
  }

  showSideBar(status:boolean){
    this.sidebar.next(status);
  }

  changePageTitle(title:string){

    this.pageTitle.next(title);
  }

  getCounties():Observable<any>{

    var url = this.mainRoute + '/getcounties';

    return this.http.get(url, {responseType: 'json'});
  }

  getAllUsers():Observable<Users>{

    var url = this.mainRoute + '/getall';

    return this.http.get<Users>(url, {responseType: 'json'});
  }
  updateUser(id:string, data:Users):Observable<Users>{
    var url = this.mainRoute + '/updade/' + id;

    return this.http.put<Users>(url, data, {responseType: 'json'});
  }

  addUser(data:Users):Observable<Users>{
    var url = this.mainRoute + '/newuser';

    return this.http.post<Users>(url, data);
  }

}
