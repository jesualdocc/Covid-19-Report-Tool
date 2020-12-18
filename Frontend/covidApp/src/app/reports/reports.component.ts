import { DataService } from './../services/data.service';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.css']
})
export class ReportsComponent implements OnInit {
  title:string = "Reports";

  constructor(private dataService:DataService) {
    this.dataService.changePageTitle(this.title);
  }

  ngOnInit(): void {
  }

}
