import { ICovidData } from './../CovidData';
import { DataService } from 'src/app/services/data.service';
import { Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';

@Component({
  selector: 'app-covidpredictions',
  templateUrl: './covidpredictions.component.html',
  styleUrls: ['./covidpredictions.component.css']
})
export class CovidpredictionsComponent {

  displayedColumns: string[] = ['date','cases','deaths'];
  dataSource:MatTableDataSource<ICovidData>;
  loading:boolean =  false;

  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort:MatSort;

  public selectedName:any;

  constructor(private dataService:DataService) {
    this.requestData()
  }

  public highlightRow(model:any) {
    this.selectedName = model.date;
  }

  async requestData(){
    this.loading = true;

      var data =  await this.dataService.getPredictions().toPromise().then(res=> {
        var data = res['body'];
        return data;
      });

    var tableData = this.formatData(data);

    this.dataSource = new MatTableDataSource<ICovidData>(tableData);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
    this.loading = false;
  }

  formatData(data:any):ICovidData[]{
    var arrData:ICovidData[] = []


      var cases = data['cases'];
      var deaths = data['deaths'];
      var days = data['days'];




    for (let i = 0; i < days; i++){
      var arr:ICovidData = {cases: 0, date: "", deaths: 0};

      var nextDate = new Date();
      nextDate.setDate(nextDate.getDate() + 1 + i);

      arr.cases = cases[i];
      arr.deaths = deaths[i];
      arr.date = nextDate.toLocaleDateString();
      arrData.push(arr);
    }


    return arrData;
  }

}
