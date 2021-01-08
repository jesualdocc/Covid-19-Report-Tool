import { Users } from 'src/app/registration/Users';
import { DataService } from './../../services/data.service';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
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
  userInfo:string;

  constructor(private router: Router, private dataService:DataService,
    private loginService:LoginService) {
  }

  //Function to toggle sidemenu
  sidebarDisplay():void{
    this.sidebarStatus = !this.sidebarStatus;
    this.dataService.showSideBar(this.sidebarStatus);
  }

  ngOnInit(): void {

    //Subscribe to service that keeps tracks of each page title (updates main title variable)
    this.dataService.currentPageTitle.subscribe(t=> this.pageTitle = t);

    //Checks if user is logged (display different icons for login/out)
    this.isLoggedin = this.loginService.isLoggedIn;

    if(this.isLoggedin){
      var user = this.loginService.user;

      this.userInfo = '(' + user['county'] + ', ' + user['state'] + ')    ';
    }


    //Check if it's homepage to hide/show sidemenu (doesnt show on homepage)
    this.homePage = this.pageTitle == "Covid Reporting Tool" ? true : false;

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
