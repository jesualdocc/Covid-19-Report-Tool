import { LoginService } from 'src/app/login/login.service';
import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table/';
import { DataService } from 'src/app/services/data.service';
import {ICovidData} from '../CovidData';

@Component({
  selector: 'app-covidtable',
  templateUrl: './covidtable.component.html',
  styleUrls: ['./covidtable.component.css']
})
export class CovidtableComponent implements AfterViewInit {


  displayedColumns: string[] = ['date','cases', 'deaths'];
  dataSource:MatTableDataSource<ICovidData>;
  response:any;
  loading:boolean = false;

  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort:MatSort;

  public selectedName:any;

  constructor( private dataService:DataService, private loginService:LoginService){

    this.requestData(60);

  }


  ngAfterViewInit() {

  }

  public highlightRow(model:any) {
    this.selectedName = model.date;
  }

  //Function to filter data
  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  async requestData(days:number){
    this.loading = true;
    var user = this.loginService.user;
    user['days'] = days;

      var data =  await this.dataService.getCovidData(user).toPromise().then(res=> {
        var data = res['body'].data;
        return data;
      });

    var tableData = this.formatData(data);

    this.dataSource = new MatTableDataSource<ICovidData>(tableData);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
    this.loading = false;
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



