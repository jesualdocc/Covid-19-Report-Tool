import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table/';
import { DataService } from 'src/app/services/data.service';
import {ICovidData} from '../CovidData';

const cData:ICovidData[] = [
  {date:Date.now(), cases:123, deaths:565, confirmedCases:785, confirmedDeaths:984, probableCases:53, probableDeaths:535, str:"Hello"},
  {date:Date.now(), cases:134, deaths:85, confirmedCases:785, confirmedDeaths:984, probableCases:53, probableDeaths:535, str:"Teste"},
  {date:Date.now(), cases:223, deaths:745, confirmedCases:785, confirmedDeaths:984, probableCases:53, probableDeaths:535, str:"Another"}
];

@Component({
  selector: 'app-covidtable',
  templateUrl: './covidtable.component.html',
  styleUrls: ['./covidtable.component.css']
})
export class CovidtableComponent implements AfterViewInit {


  displayedColumns: string[] = ['date','cases', 'deaths', 'confirmedCases', 'confirmedDeaths', 'probableCases', 'probableDeaths'];
  dataSource:MatTableDataSource<ICovidData>;

  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort:MatSort;

  public selectedName:any;

  constructor(){
    this.dataSource = new MatTableDataSource<ICovidData>(cData);
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
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
}



