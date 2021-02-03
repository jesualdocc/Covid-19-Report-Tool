import { LoginService } from 'src/app/login/login.service';
import { DataService } from 'src/app/services/data.service';
import { Component, OnInit } from '@angular/core';
import { Users } from 'src/app/registration/Users';
import { Router } from '@angular/router';

@Component({
  selector: 'app-profileinformation',
  templateUrl: './profileinformation.component.html',
  styleUrls: ['./profileinformation.component.css']
})
export class ProfileinformationComponent implements OnInit {

  countries:Set<string> =  new Set<string>();
  states = [];
  counties = [];
  model = new Users();
  submitted = false;
  submissionMessage = '';
  errorMessage = false;
  loading:boolean = false;
  stateListEnable = false;
  countyListEnable = false;

  constructor(private dataService:DataService, private router:Router, private loginService:LoginService) { }

  ngOnInit(): void {
    this.getUser();
    this.getCountries();
    //this.getStateProvinces(this.model.state, 0);
    //this.getStateCounties(this.model.county, 0);

  }

  getUser(){
      var data = this.loginService.user;

      this.model.id = data['id'];
      this.model.firstName = data['firstName'];
      this.model.lastName = data['lastName'];
      this.model.userName = data['userName'];
      this.model.country = data['country'];
      this.model.state = data['state'];
      this.model.county = data['county'];
  }

  onSubmit(){

    this.sendData();


  }

  cancel(){
    this.router.navigate(['/dashboard']);
  }

  sendData(){

    this.dataService.updateUser(this.model, 'profile').subscribe(result=>{
      if(result.status == 201){
        this.errorMessage = false;
        this.submitted = true;
        this.submissionMessage = '';

        this.loginService.logout();
        alert("User Info Updated")
      }

   },
   err=>{
        this.errorMessage = true;
        this.submissionMessage = "An error occurred!Try Again...";
   }
   );
  }

  getCountries(){
    this.loading = true;
    this.dataService.getCountries().subscribe(data=>{
      if(data.status == 200){
        let result = data['body'].data;

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

  getStateProvinces(country:string, change:number){
    this.loading = true;
    if(change){
      this.states = [];
      this.stateListEnable = false;
      this.countyListEnable = false;
    }

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

  getStateCounties(state:string, change:number){
    this.loading = true;

    if(change){
      this.counties = [];
      this.countyListEnable = false;
    }

    this.dataService.getCounties({'state':state}).subscribe(data=>{
      if(data.status == 200){

        this.counties = data['body'].data
        this.counties.sort()

      }
      this.countyListEnable = true;
      this.loading = false;

    });
  }



}

