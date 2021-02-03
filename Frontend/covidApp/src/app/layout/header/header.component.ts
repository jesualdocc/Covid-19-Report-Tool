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

  sidebarStatus:boolean = false;
  pageTitle:string;
  showMenu:boolean = false;;
  isLoggedin:boolean;
  userInfo:string;

  get showLogin():boolean{

    if (this.pageTitle == 'Globe'){
      return false;
    }
   return true;
  }

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
      //Check if it's homepage to hide/show sidemenu
      this.showMenu = true;
      let state = user['state'] != null ? user['state'] : '';
      let county = user['county'] != null ? user['county'] : '';
      this.userInfo = '(' + county + ', ' + state + ', ' + user['country'] + ')    ';
    }
  }

  login():void{
    this.router.navigate(['/login']);
  }

  logout():void{
    this.isLoggedin = false;
    this.showMenu = false;
    this.loginService.logout();

  }

}
