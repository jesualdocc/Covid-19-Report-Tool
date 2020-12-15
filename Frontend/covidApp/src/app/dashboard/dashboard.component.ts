import { DoughnutGraph } from './Charts/DoughnutGraph';
import { PieGraph } from './Charts/PieGraph';
import { LineGraph } from './Charts/LineGraph';
import {BarGraph} from './Charts/BarGraph';
import { Component, OnInit } from '@angular/core';
import{Chart} from 'chart.js';
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  lineGraph:Chart;
  pieGraph:Chart;
  doughnutGraph:Chart;
  bargraph:Chart;

  constructor(private dataService:DataService) {
    this.dataService.changePageTitle("Dashboard");
   }

  ngOnInit(): void {
    const chart1 = new LineGraph('chart1', [[1, 2, 3, 4, 5, 6, 7], [67, 38, 839, 4664, 988, 674, 123]]);
    this.lineGraph = chart1.getChart();


    const chart2 = new PieGraph('chart2', [100, 25]);
    this.pieGraph = chart2.getChart();

    const chart3 = new BarGraph('chart3', [[100, 200, 388, 4, 5, 6, 788], [67, 38, 839, 4664, 988, 674, 123]]);
    this.lineGraph = chart3.getChart();

    const chart4 = new DoughnutGraph('chart4', [100, 25]);
    this.doughnutGraph = chart4.getChart();


  }


}
