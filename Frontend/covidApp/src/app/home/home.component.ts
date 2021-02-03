import { Users } from 'src/app/registration/Users';
import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { DataService } from '../services/data.service';
import { usStates } from '../services/States';
import * as THREE from 'three';
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
  countries:Set<string> =  new Set<string>();
  states = [];
  counties = [];
  submitted = false;
  submissionMessage = '';
  errorMessage = false;
  loading:boolean = false;
  globeView = false;
  data:any = null;
  stateListEnable = false;
  countyListEnable = false;


  constructor(private dataService:DataService, private router:Router) {
    this.dataService.changePageTitle(this.title);

  }

  ngOnInit(): void {
    this.getCountries();
  }


  getCountries(){
    this.loading = true;
    this.dataService.getCountries().subscribe(data=>{
      if(data.status == 200){
        let result = data['body'].data;

        this.countries.add('World');
        this.countries.add('US');

        for(var c of result){
          this.countries.add(c[0]);
        }
      }
    },
    err=>{

    },
    ()=>{
      this.loading = false;
    }
    );
  }

  getStateProvinces(country:string){
    this.loading = true;
    this.states = [];
    this.stateListEnable = false;
    this.countyListEnable = false;

    this.dataService.getStates({'country':country}).subscribe(data=>{
      if(data.status == 200){
        this.states = data['body'].data;
        this.states.sort()
      }

    },err=>{},
    ()=>{
      this.stateListEnable = true;
      this.loading = false;
    });
  }

  getStateCounties(state:string){
    this.loading = true;
    this.counties = [];
    this.countyListEnable = false;

    this.dataService.getCounties({'state':state}).subscribe(data=>{
      if(data.status == 200){

        this.counties = data['body'].data
        this.counties.sort()

      }
      this.countyListEnable = true;
      this.loading = false;

    });
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

  switchToGlobe(){
    this.router.navigate(['globeview']);

  }

}
