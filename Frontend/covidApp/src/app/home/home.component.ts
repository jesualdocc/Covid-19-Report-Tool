import { Users } from 'src/app/registration/Users';
import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { DataService } from '../services/data.service';
import { usStates } from '../services/States';
import { ICovidData } from '../reports/CovidData';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})

export class HomeComponent implements OnInit {
  title:string = "Covid Reporting Tool";
  model = new Users();
  states = usStates;
  counties = [];
  submitted = false;
  submissionMessage = '';
  errorMessage = false;
  loading:boolean = false;
  countyListEnable = false;


  constructor(private dataService:DataService, private router:Router) {
    this.dataService.changePageTitle(this.title);

  }

  ngOnInit(): void {

  }

  getStateCounties(state:string){

    this.loading = true;
    this.counties = []

    this.dataService.getCounties({'state':state}).subscribe(data=>{
      if(data.status == 200){

        var result = data['body'].data;
        for(var i of result){
          this.counties.push(i)
        }

        this.counties.sort()
        this.loading = false;
        this.countyListEnable = true;
      }

    },
    err=>{
      this.submissionMessage = "An error occured... Try again ";
    })
  }

  onSubmit(){
    this.model.days = 30;
    this.dataService.location = this.model;
    this.loading = false;
    this.submitted = true;
  }

  newReport(){
    this.model = new Users();
    this.countyListEnable = false;
    this.submitted = false;

  }


}

