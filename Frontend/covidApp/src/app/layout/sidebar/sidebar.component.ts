import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {

  optionsList = [["dashboard"," Dashboard"],["analytics"," Reports"],["people"," Twitter Feed"], ["settings","Settings"]];


  constructor() { }

  ngOnInit(): void {
  }

}
