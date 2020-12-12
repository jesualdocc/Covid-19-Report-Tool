import { DataService } from './../../services/data.service';
import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {

  @Output() toggleSidenav = new EventEmitter<void>();
  private returnUrl:string = '/';
  public sidebarStatus:boolean = false;
  public pageTitle:string;

  constructor(private router: Router, private dataService:DataService) {

  }

  sidebarDisplay():void{
    this.sidebarStatus = !this.sidebarStatus;
    this.dataService.showSideBar(this.sidebarStatus);
  }


  ngOnInit(): void {

    this.dataService.currentPageTitle.subscribe(t=> this.pageTitle = t);

  }

}
