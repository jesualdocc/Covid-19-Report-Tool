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
  model = new Users();
  submitted = false;
  submissionMessage = '';
  emailList:string[] = [];
  usernameList:string[] = [];
  errorMessage = false;

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
    //this.getAll();
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
     var result = new Array(data);
      for(var values of result){
        this.emailList.push(values['email']);
        this.usernameList.push(values['userName']);
      }

    });}

  sendData(){
    this.dataService.addUser(this.model).subscribe(result=>{
    if(result['ok'] == 1){
      this.errorMessage = false;
      this.submitted = true;
      this.submissionMessage = '';
      alert("Registration Successful");
      //this.dialogRef.close();
      this.router.navigate(['/login']);
    }
    else{

      this.errorMessage = true;
      if(this.emailList.includes(this.model.email)){
        this.submissionMessage = "Email is already Registered";
      }
      else{
        this.submissionMessage = "An error occurred!Try Again..."
      }

    }
    });
  }

}
