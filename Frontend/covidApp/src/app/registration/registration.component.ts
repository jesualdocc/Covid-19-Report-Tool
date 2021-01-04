import { usStates } from './../services/States';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialogRef } from '@angular/material/dialog';
import {Users} from './Users';
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.css']
})
export class RegistrationComponent implements OnInit {

  states = usStates;
  counties = [];
  model = new Users();
  submitted = false;
  submissionMessage = '';
  emailList:string[] = [];
  usernameList:string[] = [];
  errorMessage = false;
  checkMatch:string = "";
  loading:boolean = false;
  countyListEnable = false;

  //Property that get checks in realtime
  get passwordMatch():boolean{

    return this.model.password == this.checkMatch ? true:false;

  }

  //Assures that county and states are selected (used along with form.valid)
  get areSelected():boolean{
    if(this.model.county == null || this.model.county == undefined || this.model.county == ""){
      return false;
    }
    if(this.model.county == null || this.model.county == undefined || this.model.county == ""){
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
    this.getAll();

  }

  getStateCounties(state:string){
    this.loading = true;
    this.counties = [];
    this.dataService.getCounties({'state':state}).subscribe(data=>{
      if(data.status == 200){

        var result = data['body'].data
        for(var i of result){
          this.counties.push(i)
        }

        this.counties.sort()
        this.loading = false;
        this.countyListEnable = true;
      }

    })
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


  getAll(){

    this.dataService.getAllUsers().toPromise().then(
      data=>{

        if(data.status == 200){
          var result = data['body'].users;

          var emails = result['email'];

          var usernames = result['userName'];

            for(var i in emails){

            this.emailList.push(emails[i]);
            this.usernameList.push(usernames[i]);
            }
        }
      }
    ).catch(err=>
      {
      console.log(err)
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
