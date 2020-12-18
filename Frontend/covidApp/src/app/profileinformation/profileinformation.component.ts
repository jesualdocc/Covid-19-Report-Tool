import { LoginService } from 'src/app/login/login.service';
import { DataService } from 'src/app/services/data.service';
import { Component, OnInit } from '@angular/core';
import { Users } from 'src/app/registration/Users';
import { Router } from '@angular/router';
import { usStates } from '../services/States';


@Component({
  selector: 'app-profileinformation',
  templateUrl: './profileinformation.component.html',
  styleUrls: ['./profileinformation.component.css']
})
export class ProfileinformationComponent implements OnInit {

  states = usStates;
  counties = ["County1", "County 2"];
  model = new Users();
  submitted = false;
  submissionMessage = '';
  errorMessage = false;

  constructor(private dataService:DataService, private router:Router, private loginService:LoginService) { }

  ngOnInit(): void {
    this.getUser();

  }

  getUser(){
      var data = this.loginService.user;

      this.model.id = data['id'];
      this.model.firstName = data['firstName'];
      this.model.lastName = data['lastName'];
      this.model.userName = data['userName'];
      this.model.email = data['email'];
      this.model.password = data['password'];
      this.model.county = data['county'];
      this.model.state = data['state'];
  }

  onSubmit(){

    //this.sendData();


  }

  sendData(){
    this.dataService.updateUser(this.model).subscribe(result=>{
      if(result['ok'] == 1){
        this.errorMessage = false;
        this.submitted = true;
        this.submissionMessage = '';
        alert("User Updated");

        this.router.navigate(['/dashboard']);
      }
      else{
        this.errorMessage = true;
        this.submissionMessage = "An error occurred!Try Again...";

      }
   });
  }

}

