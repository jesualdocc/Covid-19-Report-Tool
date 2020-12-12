import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

//Service to share data between unrelated components
export class DataService {
private sidebar = new BehaviorSubject(false);
currentSidebarStatus = this.sidebar.asObservable();

private pageTitle = new BehaviorSubject("Dashboard");
currentPageTitle = this.pageTitle.asObservable();

  constructor() { }

  showSideBar(status:boolean){
    this.sidebar.next(status);
  }

  changePageTitle(title:string){
    this.pageTitle.next(title);
  }
}
