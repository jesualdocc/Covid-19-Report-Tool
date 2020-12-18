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
  counties:any;
  model = new Users();
  submitted = false;
  submissionMessage = '';
  emailList:string[] = [];
  usernameList:string[] = [];
  errorMessage = false;
  checkMatch:string = "";

  //Property that get checks in realtime
  get passwordMatch():boolean{

    return this.model.password == this.checkMatch ? true:false;

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
    this.dataService.getAllUsers().subscribe(data=>{
    var result = data['users']
    var emails = result['email']
    var usernames = result['userName']

      for(var i in emails){

      this.emailList.push(emails[i]);
      this.usernameList.push(usernames[i]);
      }

    });}

  sendData(){
    this.dataService.addUser(this.model).subscribe(result=>{
    if(result['ok'] == 1){
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
