import { LineGraph2 } from './Charts/LineGraph2';
import { LoginService } from 'src/app/login/login.service';
import { PieGraph } from './Charts/PieGraph';
import { LineGraph } from './Charts/LineGraph';
import { BarGraph } from './Charts/BarGraph';
import { Component, OnInit } from '@angular/core';
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent implements OnInit {
  constructor(
    private dataService: DataService,
    private loginService: LoginService
  ) {
    this.dataService.changePageTitle('Dashboard');
  }

  ngOnInit(): void {
    const user = this.loginService.user;
    user['days'] = 14;
    this.dataService.getCovidData(user).subscribe(
      (result) => {
        //[[cases (sun to sat)], [deaths(sund to sat)]]
        var data = result['body'].data;

        var cases = this.formatData(data, 'cases');
        var deaths = this.formatData(data, 'deaths');

        const chart1 = new LineGraph('chart1', cases);

        const chart4 = new LineGraph2('chart2', deaths);

        const chart3 = new BarGraph('chart3', [cases, deaths]);

        var casesConfirmed = this.formatData(data, 'cases', 1);
        var deathsConfirmed = this.formatData(data, 'deaths', 1);

        const chart2 = new PieGraph('chart4', [casesConfirmed, deathsConfirmed]);
      },
      (err) => {}
    );
  }

  //Data for Dashboard
  formatData(data: any, field: string, days: number = 14) {
    var arrData = [];
    var tmpArr = [];
    var i = 0;

    var sortedData = this.sortDataByDate(data);

    //Get key(dates) and values({cases, deaths...} )
    Object.keys(sortedData).forEach(function (key) {

      var values = data[key];

      tmpArr.push(values[field]);

      if (i == 13 && days != 1) {

        var weekday = new Date(key).getDay();
        //Get previous week's record
        var endIndex = i - weekday;
        var startIndex = endIndex - 7;

        for (let j = startIndex; j < endIndex; j++) {
          arrData.push(tmpArr[j]);

        }
      }

      i++;
    });

    if (days == 1) {
      var lastIndex = tmpArr.length - 1;
      var value = tmpArr[lastIndex];
      return value;
    }

    //Seven days
    return arrData;
  }

  //Sorts JSON by key(date) ==> {"date1":{}, "date2":{}, "date3":{}, ...}
  sortDataByDate(data: any) {
    var sorted = {};
    var key;
    var arr = [];

    for (key in data) {
      if (data.hasOwnProperty(key)) {
        arr.push(key);
      }
    }

    arr.sort(function (a, b) {
      var date1: any = new Date(a);
      var date2: any = new Date(b);
      return date1 - date2;
    });

    for (key = 0; key < arr.length; key++) {
      sorted[arr[key]] = data[arr[key]];
    }

    return sorted;
  }
}
