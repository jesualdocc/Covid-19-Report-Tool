import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {

  selectedRoute:any;

  //['icon name', 'Page Title']
  optionsList = [["dashboard","Dashboard"],["analytics","Reports"],["people","Twitter Feed"], ["settings","Account Settings"]];


  constructor(private router: Router) { }

  ngOnInit(): void {
  }

  //Navigates to route based on selected value from mat-list and optionsList variable
  goTo(selection:any){
    var route;

    if(selection[1] == 'Dashboard'){
      route = '/dashboard';
    }
    if(selection[1] == 'Reports'){
      route = '/reports';
    }
    if(selection[1] == 'Twitter Feed'){
      route = '/twitter';
    }
    if(selection[1] == 'Account Settings'){
      route = '/settings';
    }

    this.router.navigate([route]);
  }
}
