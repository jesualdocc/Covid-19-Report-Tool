import { Component, OnInit } from '@angular/core';
import{Chart} from 'chart.js'
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  constructor(private dataService:DataService) {
    this.dataService.changePageTitle("Dashboard");
   }

  ngOnInit(): void {

  }


}
