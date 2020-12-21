import { LineGraph2 } from './Charts/LineGraph2';
import { LoginService } from 'src/app/login/login.service';
import { PieGraph } from './Charts/PieGraph';
import { LineGraph } from './Charts/LineGraph';
import {BarGraph} from './Charts/BarGraph';
import { Component, OnInit } from '@angular/core';
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  constructor(private dataService:DataService, private loginService:LoginService) {
    this.dataService.changePageTitle("Dashboard");
   }

  ngOnInit(): void {

    const user = this.loginService.user;
    user['days'] = 7;
    this.dataService.getCovidData(user).subscribe(result=>{
       //[[cases (sun to sat)], [deaths(sund to sat)]]
      var data = result['body'].data;

      var cases = this.formatData(data, 'cases', 7);
      var deaths = this.formatData(data,'deaths', 7);

      const chart1 = new LineGraph('chart1', cases);

      const chart4 = new LineGraph2('chart2', deaths);

      const chart3 = new BarGraph('chart3', [cases, deaths]);

      var casesConfirmed = this.formatData(data, 'confirmed_cases', 1);
      var deathsConfirmed = this.formatData(data,'confirmed_deaths', 1);

      const chart2 = new PieGraph('chart4', [casesConfirmed, deathsConfirmed]);

    },
    err=>{


    });
  }

  //Data for Dashboard
  formatData(data:any, field:string, days:number){
    var arrData = [];
     //Get key(dates) and values({cases, deaths...} )
     Object.keys(data).forEach(function(key) {
      var values = data[key];

      var weekday = new Date(key).getDay();

      //Sunday=0 to Saturday=6
      arrData[weekday] = values[field];

  });

  if (days == 1){

    var weekday = new Date().getDay(); //Today
    var value = arrData[weekday];

    //Today's data not available yet
    if( value == undefined || value == null )
    {
      //Sunday = 0  go to sat = 6
      if(weekday == 0){
        weekday = 6;
      }
      else{
        weekday--;
      }
      value = arrData[weekday];//day before
    }

    return value;
  }

  //Seven days
  return arrData;

  }

}
