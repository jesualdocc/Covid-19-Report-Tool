import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { LoginService } from '../login/login.service';
import { Users } from '../registration/Users';
import { DataService } from '../services/data.service';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css']
})
export class SettingsComponent implements OnInit {
  title:string ="Account Settings";
  model = new Users();
  submitted = false;
  submissionMessage = '';
  checkCurrentP:string; //current password
  checkMatch:string = "";
  errorMessage: boolean = false;

  //Property that get checks in realtime
  get passwordMatch():boolean{

    return this.model.password == this.checkMatch ? true:false;

  }

  constructor(private dataService:DataService, private loginService:LoginService, private router:Router) {
    this.dataService.changePageTitle(this.title);
   }

  ngOnInit(): void {
    this.getUser();
  }



  onSubmit(){
    this.sendData();

  }

  cancel(){
    this.router.navigate(['/dashboard']);
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

sendData(){
 //For password change only
  this.dataService.updateUser(this.model, 'password').subscribe(result=>{
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

}
