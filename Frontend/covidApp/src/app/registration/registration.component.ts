
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import {Users} from './Users';
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.css']
})
export class RegistrationComponent implements OnInit {

  countries:Set<string> =  new Set<string>();
  states = [];
  counties = [];
  model = new Users();
  submitted = false;
  submissionMessage = '';
  usernameList:string[] = [];
  errorMessage = false;
  checkMatch:string = "";
  loading:boolean = false;
  stateListEnable = false;
  countyListEnable = false;

  //Property that get checks in realtime
  get passwordMatch():boolean{

    return this.model.password == this.checkMatch ? true:false;

  }

  //Assures that county and states are selected (used along with form.valid)
  get isSelected():boolean{
    if(this.model.country == null || this.model.country == undefined || this.model.country == ""){
      return false;
    }

    return true;
  }

  //Property that get checks in realtime
  get checkUsername():string {
    const uName = this.model.userName;

    if(this.usernameList.includes(uName)){
      const ret = 'Username:' + uName + ' is not available';
      return ret;
    }

    return '';
   }

   constructor(private router: Router, private dataService:DataService) { }


  ngOnInit(): void {
    this.getCountries();

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
      this.getAllUsernames();
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

    this.sendData();

  }

  clearForm(){
    this.model = new Users();
  }

  cancel(){
    this.router.navigate(['/home']);
  }


  getAllUsernames(){
    this.loading = true;
    this.dataService.getAllUsers().subscribe(
      data=>{

        if(data.status == 200){
          var result = data['body'].users;

          var usernames = result['userName'];

            for(var i in usernames){

            this.usernameList.push(usernames[i]);
            }
        }
      }, err=>{

      },
      ()=>{
        this.loading = false;

      });
  }

  sendData(){

    this.dataService.addUser(this.model).subscribe(result=>{
    if(result.status == 201){
      this.errorMessage = false;
      this.submitted = true;
      this.submissionMessage = '';
      alert("Registration Successful");
      this.router.navigate(['/login']);
    }
    else{

      this.submissionMessage = "An error occurred!Try Again...";

    }
    });
  }

}
