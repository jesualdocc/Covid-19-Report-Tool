import { Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ICovidData } from 'src/app/reports/CovidData';
import { DataService } from 'src/app/services/data.service';

@Component({
  selector: 'app-table',
  templateUrl: './table.component.html',
  styleUrls: ['./table.component.css']
})
export class TableComponent implements OnInit {

  displayedColumns: string[] = ['date','cases', 'deaths'];
  dataSource:MatTableDataSource<ICovidData>;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort:MatSort;
  location:any;
  get tableName():string{

    let name = '';
    if (this.location['state'] != undefined){
      console.log('Here 1')
      if (this.location['county'] != undefined){
        name = this.location['country'] + ', ' + this.location['state'] + ', ' + this.location['county']

      }
      else{

        name = this.location['country'] + ', ' + this.location['state']

      }

      return name;
    }

    name = this.location['country'];
    return name;
  }

  constructor(private dataService:DataService) {

    this.requestData();
   }

  ngOnInit(): void {

  }

  async requestData(){

    this.location = this.dataService.location;
      var data =  await this.dataService.getCovidData(this.location).toPromise().then(res=> {
        var data = res['body'].data;
        return data;
      });

    var tableData = this.formatData(data);

    this.dataSource = new MatTableDataSource<ICovidData>(tableData);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }


  formatData(data:any){

    var arrData:ICovidData[] =[];
     //Get key(dates) and values({cases, deaths...} )
     Object.keys(data).forEach(function(key) {

      var arr:ICovidData = {cases: 0, date: "", deaths: 0};

      var values = data[key];
      values['date'] = key;

      arr.cases = values['cases'];
      arr.deaths = values['deaths'];

      arr.date = values['date'];

      arrData.push(arr);

  });

  //Descending based on date
    arrData.sort((a, b) => {
      var x = new Date(a.date);
      var y = new Date(b.date);

      if(x > y){
        return -1;
      }

      if (x < y){
        return 1;
      }

      return 0;
    });

   return arrData;
  }

}
