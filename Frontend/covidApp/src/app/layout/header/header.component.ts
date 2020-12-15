import { DataService } from './../../services/data.service';
import { Component, EventEmitter, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { LoginService } from 'src/app/login/login.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit{

  public sidebarStatus:boolean = false;
  public pageTitle:string;
  public homePage:boolean;
  isLoggedin:boolean;

  constructor(private router: Router, private dataService:DataService,
    private loginService:LoginService) {
  }

  sidebarDisplay():void{
    this.sidebarStatus = !this.sidebarStatus;
    this.dataService.showSideBar(this.sidebarStatus);
  }

  ngOnInit(): void {

    this.dataService.currentPageTitle.subscribe(t=> this.pageTitle = t);
    this.isLoggedin = this.loginService.isLoggedIn;
    this.homePage = this.pageTitle == "Covid Report" ? true : false;

  }

  login():void{
    this.router.navigate(['/login']);
  }

  logout():void{
    this.isLoggedin = false;
    this.homePage = true;
    this.loginService.logout();

  }

}
